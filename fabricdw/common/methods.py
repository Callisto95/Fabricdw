import os.path
import shutil

from pick import pick

from fabricdw.args import args


def yes_no_question(question: str, yes_first: bool = False) -> bool:
	options = ["No", "Yes"]
	
	if yes_first:
		options = options[::-1]
	
	_, index = pick(options, question, indicator=">")
	
	return index == 1


def remove_dir(directory: str) -> None:
	if args().allow_delete_directory:
		shutil.rmtree(directory)
	else:
		print(f"Keeping directory '{directory}' as it was not empty beforehand")


def absolute_path(path: str) -> str:
	return os.path.abspath(os.path.expanduser(path))


def directory_is_empty(directory: str) -> bool:
	return len(os.listdir(directory)) == 0


def ask_okay_to_write_into(directory: str = None, message_if_cancelled: str = None) -> bool:
	"""Asks the user if the non-empty directory may be written into.
	It is determined whether the directory is empty within this method
	
	:returns: True if writing into the given directory is allowed"""
	
	if not directory:
		directory = args().output_dir
	
	if not os.path.isdir(directory):
		raise ValueError(f"The given directory '{directory}' is not a directory")
	
	if directory_is_empty(directory):
		return True
	else:
		if args().allow_non_empty:
			print(f"Writing into filled directory '{directory}'")
			args().allow_delete_directory = False
			return True
		else:
			answer: bool = yes_no_question(f"The directory '{directory}' is not empty. Proceed anyway?")
			
			if not answer and message_if_cancelled:
				print(message_if_cancelled)
			
			return answer


def convert_bool_to_str(b: bool) -> str:
	return "true" if b else "false"


def convert_str_to_bool(s: str) -> bool:
	match s:
		case "true":
			return True
		case "false":
			return False
		case _:
			raise ValueError(f"str '{s}' is not convertable to bool")
