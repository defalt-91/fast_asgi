import os

env_path = 'configurations/.env'


def write():
	with open(env_path, 'r') as f:
		lines_list = f.readlines()
		for line in lines_list:
			key, value = line.strip('\n').split('=')
			os.environ[key] = value


if __name__ == "__main__":
	write()
else:
	pass
