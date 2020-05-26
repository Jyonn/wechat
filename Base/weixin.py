import requests
from SmartDjango import E

from Base.common import QIX_APP_ID, QIX_APP_SECRET

import base64
import json
from Crypto.Cipher import AES


@E.register(id_processor=E.idp_cls_prefix())
class WeixinError:
    JS_CODE = E("需要鉴权代码")
    APP_ID = E("错误的小程序ID")
    DECRYPT = E("用户信息提取失败")


class Weixin:
    CODE2SESSION_URL = 'https://api.weixin.qq.com/sns/jscode2session' \
                       '?appid=%s' \
                       '&secret=%s' \
                       '&js_code=%s' \
                       '&grant_type=authorization_code'

    @staticmethod
    def code2session(code):
        url = Weixin.CODE2SESSION_URL % (QIX_APP_ID, QIX_APP_SECRET, code)

        data = requests.get(url).json()

        if 'openid' not in data:
            raise WeixinError.JS_CODE
        return data

    @classmethod
    def decrypt(cls, encrypted_data, iv, session_key):
        try:
            encrypted_data = base64.b64decode(encrypted_data)
            iv = base64.b64decode(iv)
            session_key = base64.b64decode(session_key)

            cipher = AES.new(session_key, AES.MODE_CBC, iv)

            decrypted = json.loads(cls._un_pad(cipher.decrypt(encrypted_data)).decode())

            if decrypted['watermark']['appid'] != QIX_APP_ID:
                raise WeixinError.APP_ID
        except Exception as err:
            raise WeixinError.DECRYPT(debug_message=err)

        return decrypted

    @staticmethod
    def _un_pad(s):
        return s[:-ord(s[len(s)-1:])]
