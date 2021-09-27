import re

import requests
from SmartDjango import E
from SmartDjango.classify import Classify
from bs4 import BeautifulSoup

from Base.common import ADMIN_PHONE, msg_idp
from Base.crypto import Crypto
from Base.phone import Phone


@E.register(id_processor=msg_idp)
class SMSMessage:
    NONE = E('暂无可用的共享手机号')
    NO_PHONE = E('请使用sms -r命令获取新手机号')
    FAIL_FETCH = E('获取短信失败')


class FreeSMSCrawler:
    NAME = 'NAME'
    BASE_URL = ''

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
    }

    @classmethod
    def get_web_data(cls, url, data: Classify):
        try:
            with requests.get(url, headers=cls.HEADERS) as r:
                html = r.content.decode()
            data.error_web_times = 0
        except Exception:
            data.error_web_times += 1
            if data.error_web_times == 3:
                Phone.announce(ADMIN_PHONE, cls, '无法获取网站信息')
            return
        return html

    @classmethod
    def get_phone_list(cls, data: Classify):
        raise NotImplementedError

    @classmethod
    def get_msg(cls, data: Classify, phone):
        raise NotImplementedError


class FreeReceiveSMS(FreeSMSCrawler):
    NAME = 'freereceivesms.com'
    BASE_URL = 'https://www.freereceivesms.com'

    @staticmethod
    def item_processor(item):
        time = item.find(class_='font-italic').text
        msg = item.find(class_='col-lg-8').find('div')
        if msg.get('sec') is not None:  # may be ''
            msg = Crypto.AES_ECB.decrypt(msg.text, key='vnPrahqvcnLvcYZ5')
        else:
            msg = msg.text
        if msg:
            return ['👉%s' % time, msg, '']

    @classmethod
    def get_phone_list(cls, data: Classify):
        html = cls.get_web_data(cls.BASE_URL + '/en/cn/', data)
        if not html:
            return

        data.fr_map = data.fr_map or dict()
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all(class_='border p-3')
        for item in items:
            phone = item.find('h4').text
            if not phone.startswith('+86 '):
                data.error_re_times += 1
                if data.error_re_times == 3:
                    Phone.announce(ADMIN_PHONE, cls, '无法解析手机信息')
                return
            phone = phone[4:]
            href = item.find('a').get('href')
            data.fr_map[phone] = href

        return [int(phone) for phone in data.fr_map]

    @classmethod
    def get_msg(cls, data: Classify, phone):
        data.fr_map = data.fr_map or dict()
        phone = str(phone)
        if phone not in data.fr_map:
            raise SMSMessage.NO_PHONE
        href = data.fr_map[phone]

        url = '%s%s' % (cls.BASE_URL, href)
        try:
            with requests.get(url, headers=cls.HEADERS) as r:
                html = r.content.decode()
        except Exception:
            raise SMSMessage.FAIL_FETCH

        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all(class_='border-bottom')
        items = [cls.item_processor(item) for item in items][:10]
        items = list(filter(lambda x: x, items))
        lines = []
        [lines.extend(item) for item in items]
        return lines


class TemporaryPhoneNumber(FreeSMSCrawler):
    NAME = 'temporary-phone-number.com'
    BASE_URL = 'https://temporary-phone-number.com/China-Phone-Number/'

    @staticmethod
    def item_processor(item):
        time = item.find('time').text
        msg = item.find(class_='direct-chat-text').text.strip().replace('\x1b', '')
        if msg:
            return ['👉%s' % time, msg, '']

    @classmethod
    def get_phone_list(cls, data: Classify):
        html = cls.get_web_data(cls.BASE_URL, data)
        if not html:
            return

        finder = re.findall('"%s86(\d+)"' % cls.BASE_URL, html, flags=re.S)
        if not finder:
            data.error_re_times += 1
            if data.error_re_times == 3:
                Phone.announce(ADMIN_PHONE, cls, '无法解析手机信息')
            return

        return [int(phone) for phone in finder]

    @classmethod
    def get_msg(cls, data: Classify, phone):
        url = '%s86%s' % (cls.BASE_URL, phone)
        try:
            with requests.get(url) as r:
                html = r.content.decode()
        except Exception:
            raise SMSMessage.FAIL_FETCH

        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all(class_='direct-chat-msg')
        items = [cls.item_processor(item) for item in items][:10]
        items = list(filter(lambda x: x, items))
        lines = []
        [lines.extend(item) for item in items]
        return lines
