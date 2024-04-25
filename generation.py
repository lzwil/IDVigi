from tkinter import *
from tkinter import filedialog

# Créer la fenêtre
window = Tk()
window.title("Générateur de tableau de corrélation")
window.geometry("720x480")
window.iconbitmap("logo.ico")
window.config(background="#bfc2c7")

# Créer la frame principale
frame = Frame(window, bg="#bfc2c7")

# Création d'image
width = 300
height = 300
image = PhotoImage(file="logo.png")
canvas = Canvas(frame, width=width, height=height, bg="#bfc2c7", bd=0, highlightthickness=0)
canvas.create_image(width/2, height/2, image=image)
canvas.grid(row=0, column=1, sticky=W)

# Créer sous-boite
left_frame = Frame(frame, bg="#bfc2c7")

#Créer titre
label_title = Label(left_frame, text="Fichier 1", font=("Helvetica", 20), bg="#bfc2c7", fg="white")
label_title.pack()

# On place la sous boite à gauche de la frame principale
left_frame.grid(row=0, column=0, sticky=W)

# Afficher la frame
frame.pack(expand=YES)

# Création d'une barre de menu
menu_bar = Menu(window)

# Créer un premier menu
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Quitter", command=window.quit)
menu_bar.add_cascade(label="Fichier", menu=file_menu)

#Configurer la fenêtre pour ajouter la barre de menu
window.config(menu=menu_bar)

def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        print("Fichier selectionné:", file_path)

select_button = Button(window, text="Select File", command=select_file)
select_button.pack(pady=20)

# Afficher la fenêtre
window.mainloop()



