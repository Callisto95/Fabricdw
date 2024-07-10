import getpass
import subprocess
from argparse import ArgumentParser, Namespace

from colorama import Fore, Style

arguments: Namespace | None = None


class InitializationError(Exception):
	pass


# importing ARGS (as Namespace) will not work
# it will *always* be a reference to None
def args() -> Namespace:
	global arguments
	
	if arguments is None:
		raise InitializationError("'parse_args' must be called before args is available")
	
	return arguments


def list_all_installations() -> None:
	from fabricdw.common import CONFIG
	
	if len(CONFIG.installations) == 0:
		print("There are no installations")
		return
	
	if args().verify:
		from fabricdw.common import Installation, InstallationDoesNotExistError
		for installation in CONFIG.installations:
			try:
				print(f"[ {Fore.BLUE}--{Style.RESET_ALL} ]", end="\r")
				
				Installation.ensure_exists(installation.name)
				
				print(f"[ {Fore.GREEN}OK{Style.RESET_ALL} ]", end="")
			except InstallationDoesNotExistError:
				print(f"[{Fore.RED}FAIL{Style.RESET_ALL}]", end="")
			finally:
				print(f" {installation}")
		
		print()
	
	if len(CONFIG.installations) == 0:
		print("There are no installations")
		return
	
	print("All installations:")
	for installation in CONFIG.installations:
		print(f"\t{installation}")


def parse_args() -> None:
	global arguments
	
	from fabricdw.common import absolute_path, CONFIG, VersionChoice
	from fabricdw.installations import (copy_installation, create_installation, delete_installation, move_installation,
		update_installation, rename_installation, import_installation)
	from fabricdw.properties import create_replacements
	
	root_parser = ArgumentParser()
	subparser = root_parser.add_subparsers()
	
	create_parser = subparser.add_parser("create", help="Create a new installation")
	delete_parser = subparser.add_parser("delete", help="Remove an existing installation")
	copy_parser = subparser.add_parser("copy", help="copies an existing installation")
	move_parser = subparser.add_parser("move", help="Moves an existing installation")
	rename_parser = subparser.add_parser("rename", help="Renames an existing installation")
	update_parser = subparser.add_parser("update", help="Updates the Fabric loader and installer of the installation")
	import_parser = subparser.add_parser("import", help="Import an existing installation")
	list_parser = subparser.add_parser("list", help="List all existing installations")
	
	# can be called with args.function()
	root_parser.set_defaults(function=lambda: root_parser.print_help())
	create_parser.set_defaults(function=create_installation)
	delete_parser.set_defaults(function=delete_installation)
	copy_parser.set_defaults(function=copy_installation)
	move_parser.set_defaults(function=move_installation)
	rename_parser.set_defaults(function=rename_installation)
	update_parser.set_defaults(function=update_installation)
	import_parser.set_defaults(function=import_installation)
	list_parser.set_defaults(function=list_all_installations)
	
	for parser in [create_parser, delete_parser, move_parser, update_parser, import_parser]:
		parser.add_argument("name", action="store", type=str, help="Name of the installation")
	
	for parser in [copy_parser, rename_parser]:
		parser.add_argument("source", action="store", type=str, help="Name of the source installation")
		parser.add_argument("target", action="store", type=str, help="Name of the target installation")
	
	for parser in [create_parser, update_parser]:
		parser.add_argument(
			"-p",
			"--property",
			action="append",
			type=str,
			dest="properties",
			default=[],
			help="changes the default properties in server.properties"
		)
		
		# general server properties
		parser.add_argument(
			"-u",
			"--user",
			action="store",
			type=str,
			dest="user",
			default=getpass.getuser(),
			help="The user, who starts the server"
		)
		parser.add_argument(
			"-m",
			"--min-ram",
			action="store",
			type=float,
			dest="min_ram",
			default=CONFIG.defaults.min_ram,
			help="Minimum amount of RAM the server can use"
		)
		parser.add_argument(
			"-x",
			"--max-ram",
			action="store",
			type=float,
			dest="max_ram",
			default=CONFIG.defaults.max_ram,
			help="Maximum amount of RAM the server can use"
		)
		parser.add_argument(
			"-k",
			"--backups",
			action="store",
			type=int,
			dest="backups",
			default=CONFIG.defaults.backups,
			help="The amount of backups which will be kept"
		)
		parser.add_argument(
			"-t",
			"--idle-time",
			action="store",
			type=int,
			dest="idle_time",
			default=CONFIG.defaults.idle_time,
			help="The time after which the server will turn idle"
		)
		parser.add_argument(
			"--show-init-output",
			action="store_const",
			dest="init_output",
			default=subprocess.DEVNULL,
			const=None,
			help="Show the output when the server initializes"
		)
		
		parser.add_argument(
			"--allow-non-empty",
			action="store_true",
			dest="allow_non_empty",
			help="Allows the target directory to be not empty"
		)
		parser.add_argument(
			"--allow-snapshots",
			action="store_true",
			dest="allow_snapshots",
			help="Allows the usage of snapshot game versions"
		)
		parser.add_argument(
			"--allow-unstable",
			action="store_true",
			dest="allow_unstable",
			help="Allows the usage of non-stable loader and installer versions. Recommended to use with "
				 "'--loader-version ask' and '--installer-version ask'."
		)
		
		# it is best to use the latest fabric version
		parser.add_argument(
			"-g",
			"--game-version",
			action="store",
			dest="game_version",
			default=VersionChoice.ASK,
			type=str,
			help="Which version of Minecraft to use. Either 'ask', 'latest', or an actual version	"
		)
		parser.add_argument(
			"-l",
			"--loader-version",
			action="store",
			dest="loader_version",
			default=VersionChoice.LATEST,
			type=str,
			help="Which version of the Fabric loader to use.  Either 'ask', 'latest', or an actual version"
		)
		parser.add_argument(
			"-i",
			"--installer-version",
			action="store",
			dest="installer_version",
			default=VersionChoice.LATEST,
			type=str,
			help="Which version of Fabric installer to use. Either 'ask', 'latest', or an actual version"
		)
		
		# java properties
		parser.add_argument(
			"--java",
			action="store",
			dest="java_executable",
			default="java",
			type=str,
			help="The java executable to use. Defaults to the 'java' command"
		)
		parser.add_argument(
			"--java-args", action="store", dest="java_args", default=[], type=str, help="Arguments for the JRE"
		)
	
	for parser in [create_parser, copy_parser]:
		parser.add_argument(
			"-d",
			"--directory",
			action="store",
			type=str,
			default=None,
			dest="output_dir",
			help="The directory in which Fabricdw will work"
		)
	
	# required instead of optional
	# still defaults to current directory
	for parser in [move_parser, import_parser]:
		parser.add_argument(
			"output_dir",
			action="store",
			type=str,
			default=None,
			help="The directory to which the installation will be moved to"
		)
	
	update_parser.add_argument(
		"--keep-backups", action="store_true", dest="keep_backups", help="If the created backups should be kept"
	)
	
	delete_parser.add_argument(
		"--yes-just-delete",
		action="store_true",
		dest="skip_delete_question",
		help="Skip the question whether the installation should really be deleted"
	)
	
	list_parser.add_argument(
		"--verify", action="store_true", dest="verify", help="verifies the existence all installtions"
	)
	
	args = root_parser.parse_args()
	
	args.allow_delete_directory = True
	
	if hasattr(args, "properties"):
		args.properties = create_replacements(args)
	
	# if not given, use current dir + name
	if hasattr(args, "output_dir") and args.output_dir is None:
		args.output_dir = absolute_path(args.output_dir if args.output_dir is not None else f"./{args.name}")
	
	arguments = args


__all__ = ["args", "parse_args"]
