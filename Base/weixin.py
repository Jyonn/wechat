import requests
from SmartDjango import E

from Base.common import QIX_APP_ID, QIX_APP_SECRET

import base64
import json
from Crypto.Cipher import AES

from Config.models import CI, Config


@E.register(id_processor=E.idp_cls_prefix())
class WeixinError:
    JS_CODE = E("需要鉴权代码")
    APP_ID = E("错误的小程序ID")
    DECRYPT = E("用户信息提取失败")
    SAFE_CHECK_FAIL = E("敏感检测失败", hc=500)
    CONTENT_UNSAFE = E("存在敏感内容", hc=403)


class Weixin:
    CODE2SESSION_URL = 'https://api.weixin.qq.com/sns/jscode2session' \
                       '?appid=%s' \
                       '&secret=%s' \
                       '&js_code=%s' \
                       '&grant_type=authorization_code'

    MSG_SEC_CHECK_URL = 'https://api.weixin.qq.com/wxa/msg_sec_check?access_token=%s'

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

    @classmethod
    def msg_sec_check(cls, content):
        access_token = Config.get_value_by_key(CI.QIX_ACCESS_TOKEN)
        try:
            data = json.dumps(dict(content=content), ensure_ascii=False)
            data = data.encode()
            resp = requests.post(cls.MSG_SEC_CHECK_URL % access_token, data=data)
            data = resp.json()
            if data['errcode'] == 87014:
                raise WeixinError.CONTENT_UNSAFE
            if data['errcode'] != 0:
                raise WeixinError.SAFE_CHECK_FAIL
        except E as e:
            raise e
        except Exception:
            raise WeixinError.SAFE_CHECK_FAIL
