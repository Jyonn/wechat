from SmartDjango import NetPacker

from Config.models import Config, CI

NetPacker.set_mode(debug=True)

WX_TOKEN = Config.get_value_by_key(CI.WX_TOKEN)
WX_AES_KEY = Config.get_value_by_key(CI.WX_AES_KEY)
