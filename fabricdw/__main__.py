from fabricdw.common import InstallationAlreadyExistError, InstallationDoesNotExistError, write_config
from fabricdw.args import parse_args, args


def main() -> None:
	parse_args()
	
	try:
		args().function()
	except (InstallationAlreadyExistError, InstallationDoesNotExistError) as error:
		print(error)
	
	write_config()


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("Keyboard interrupt! Exiting!")
