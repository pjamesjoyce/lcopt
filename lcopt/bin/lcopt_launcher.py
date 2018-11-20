from tkinter import *
from tkinter import ttk
from tkinter import filedialog, simpledialog
from lcopt.utils import FORWAST_PROJECT_NAME, check_for_config, DEFAULT_CONFIG, bw2_project_exists, DEFAULT_PROJECT_STEM
from lcopt.data_store import storage
from lcopt.settings import settings
from lcopt import LcoptModel
import yaml
from brightway2 import *
import os
from pathlib import Path

asset_path = os.path.join(Path(os.path.dirname(os.path.realpath(__file__))).parent, 'assets')
example_ecoinvent_version = "3.3"
example_ecoinvent_system_model = "cutoff"


def check_databases():
    # TODO update this to match the new checks depending on settings

    example_ecoinvent_present = False
    default_ecoinvent_present = False
    forwast_present = False
    ecoinvent_list = []

    example_ei_name = "Ecoinvent{}_{}_{}".format(*example_ecoinvent_version.split('.'), example_ecoinvent_system_model)
    example_formatted = "{}.{} {}".format(*example_ei_name[9:].split("_"))

    config_file = check_for_config()
    # If, for some reason, there's no config file, write the defaults
    if config_file is None:
        config_file = DEFAULT_CONFIG
        with open(storage.config_file, "w") as cfg:
            yaml.dump(config_file, cfg, default_flow_style=False)

    store_option = storage.project_type

    default_ei_name = "Ecoinvent{}_{}_{}".format(*settings.ecoinvent.version.split('.'), settings.ecoinvent.system_model)
    default_formatted = "{}.{} {}".format(*default_ei_name[9:].split("_"))

    # Check if there's already a project set up that matches the current configuration

    if store_option == 'single':

        project_name = storage.single_project_name

        if bw2_project_exists(project_name):
            projects.set_current(project_name)
            if example_ei_name in databases:
                example_ecoinvent_present = True
            if default_ei_name in databases:
                default_ecoinvent_present = True
            if 'forwast' in databases:
                forwast_present = True

            ecoinvent_list = ["{}.{} {}".format(*x[9:].split("_"))
                              for x in databases
                              if x.startswith("Ecoinvent")]

    else:  # default to 'unique'
        example_project_name = DEFAULT_PROJECT_STEM + example_ei_name
        default_project_name = DEFAULT_PROJECT_STEM + default_ei_name

        example_ecoinvent_present = bw2_project_exists(example_project_name)
        default_ecoinvent_present = bw2_project_exists(default_project_name)

        forwast_present = bw2_project_exists(FORWAST_PROJECT_NAME)

        ecoinvent_list = ["{}.{} {}".format(*x.name[21:].split("_"))
                          for x in projects
                          if x.name.startswith("LCOPT_Setup_Ecoinvent")]

    return {'ecoinvent': {
            'default': {'name': default_formatted, 'present': default_ecoinvent_present},
            'example': {'name': example_formatted, 'present': example_ecoinvent_present},
            'list': ecoinvent_list
            },
            'forwast': {
                'default': forwast_present}
            }


def main():
    dbc = check_databases()
    CHECK_EXAMPLE_ECOINVENT = dbc['ecoinvent']['example']['present']
    EXAMPLE_ECOINVENT_NAME = dbc['ecoinvent']['example']['name']
    CHECK_FORWAST = dbc['forwast']['default']
    CHECK_DEFAULT_ECOINVENT = dbc['ecoinvent']['default']['present']
    DEFAULT_ECOINVENT_NAME = dbc['ecoinvent']['default']['name']
    ECOINVENT_LIST = dbc['ecoinvent']['list']

    ECOINVENT_USER = settings.ecoinvent.username not in [None, 'None']
    print("example ecoinvent: {}\n"
          "default ecoinvent: {}\n"
          "installed ecoinvent versions: {}\n"
          "forwast: {}\n"
          "ecoinvent user: {}".format(CHECK_EXAMPLE_ECOINVENT, CHECK_DEFAULT_ECOINVENT, ECOINVENT_LIST, CHECK_FORWAST, ECOINVENT_USER))

    def create_model(*args):
        print("Create")
        #root.withdraw()
        model_name = simpledialog.askstring("New", "Enter a name for your model")
        if model_name:
            if ECOINVENT_USER or CHECK_DEFAULT_ECOINVENT:
                model = LcoptModel(model_name)
            else:
                model = LcoptModel(model_name, useForwast=True)
            model.launch_interact()
            root.destroy()
        else:
            pass
            # root.deiconify()



    def load_model(*args):
        print("Load")
        root.withdraw()

        titleString = "Choose a model to open"
        filetypesList = [('Lcopt model files', '.lcopt')]
        file_path = filedialog.askopenfilename(title=titleString, filetypes=filetypesList, initialdir=storage.model_dir)
        print(file_path)

        if file_path:
            model = LcoptModel(load=file_path)
            model.launch_interact()

        root.destroy()

    def load_example(*args):
        print("Load example")

        root.withdraw()

        if CHECK_EXAMPLE_ECOINVENT:
            file_path = os.path.join(asset_path, 'ecoinvent_example.lcopt')
            useForwast = False
        elif CHECK_FORWAST:
            file_path = os.path.join(asset_path, 'forwast_example.lcopt')
            useForwast = True
        else:
            if ECOINVENT_USER:
                print('setting up for ecoinvent')
                file_path = os.path.join(asset_path, 'ecoinvent_example.lcopt')
                useForwast = False
            else:
                print('setting up for forwast')
                file_path = os.path.join(asset_path, 'forwast_example.lcopt')
                useForwast = True

        #    root.destroy()
        #    return
        if useForwast:
            print('loading forwast model')
            model = LcoptModel(load=file_path, useForwast=useForwast)
        else:
            model = LcoptModel(load=file_path, ecoinvent_version=example_ecoinvent_version,
                               ecoinvent_system_model=example_ecoinvent_system_model)

        model.launch_interact()

        root.destroy()

    def launch_settings():
        settings.launch_interact()
        root.destroy()

    icon = os.path.join(asset_path, 'lcopt_icon.ico')
    root = Tk()
    root.title("LCOPT Launcher")
    try:
        root.iconbitmap(icon)
    except:
        pass

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    initial_width = 625
    initial_height = 250  # 125
    initial_x = int(screen_width / 2 - initial_width / 2)
    initial_y = int(screen_height / 2 - initial_height / 2)

    root.geometry('{}x{}+{}+{}'.format(initial_width, initial_height, initial_x, initial_y))

    # TODO: Maybe figure out how to use a custom icon - not urgent
    # img = PhotoImage(file = r'C:\Users\pjjoyce\Dropbox\04. REDMUD IP LCA Project\04. Modelling\lcopt\static\img\lcoptIcon2.gif')
    # root.tk.call('wm', 'iconphoto', root._w, img)

    mainframe = ttk.Frame(root, padding="20 20 20 20")  # padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    ttk.Label(mainframe, text="Actions").grid(row=0, column=0)
    ttk.Label(mainframe, text="Database status").grid(row=0, column=1)
    btn_width = 20
    #ttk.Label(mainframe, text="Welcome to the LCOPT Launcher").grid(column=1, row=1, columnspan=3)
    ttk.Button(mainframe, text="Create Model", command=create_model, width=btn_width).grid(column=0, row=1, sticky=W)
    ttk.Button(mainframe, text="Open Model", command=load_model, width=btn_width).grid(column=0, row=2, sticky=W)
    btn_example = ttk.Button(mainframe, text="Open Example Model", command=load_example, width=btn_width)
    btn_example.grid(column=0, row=3, sticky=W)
    btn_settings = ttk.Button(mainframe, text="Settings", command=launch_settings, width=btn_width)
    btn_settings.grid(column=0, row=4, sticky=W)

    if CHECK_EXAMPLE_ECOINVENT:
        example_ecoinvent_label = "Yes ({})".format(EXAMPLE_ECOINVENT_NAME)
    else:
        example_ecoinvent_label = "No ({})".format(EXAMPLE_ECOINVENT_NAME)

    if CHECK_DEFAULT_ECOINVENT:
        default_ecoinvent_label = "Yes ({})".format(DEFAULT_ECOINVENT_NAME)
    else:
        default_ecoinvent_label = "No ({})".format(DEFAULT_ECOINVENT_NAME)

    if CHECK_FORWAST:
        forwast_label = "Yes"
    else:
        forwast_label = "No"

    if ECOINVENT_USER:
        user_label = "Yes ({})".format(settings.ecoinvent.username)
    else:
        user_label = "No"

    tv = ttk.Treeview(mainframe, height=max(5, min(6, 4+len(ECOINVENT_LIST))))
    vsb = ttk.Scrollbar(mainframe, orient="vertical", command=tv.yview)
    vsb.grid(column=2, row=1, rowspan=4, sticky=NS)
    tv.configure(yscrollcommand=vsb.set)
    tv['columns'] = ('a')
    tv.heading("#0", text='Item')
    tv.column('#0', anchor=W, width=225)
    tv.column('a', anchor=E, width=150)
    tv.heading('a', text="Status")
    tv.grid(column=1, row=1, rowspan=4, sticky=N)

    tv.insert('','end', text="Ecoinvent (Example version)", values=(example_ecoinvent_label,))
    tv.insert('', 'end', text="Ecoinvent (Default version)", values=(default_ecoinvent_label,))
    tv.insert('', 'end', text="Forwast", values=(forwast_label,))
    tv.insert('', 'end', text="Ecoinvent user", values=(user_label,))
    for i, v in enumerate(ECOINVENT_LIST):
        if i == 0:
            tv.insert('', 'end', text="Available Ecoinvent versions", values=(v,))
        else:
            tv.insert('', 'end', text="", values=(v,))


    #ttk.Label(mainframe,
    #          text="  Ecoinvent for example set up: {}  \n"
    #               "  Default ecoinvent version set up: {} \n"
    #               "  Forwast set up: {}  \n"
    #               "  Ecoinvent user: {}  ".format(example_ecoinvent_label,
    #                                               default_ecoinvent_label,
    #                                               forwast_label,
    #                                               user_label),
    #          foreground="#888", relief="groove").grid(column=1, row=0, rowspan=4, sticky=N)

    if not CHECK_FORWAST and not CHECK_DEFAULT_ECOINVENT and not CHECK_EXAMPLE_ECOINVENT:
        root.geometry('{}x{}+{}+{}'.format(525, 285, initial_x, initial_y))
        ttk.Label(mainframe,
                  text="WARNING - No background databases have been set up in brightway!\nTo open a model that uses ecoinvent, make sure you've\n entered your username and password in lcopt-settings\nIf you load a model that uses forwast, or load the example model, \nit may take a bit longer as the forwast database is set up",
                  foreground="#8b0000", justify=CENTER).grid(column=1, row=4, columnspan=3)
        # btn_example.state(["disabled"])
        pass

    for child in mainframe.winfo_children():
        child.grid_configure(padx=5, pady=5)

    root.mainloop()
    # root.update()
    print('bye')


if __name__ == "__main__":
    main()
