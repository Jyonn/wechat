from django.db import models
from smartdjango import Error

from Config.validators import ConfigValidator, ConfigErrors


class Config(models.Model):
    vldt = ConfigValidator

    key = models.CharField(
        max_length=vldt.MAX_KEY_LENGTH,
        unique=True,
        validators=[vldt.key],
    )

    value = models.CharField(
        max_length=vldt.MAX_VALUE_LENGTH,
        validators=[vldt.value],
    )

    @classmethod
    def get_config_by_key(cls, key) -> 'Config':
        try:
            return cls.objects.get(key=key)
        except cls.DoesNotExist as err:
            raise ConfigErrors.NOT_FOUND(details=err)

    @classmethod
    def get_value_by_key(cls, key, default=None):
        try:
            return cls.get_config_by_key(key).value
        except Exception:
            return default

    @classmethod
    def update_value(cls, key, value):
        try:
            config = cls.get_config_by_key(key)
            config.value = value
            config.save()
        except Error as e:
            if e == ConfigErrors.NOT_FOUND:
                try:
                    config = cls(
                        key=key,
                        value=value,
                    )
                    config.save()
                except Exception as err:
                    raise ConfigErrors.CREATE(details=err)
            else:
                raise e
        except Exception as err:
            raise ConfigErrors.CREATE(details=err)


class ConfigInstance:
    ADMIN_PHONE = 'admin-phone'

    WX_TOKEN = 'wx-Token'
    WX_AES_KEY = 'wx-EncodingAESKey'
    WX_APP_ID = 'wx-AppID'
    WX_APP_SECRET = 'wx-AppSecret'

    WX_ACCESS_TOKEN = 'wx-AccessToken'
    WX_ACCESS_TOKEN_EXPIRE = 'wx-AccessTokenExpire'

    QIX_ACCESS_TOKEN = 'qiX-AccessToken'
    QIX_ACCESS_TOKEN_EXPIRE = 'qiX-AccessTokenExpire'

    YP_KEY = 'yp-Key'

    SECRET_KEY = 'secret_key'
    JWT_ENCODE_ALGO = 'jwt_encode_algo'

    QIX_APP_ID = 'qiX-AppID'
    QIX_APP_SECRET = 'qiX-AppSecret'


CI = ConfigInstance
