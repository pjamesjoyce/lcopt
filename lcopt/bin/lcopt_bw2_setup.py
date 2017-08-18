from sys import argv
from lcopt.utils import lcopt_bw2_setup


def main():
    ecospold_path = argv[1]
    lcopt_bw2_setup(ecospold_path)


if __name__ == "__main__":
    main()
