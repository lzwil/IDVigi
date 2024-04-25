from tkinter import *

# Créer une fenêtre
window = Tk()

# Personnaliser la fenêtre
window.title("IDVigi")
window.geometry("1080x720")
window.minsize(480, 360)
window.iconbitmap("logo.ico")
window.config(background="#bfc2c7")

# Ajouter texte
label_title = Label(window, text="IDVigi", font=("Courrier", 40))
label_title.pack()

# Creer frame pour le tableau
frame = Frame(window, bg='#bfc2c7', bd=1, relief=SUNKEN)
frame.pack(expand=YES)
frame.grid(row=5, column=5, sticky=W)




# Afficher la fenêtre
window.mainloop()


