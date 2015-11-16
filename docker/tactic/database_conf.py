import os

import tacticenv
from pyasm.common import Config
from pyasm.search import DbPasswordUtil

DbPasswordUtil.set_password('')

Config.set_value("database", "server", os.environ['TACTIC_POSTGRES_PORT_5432_TCP_ADDR'])
Config.save_config()
