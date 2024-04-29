from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
from html2image import Html2Image
import main


file_path1 = ""
file_path2 = ""
# Function to update the canvas image
def update_canvas_image(image_path):
    # Load the new image
    new_image = Image.open("C:/Users/leozw/PycharmProjects/IDVigi/tableau_final.png")
    tk_image = ImageTk.PhotoImage(new_image)

    # Update the canvas size to match the image size
    canvas.config(width=tk_image.width(), height=tk_image.height())

    # Update the canvas image
    canvas.delete("all")
    canvas.create_image(0, 0, anchor=NW, image=tk_image)
    canvas.image = tk_image  # Keep reference to avoid garbage collection

# Function to execute the main function
def execute_main():
    global file_path1, file_path2
    if file_path1 and file_path2:
        main.creerCarteIdVigi(file_path1, file_path2)
        update_canvas_image("tableau_final.png")
    else:
        print("Veuillez sélectionner les fichiers SNPx et MergeSNP.")

# Function to select file
def select_file(file_number):
    global file_path1, file_path2
    if file_number == 1:
        file_path1 = filedialog.askopenfilename()
        if file_path1:
            cheminFichier1 = Label(left_frame, text=file_path1, font=("Montserrat", 9),
                                   bg="#bfc2c7", fg="white")
            cheminFichier1.grid(row=1, column=0, sticky=W, padx=(0, 10), pady=(10, 0))
    else:
        file_path2 = filedialog.askopenfilename()
        if file_path2:
            cheminFichier2 = Label(left_frame, text=file_path2, font=("Montserrat", 9),
                                   bg="#bfc2c7", fg="white")
            cheminFichier2.grid(row=3, column=0, sticky=W, padx=(0, 0), pady=(10, 0))  # Adjusted padding


# Create the window
window = Tk()
window.title("Générateur de tableau de corrélation")
window.geometry("1080x720")
window.config(background="#bfc2c7")
window.iconbitmap('logo.ico')

# Create the frame
frame = Frame(window, bg="#bfc2c7")
frame.pack(fill=BOTH, expand=YES)

# Load the image
logo_image = Image.open("logo.png")
width, height = logo_image.size
max_width, max_height = 600, 600  # Enlarged width and height of the canvas
scale = min(max_width / width, max_height / height)
new_width = int(width * scale)
new_height = int(height * scale)
resized_logo = logo_image.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)
tk_logo = ImageTk.PhotoImage(resized_logo)

# Create sub-frame for labels and buttons
left_frame = Frame(frame, bg="#bfc2c7")
left_frame.pack(side=LEFT, fill=Y)

#Label
label1 = Label(left_frame, text="Fichier SNPx:", font=("Montserrat", 14), bg="#bfc2c7", fg="white")
label1.grid(row=0, column=0, sticky=W, padx=(0), pady=(300, 0))  # Adjusted padding
label2 = Label(left_frame, text="Fichier MergeSNP:", font=("Montserrat", 14), bg="#bfc2c7", fg="white")
label2.grid(row=2, column=0, sticky=W, padx=(0), pady=(10, 0))  # Adjusted padding

# Button to select file
select_button1 = Button(left_frame, text="Sélectionner fichier SNPx", command=lambda: select_file(1),
                        bg="#4CAF50", fg="white")
select_button1.grid(row=0, column=0, sticky=W, padx=170, pady=(300, 0))  # Adjusted padding


select_button2 = Button(left_frame, text="Sélectionner fichier MergeSNP", command=lambda: select_file(2),
                        bg="#4CAF50", fg="white")
select_button2.grid(row=2, column=0, sticky=W, padx=170, pady=(8, 0))  # Adjusted padding

# Bouton pour exécuter la comparaison
execute_button = Button(left_frame, text="Comparer", command=execute_main, bg="#008CBA", fg="white")
execute_button.grid(row=4, column=0, sticky=W, padx=170, pady=(8, 0))  # Adjusted padding

# Create canvas and display image
canvas = Canvas(frame, width=new_width, height=new_height, bg="#bfc2c7", bd=0, highlightthickness=0)
canvas.create_image(0, 0, anchor=NW, image=tk_logo)
canvas.pack(side=RIGHT, fill=BOTH, expand=YES, padx=(20, 10), pady=(20, 10))  # Adjusted padding

# Add menu
menu_bar = Menu(window)
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Quitter", command=window.quit)
menu_bar.add_cascade(label="Fichier", menu=file_menu)
window.config(menu=menu_bar)

hti = Html2Image()
hti.screenshot(html_file="styled_output.html", save_as='tableau_final.png', size=(2000, 1000))

# Display window
window.mainloop()