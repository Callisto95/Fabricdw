# METHODS MUST BE FIRST
# CONFIG REQUIRES SOME METHODS
from fabricdw.common.methods import (absolute_path, ask_okay_to_write_into, convert_bool_to_str, convert_str_to_bool,
	remove_dir, yes_no_question)
from fabricdw.common.config import (CONFIG, Config, Defaults, Installation, InstallationAlreadyExistError,
	InstallationDoesNotExistError, InvalidCombinationException, VersionChoice, write_config)
	
SERVER_JAR_FILE: str = "fabric-server-launch.jar"
SERVER_PROPERTIES_FILE: str = "server.properties"
FABRICD_ENV_FILE: str = "fabricdw"
EULA_FILE: str = "eula.txt"
