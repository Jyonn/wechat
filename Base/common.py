import hashlib
from datetime import datetime

from SmartDjango import NetPacker, E
from django.http import HttpResponse
from wechatpy import WeChatClient

from Base.logging import Logging
from Config.models import Config, CI


DEV_MODE = True


# def data_packer(resp):
#     return resp['body'] or ''


def body_packer(func):
    def wrapper(r, *args, **kwargs):
        try:
            data = func(r, *args, **kwargs)
        except E:
            data = ''
        return HttpResponse(
            data,
            status=200,
            content_type="application/json; encoding=utf-8",
        )
    return wrapper


NetPacker.set_mode(debug=True)
# NetPacker.customize_data_packer(data_packer)

ADMIN_PHONE = Config.get_value_by_key(CI.ADMIN_PHONE)

WX_TOKEN = Config.get_value_by_key(CI.WX_TOKEN)
WX_AES_KEY = Config.get_value_by_key(CI.WX_AES_KEY)
WX_APP_ID = Config.get_value_by_key(CI.WX_APP_ID)
WX_APP_SECRET = Config.get_value_by_key(CI.WX_APP_SECRET)

QIX_APP_ID = Config.get_value_by_key(CI.QIX_APP_ID)
QIX_APP_SECRET = Config.get_value_by_key(CI.QIX_APP_SECRET)

YP_KEY = Config.get_value_by_key(CI.YP_KEY)

SECRET_KEY = Config.get_value_by_key(CI.SECRET_KEY)
JWT_ENCODE_ALGO = Config.get_value_by_key(CI.JWT_ENCODE_ALGO)

wechat_client = WeChatClient(appid=WX_APP_ID, secret=WX_APP_SECRET)
qiX_client = WeChatClient(appid=QIX_APP_ID, secret=QIX_APP_SECRET)

logging = Logging(datetime.now().strftime('%Y-%m-%d %H%M%S') + '.log')


def md5(b):
    m = hashlib.md5()
    m.update(b)
    return m.hexdigest()
