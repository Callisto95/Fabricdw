import os
import shutil

from fabricdw.args import args
from fabricdw.common import ask_okay_to_write_into, CONFIG, Installation, remove_dir


def move_installation() -> None:
	source: Installation = Installation.ensure_exists(args().name)
	
	target_directory: str = args().output_dir
	
	try:
		os.makedirs(target_directory, exist_ok=True)
		
		if not ask_okay_to_write_into(target_directory, message_if_cancelled="move cancelled"):
			return
		
		os.replace(source.root, target_directory)
		
		old_root = source.root
		source.root = target_directory
		
		print(
			f"Moved {source.pretty_name()} ('{old_root}' -> '{target_directory}')	"
		)
	except KeyboardInterrupt:
		if remove_dir(target_directory):
			print("Interrupted! Cleaning up...")


def rename_installation() -> None:
	installation: Installation = Installation.ensure_exists(args().source)
	
	installation.name = args().target
	
	print(f"Renamed {Installation.pretty_name_str(args().source)} to {Installation.pretty_name_str(args().target)}")
