import getpass
import subprocess
from argparse import ArgumentParser, Namespace

import fabricdw.common.config
from fabricdw.common import CONFIG, Installation, absolute_path, write_config
from fabricdw.installations import remove_installation, copy_installation
from fabricdw.installations.create import create_installation
from fabricdw.properties import create_replacements


LIST_ALL_INSTALLATIONS_ARG: str = "--list"


def parse_args() -> Namespace:
	defaults: fabricdw.common.config.Defaults = CONFIG.defaults
	
	parser = ArgumentParser()
	
	parser.add_argument("name", action="store", type=str, help="name of the installation")
	
	# Fabricdw
	# implicit --list argument, giving a name to list installations is dumb
	parser.add_argument("-c", "--copy", action="store", dest="copy")
	parser.add_argument("-r", "--remove", action="store_true", dest="remove")
	parser.add_argument("-d", "--directory", action="store", type=str, dest="output_dir", default=None)
	
	# Server
	parser.add_argument("-u", "--user", action="store", type=str, dest="user", default=getpass.getuser())
	parser.add_argument("-mn", "--min-ram", action="store", type=float, dest="min_ram", default=defaults.min_ram)
	parser.add_argument("-mx", "--max-ram", action="store", type=float, dest="max_ram", default=defaults.max_ram)
	parser.add_argument("-b", "--backups", action="store", type=int, dest="backups", default=defaults.backups)
	parser.add_argument("-i", "--idle-time", action="store", type=int, dest="idle_time", default=defaults.idle_time)
	parser.add_argument("--show-init-output", action="store_const", dest="init_output", default=subprocess.DEVNULL, const=None)
	
	parser.add_argument("-p", "--property", action="append", type=str, dest="properties", default=[])
	
	args: Namespace = parser.parse_args()
	
	args.properties = create_replacements(args)
	
	# if not given, use current dir + name
	args.output_dir = absolute_path(args.output_dir if args.output_dir is not None else f"./{args.name}")
	
	return args


def main() -> None:
	args = parse_args()
	
	active_installation: Installation | None = CONFIG.get_installation(args.name)
	
	if args.name == LIST_ALL_INSTALLATIONS_ARG:
		list_all_installations()
	elif args.remove:
		if remove_installation(active_installation, args.name):
			CONFIG.remove_installation(active_installation)
	elif args.copy:
		_dir = copy_installation(args)
		
		if _dir:
			CONFIG.add_installation(args.name, _dir)
	else:
		_dir = create_installation(active_installation, args)
		
		if _dir:
			CONFIG.add_installation(args.name, _dir)
	
	write_config()


def list_all_installations() -> None:
	print("All installations:")
	for installation in CONFIG.installations:
		print(f"\t{installation.pretty_name()} ({installation.root})")


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("Keyboard interrupt! Exiting!")
