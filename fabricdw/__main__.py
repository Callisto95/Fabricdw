import getpass
import subprocess
from argparse import ArgumentParser, Namespace
from enum import StrEnum

import fabricdw.common.config
from fabricdw.common import CONFIG, absolute_path, write_config
from fabricdw.installations import remove_installation, copy_installation
from fabricdw.installations.create import create_installation
from fabricdw.properties import create_replacements

LIST_ALL_INSTALLATIONS_ARG: str = "--list"


class Choices(StrEnum):
	CREATE = "create"
	REMOVE = "remove"
	COPY = "copy"
	LIST = "list"


def add_property_argument(*parsers) -> None:
	for parser in parsers:
		parser.add_argument("-p", "--property", action="append", type=str, dest="properties", default=[])


def add_name_argument(*parsers) -> None:
	for parser in parsers:
		parser.add_argument("name", action="store", type=str, help="name of the installation")


def add_server_properties(*parsers) -> None:
	defaults: fabricdw.common.config.Defaults = CONFIG.defaults
	
	for parser in parsers:
		parser.add_argument("-u", "--user", action="store", type=str, dest="user", default=getpass.getuser(), help="the user who starts the server")
		parser.add_argument("-mn", "--min-ram", action="store", type=float, dest="min_ram", default=defaults.min_ram, help="minimum amount of RAM the server can use")
		parser.add_argument("-mx", "--max-ram", action="store", type=float, dest="max_ram", default=defaults.max_ram, help="maximum amount of RAM the server can use")
		parser.add_argument("-b", "--backups", action="store", type=int, dest="backups", default=defaults.backups, help="the amount of backups which will be kept")
		parser.add_argument("-i", "--idle-time", action="store", type=int, dest="idle_time", default=defaults.idle_time, help="the time after which the server will turn idle")
		parser.add_argument("--show-init-output", action="store_const", dest="init_output", default=subprocess.DEVNULL, const=None, help="show the output when the server initializes")


def add_output_dir(*parsers) -> None:
	for parser in parsers:
		parser.add_argument("-d", "--directory", action="store", type=str, default=None, dest="output_dir", help="the directory in which Fabricdw will work")


def parse_args() -> Namespace:
	parser = ArgumentParser()
	subparser = parser.add_subparsers()
	
	create_parser = subparser.add_parser(Choices.CREATE)
	remove_parser = subparser.add_parser(Choices.REMOVE)
	copy_parser = subparser.add_parser(Choices.COPY)
	list_parser = subparser.add_parser(Choices.LIST)
	
	# can be called with args.function()
	create_parser.set_defaults(function=create_installation)
	remove_parser.set_defaults(function=remove_installation)
	copy_parser.set_defaults(function=copy_installation)
	list_parser.set_defaults(function=list_all_installations)
	
	add_name_argument(create_parser, copy_parser, remove_parser)
	add_property_argument(create_parser, copy_parser)
	add_server_properties(create_parser, copy_parser)
	add_output_dir(create_parser, copy_parser)
	
	copy_parser.add_argument("new_name", action="store", type=str, help="the new name of the installation")
	
	create_parser.add_argument("--absolute-paths", action="store_true", dest="absolute_paths", help="use absolute paths, instead of relying on pwd")
	
	args: Namespace = parser.parse_args()
	
	if hasattr(args, "properties"):
		args.properties = create_replacements(args)
	
	# if not given, use current dir + name
	if hasattr(args, "output_dir") and args.output_dir is None:
		args.output_dir = absolute_path(args.output_dir if args.output_dir is not None else f"./{args.name}")
	
	return args


def main() -> None:
	args = parse_args()
	
	args.function(args)
	
	write_config()


# args is a required parameter
def list_all_installations(args: Namespace) -> None:
	print("All installations:")
	for installation in CONFIG.installations:
		print(f"\t{installation.pretty_name()} ({installation.root})")


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("Keyboard interrupt! Exiting!")
