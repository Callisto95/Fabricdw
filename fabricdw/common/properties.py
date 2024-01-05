from enum import StrEnum


class Properties(StrEnum):
	WORLD_NAME = "level-name"
	PORT_SERVER = "server-port"
	PORT_QUERY = "query.port"


class Defaults(StrEnum):
	WORLD_NAME = "world"
	PORT_SERVER = "25565"
	PORT_QUERY = "25565"
