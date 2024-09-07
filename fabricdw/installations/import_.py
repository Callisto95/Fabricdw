from os.path import exists

from fabricdw.args import args
from fabricdw.common import CONFIG, Installation


def import_installation() -> None:
	Installation.ensure_does_not_exist(args().name)
	
	target_directory: str = args().output_dir
	
	if not exists(target_directory):
		print(f"Invalid path ({target_directory})")
		return
	
	CONFIG.create_new_installation(args().name, target_directory)
