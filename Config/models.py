from SmartDjango import models, E, Hc


@E.register(id_processor=E.idp_cls_prefix())
class ConfigError:
    CREATE = E("更新配置错误", hc=Hc.InternalServerError)
    NOT_FOUND = E("不存在的配置", hc=Hc.NotFound)


class Config(models.Model):
    key = models.CharField(
        max_length=100,
        unique=True,
    )

    value = models.CharField(
        max_length=255,
    )

    @classmethod
    def get_config_by_key(cls, key):
        cls.validator(locals())

        try:
            return cls.objects.get(key=key)
        except cls.DoesNotExist as err:
            raise ConfigError.NOT_FOUND(debug_message=err)

    @classmethod
    def get_value_by_key(cls, key, default=None):
        try:
            return cls.get_config_by_key(key).value
        except Exception:
            return default

    @classmethod
    def update_value(cls, key, value):
        cls.validator(locals())

        try:
            config = cls.get_config_by_key(key)
            config.value = value
            config.save()
        except E as e:
            if e.eis(ConfigError.NOT_FOUND):
                try:
                    return cls.objects.get_or_create(
                        key=key,
                        value=value,
                    )
                except Exception as err:
                    raise ConfigError.CREATE(debug_message=err)
            else:
                raise e
        except Exception as err:
            raise ConfigError.CREATE(debug_message=err)


class ConfigInstance:
    ADMIN_PHONE = 'admin-phone'

    WX_TOKEN = 'wx-Token'
    WX_AES_KEY = 'wx-EncodingAESKey'
    WX_APP_ID = 'wx-AppID'
    WX_APP_SECRET = 'wx-AppSecret'

    WX_ACCESS_TOKEN = 'wx-AccessToken'
    WX_ACCESS_TOKEN_EXPIRE = 'wx-AccessTokenExpire'

    YP_KEY = 'yp-Key'

    SECRET_KEY = 'secret_key'
    JWT_ENCODE_ALGO = 'jwt_encode_algo'

    QIX_APP_ID = 'qiX-AppID'
    QIX_APP_SECRET = 'qiX-AppSecret'


CI = ConfigInstance
