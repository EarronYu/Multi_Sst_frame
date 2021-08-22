
from dynaconf import Dynaconf
import yaml

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=['settings.yaml', '.secrets.yaml'],
)
fp = open('settings.yaml', 'r')
st = fp.read()
fp.close()
config_file = yaml.load(st, Loader=yaml.FullLoader)


# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load this files in the order.
