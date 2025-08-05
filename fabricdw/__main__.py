from fabricdw.args import args, parse_args
from fabricdw.common import InstallationAlreadyExistError, InstallationDoesNotExistError, write_config


def main() -> None:
	parse_args()
	
	try:
		args().function()
	except (InstallationAlreadyExistError, InstallationDoesNotExistError) as error:
		print(f"Error during processing: {error}")
		print()
		print("Exact cause:")
		print(error)
	
	write_config()


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("Keyboard interrupt! Exiting!")
