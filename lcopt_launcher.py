from tkinter import *
from tkinter import ttk
from tkinter import filedialog, simpledialog


if __name__ == "__main__":
	
	def create_model(*args):
		print("create")
		root.withdraw()
		model_name = simpledialog.askstring("New", "Enter a name for your model")
		if model_name:
			from lcopt import LcoptModel
			model = LcoptModel(model_name)
			model.launch_interact()
		
		root.destroy()

	def load_model(*args):
		print("load")
		root.withdraw()

		titleString = "Choose a model to open"
		filetypesList = [('Lcopt model files', '.lcopt')]
		file_path = filedialog.askopenfilename(title = titleString, filetypes = filetypesList )
		print (file_path)

		if file_path:
			from lcopt import LcoptModel
			model = LcoptModel(load = file_path)
			model.launch_interact()

		root.destroy()


	root = Tk()
	root.title("LCOPT Launcher")
	
	screen_width = root.winfo_screenwidth()
	screen_height = root.winfo_screenheight()
	initial_width = 275
	initial_height = 125
	initial_x = int(screen_width/2 - initial_width/2)
	initial_y = int(screen_height/2 - initial_height/2)

	root.geometry('{}x{}+{}+{}'.format(initial_width, initial_height, initial_x, initial_y))

	#TODO: Maybe figure out how to use a custom icon - not urgent 
	#img = PhotoImage(file = r'C:\Users\pjjoyce\Dropbox\04. REDMUD IP LCA Project\04. Modelling\lcopt\static\img\lcoptIcon2.gif')
	#root.tk.call('wm', 'iconphoto', root._w, img)
	

	mainframe = ttk.Frame(root, padding="20 20 20 20")#padding="3 3 12 12")
	mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
	mainframe.columnconfigure(0, weight=1)
	mainframe.rowconfigure(0, weight=1)



	ttk.Label(mainframe, text = "Welcome to the LCOPT Launcher").grid(column=1, row=1, columnspan=2)
	ttk.Button(mainframe, text="Create Model", command=create_model).grid(column=1, row=2, sticky=W)
	ttk.Button(mainframe, text="Open Model", command=load_model).grid(column=2, row=2, sticky=E)

	for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)




	root.mainloop()
	#root.update()
	print('bye')