from fabricdw.args import args
from fabricdw.properties.modify import create_replacements, modify_properties


def get_property(property_name: str, fallback: str = None) -> str | None:
	if property_name in args().properties:
		return args().properties[property_name]
	return fallback
