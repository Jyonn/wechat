import datetime
from typing import List

from SmartDjango import E
from smartify import P

from Base.boc import bocfx
from Base.lines import Lines
from Base.phone import Phone
from Service.models import Service, Parameter, ServiceData, ParamDict


@E.register()
class BOCError:
    SERVICE_INACCESSIBLE = E('服务不可用')
    CURRENCY = E('货币名称错误，通过-s参数获取所有外币名称')
    SE_BN = E('短信提醒功能需要指定现汇或现钞（--se/--bn）')
    BID_ASK = E('短信提醒功能需要指定买入或卖出（--bid/--ask）')
    SMS = E('短信提醒功能需指定最大值或最小值（max/min）')
    STOP = E('已关闭短信提醒功能')
    NOT_START = E('您并没有打开短信提醒功能')
    START = E('已打开短信提醒功能')


def sms_validator(sms):
    if sms not in ['max', 'min']:
        raise BOCError.SMS


@Service.register
class BOCService(Service):
    name = 'boc'
    desc = '中银外汇牌价监测'
    long_desc = Lines(
        '监测中国银行外汇牌价',
        '⚠️支持多个币种现汇/现钞的买入/卖出价格',
        '⚠️使用短信提醒功能时需要设定具体的现汇/现钞和买入/卖出参数',
        '👉通过boc GBP -a命令获取英镑（GBP）的实时卖出价',
        '👉通过boc -s命令获取货币简写名称列表',
        '👉通过boc USA --ask --bn --sms=min命令监测美元的现钞卖出价，价格低于历史时会发短信提醒',
    )

    FX = {
        'GBP': '英镑', 'UK': '英镑', 'HKD': '港币', 'HK': '港币',
        'USD': '美元', 'US': '美元', 'USA': '美元', 'CHF': '瑞士法郎',
        'DEM': '德国马克', 'FRF': '法国法郎', 'FF': '法国法郎',
        'SGD': '新加坡元', 'SEK': '瑞典克朗', 'DKK': '丹麦克朗', 'NOK': '挪威克朗',
        'JPY': '日元', 'JP': '日元', 'CAD': '加拿大元', 'CA': '加拿大元',
        'AUD': '澳大利亚元', 'AU': '澳大利亚元', 'EUR': '欧元', 'EU': '欧元',
        'MOP': '澳门元', 'MO': '澳门元', 'PHP': '菲律宾比索', 'THB': '泰国铢',
        'NZD': '新西兰元', 'KIWI': '新西兰元', 'WON': '韩元', 'SK': '韩元',
        'RUB': '卢布', 'RU': '卢布', 'MYR': '林吉特', 'SEN': '林吉特',
        'NTD': '新台币', 'TW': '新台币', 'ESP': '西班牙比塞塔', 'ITL': '意大利里拉',
        'ANG': '荷兰盾', 'BEF': '比利时法郎', 'FIM': '芬兰马克', 'INR': '印度卢比',
        'IDR': '印尼卢比', 'BRL': '巴西里亚尔', 'AED': '阿联酋迪拉姆', 'ZAF': '南非兰特',
        'SAR': '沙特里亚尔', 'TRY': '土耳其里拉', 'YTL': '土耳其里拉'
    }

    FX_REVERSE = dict()

    KEY_TRANS = dict(SE_BID='现汇买入价', BN_BID='现钞买入价', SE_ASK='现汇卖出价', BN_ASK='现钞卖出价')
    M_TRANS = dict(min='低', max='高')

    async_user_task = True

    START = 1
    STOP = 0

    PSpotEx = Parameter(P(read_name='现汇价').default(), long='se')
    PBankNo = Parameter(P(read_name='现钞价').default(), long='bn')
    PBid = Parameter(P(read_name='买入价').default(), long='bid', short='b')
    PAsk = Parameter(P(read_name='卖出价').default(), long='ask', short='a')
    PShow = Parameter(P(read_name='显示货币简写列表').default(), long='show', short='s')
    PSms = Parameter(P(read_name='短信提醒').validate(sms_validator), long='sms')
    PSmsStop = Parameter(P(read_name='停止短信提醒').default(), long='sms-stop')

    @classmethod
    def init(cls):
        cls.validate(cls.PSpotEx, cls.PBankNo, cls.PBid, cls.PAsk, cls.PShow, cls.PSms, cls.PSmsStop)
        for k in cls.FX:
            if cls.FX[k] in cls.FX_REVERSE:
                cls.FX_REVERSE[cls.FX[k]].append(k)
            else:
                cls.FX_REVERSE[cls.FX[k]] = [k]

    @classmethod
    def async_user_handler(cls, storage_list: List[ServiceData]):
        for service_data in storage_list:
            cls.async_user(service_data)

    @classmethod
    def run(cls, directory: 'Service', storage: ServiceData, pd: ParamDict, *args):
        data = storage.classify()

        if pd.has(cls.PShow):
            return Lines(*['%s：%s' % (k, '或'.join(cls.FX_REVERSE[k])) for k in cls.FX_REVERSE])

        if pd.has(cls.PSmsStop):
            if data.status == cls.START:
                data.status = cls.STOP
                storage.update(data)
                raise BOCError.STOP
            raise BOCError.NOT_START

        if not args:
            return cls.need_help()

        currency = args[0].upper()
        if currency not in cls.FX:
            raise BOCError.CURRENCY

        if pd.has(cls.PSms):
            storage.user.require_phone()
            if not (pd.has(cls.PSpotEx) ^ pd.has(cls.PBankNo)):
                raise BOCError.SE_BN
            if not (pd.has(cls.PAsk) ^ pd.has(cls.PBid)):
                raise BOCError.BID_ASK

            sort = ('SE' if pd.has(cls.PSpotEx) else 'BN') + ','
            sort += 'ASK' if pd.has(cls.PAsk) else 'BID'
            storage.update(dict(
                currency=currency,
                sort=sort,
                monitor=pd.get(cls.PSms),
                value=None,
                status=cls.START,
            ))
            raise BOCError.START

        try:
            keys, values = bocfx(currency)
        except Exception as e:
            raise BOCError.SERVICE_INACCESSIBLE(debug_message=e)

        lines = []
        time = '实时'
        for i, k in enumerate(keys):
            if k in cls.KEY_TRANS:
                if pd.has(cls.PSpotEx) ^ pd.has(cls.PBankNo):
                    if pd.has(cls.PSpotEx) ^ ('SE' in k):
                        continue
                if pd.has(cls.PAsk) ^ pd.has(cls.PBid):
                    if pd.has(cls.PAsk) ^ ('ASK' in k):
                        continue
                lines.append('%s：%s' % (cls.KEY_TRANS[k], values[i]))
            if k == 'Time':
                time = values[i]
        lines.insert(0, '中国银行%s牌价（%s）' % (cls.FX[currency], time))
        return Lines(*lines)

    @classmethod
    def async_user(cls, storage: ServiceData):
        data = storage.classify()

        if not data.status:
            return
        if not data.error_times:
            data.error_times = 0

        crt_time = datetime.datetime.now().timestamp()
        if data.last_visit_time and data.last_visit_time + 60 * 60 > crt_time:
            return

        data.last_visit_time = crt_time

        try:
            value = bocfx(data.fx, data.sort)
        except E:
            data.error_times += 1
            if data.error_times == 3:
                Phone.announce(storage.user, cls, '中银%s汇率连续三次无法访问，已停止任务' % cls.FX[data.currency])
                storage.update(dict(status=cls.STOP))
            return

        value = float(value[0])
        if not data.value or ((data.value > value) ^ (data.monitor == 'max')):
            data.value = value
            message = str(value) + '！' + \
                      '中银%s的%s达到历史新' % (cls.FX[data.currency], cls.KEY_TRANS[data.sort.replace(',', '_')]) + \
                      cls.M_TRANS[data.monitor] + '。'
            Phone.announce(storage.user, cls, message)

        storage.update(data)
