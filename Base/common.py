from SmartDjango import NetPacker

from Config.models import Config, CI


def data_packer(resp):
    return resp['body'] or ''


NetPacker.set_mode(debug=True)
NetPacker.customize_data_packer(data_packer)

WX_TOKEN = Config.get_value_by_key(CI.WX_TOKEN)
WX_AES_KEY = Config.get_value_by_key(CI.WX_AES_KEY)
