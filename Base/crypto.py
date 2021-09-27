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
        def encrypt(data, key=None, iv=None):
            try:
                key = key or SECRET_KEY[:16]
                iv = iv or Random.new().read(AES.block_size)
                cipher = AES.new(key, AES.MODE_CBC, iv)
                encrypted_data = iv + cipher.encrypt(data)
                encrypted_data = base64.b64encode(encrypted_data).decode()
            except Exception as err:
                raise CryptoError.AES_ENCRYPT(debug_message=err)
            return encrypted_data

        @staticmethod
        def decrypt(encrypted_data, key=None):
            try:
                encrypted_data = base64.b64decode(encrypted_data)
                key = key or SECRET_KEY[:AES.block_size]
                iv = encrypted_data[:AES.block_size]
                encrypted_data = encrypted_data[AES.block_size:]
                cipher = AES.new(key, AES.MODE_CFB, iv)
                data = cipher.decrypt(encrypted_data).decode()
            except Exception as err:
                raise CryptoError.AES_DECRYPT(debug_message=err)
            return data

    class AES_ECB:
        @classmethod
        def encrypt(cls, data, key=None, iv=None):
            try:
                key = key or SECRET_KEY[:16]
                iv = iv or Random.new().read(AES.block_size)
                cipher = AES.new(key, AES.MODE_ECB, iv)
                x = AES.block_size - (len(data) % AES.block_size)
                if x:
                    data += chr(x) * x
                encrypted_data = cipher.encrypt(data)
                encrypted_data = base64.b64encode(encrypted_data).decode()
            except Exception as err:
                raise CryptoError.AES_ENCRYPT(debug_message=err)
            return encrypted_data

        @classmethod
        def decrypt(cls, encrypted_data, key=None):
            try:
                encrypted_data = base64.b64decode(encrypted_data)
                key = key or SECRET_KEY[:16]
                iv = encrypted_data[:AES.block_size]
                cipher = AES.new(key, AES.MODE_ECB, iv)
                data = cipher.decrypt(encrypted_data).decode()
                padding_len = data[len(data) - 1]
                if not isinstance(padding_len):
                    padding_len = ord(padding_len)
                data = data[:-padding_len]
            except Exception as err:
                raise CryptoError.AES_DECRYPT(debug_message=err)
            return data
