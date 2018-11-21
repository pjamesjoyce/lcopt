from lcopt.utils import lcopt_bw2_autosetup
from sys import argv

def main():
    setup_params = dict(ei_username=None,
                        ei_password=None,
                        ecoinvent_version="3.3",
                        ecoinvent_system_model="cutoff",
                        overwrite=True)

    param_list = ["script", "ei_username", "ei_password", "ecoinvent_version", "ecoinvent_system_model", "overwrite"]

    for i in range(1,5):
        try:
            setup_params[param_list[i]] = argv[i]
        except IndexError:
            pass

    print(setup_params)

    if setup_params['ei_username'] is not None and setup_params['ei_password'] is not None:
        setup = lcopt_bw2_autosetup(**setup_params)
    else:
        print("No credentials provided")

if __name__ == '__main__':
    main()
