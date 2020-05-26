import base64

from Crypto import Random
from Crypto.Cipher import AES
from SmartDjango import E

from Base.common import SECRET_KEY


@E.register(id_processor=E.idp_cls_prefix())
class CryptoError:
    AES_ENCRYPT = E("AES加密失败")
    AES_DECRYPT = E("AES解密失败")


class Crypto:
    class AES:
        @staticmethod
        def encrypt(data):
            try:
                key = SECRET_KEY[:16]
                iv = Random.new().read(AES.block_size)
                cipher = AES.new(key, AES.MODE_CBC, iv)
                encrypted_data = iv + cipher.encrypt(data)
                encrypted_data = base64.b64encode(encrypted_data).decode()
            except Exception as err:
                raise CryptoError.AES_ENCRYPT(debug_message=err)
            return encrypted_data

        @staticmethod
        def decrypt(encrypted_data):
            try:
                encrypted_data = base64.b64decode(encrypted_data)
                key = SECRET_KEY[:16]
                iv = encrypted_data[:16]
                encrypted_data = encrypted_data[16:]
                cipher = AES.new(key, AES.MODE_CFB, iv)
                data = cipher.decrypt(encrypted_data).decode()
            except Exception as err:
                raise CryptoError.AES_DECRYPT(debug_message=err)
            return data
