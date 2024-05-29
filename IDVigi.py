from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import main
import afficherTableau
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage
from datetime import datetime
import locale
import os
import sys

df_unique = []
file_path1 = ""
file_path2 = ""
selected_sample = ""

def resource_path(relative_path):
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Function to export to pdf
def export_to_pdf(table_data, output_path):
    cutoff = int(cutoff_combobox.get())

    # Load the logo image
    logo_path = resource_path("Images/logo_ap_hm_2020_RVB.JPG")
    logo_image = Image.open(logo_path)

    # Resize the logo if needed
    max_width = 150  # Adjust as needed
    max_height = 150  # Adjust as needed
    if logo_image.width > max_width or logo_image.height > max_height:
        logo_image.thumbnail((max_width, max_height))

    # Create a ReportLabImage object for the logo
    logo_reportlab_image = ReportLabImage(logo_path, width=logo_image.width, height=logo_image.height)

    # Set up the PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []

    # Title
    title_text = "Concordance entre SNPxPlex et le résultat de NGS"
    title_style = getSampleStyleSheet()['Title']
    title_paragraph = Paragraph(title_text, title_style)

    # Create a table to position the logo and title side by side
    header_table = Table(
        [[logo_reportlab_image, title_paragraph]],
        colWidths=[logo_image.width + 10, doc.width - logo_image.width - 20]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (0, 0), 0),
        ('RIGHTPADDING', (0, 0), (0, 0), 0),
        ('TOPPADDING', (0, 0), (0, 0), 0),
        ('BOTTOMPADDING', (0, 0), (0, 0), 0),
    ]))

    # Add the header table to the elements list
    elements.append(header_table)

    # Add a spacer after the header table
    elements.append(Spacer(1, 25))  # Adjust the height as needed

    # Date
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    date_text = datetime.now().strftime("%d %B %Y")
    date_style = getSampleStyleSheet()['Normal']
    date_paragraph = Paragraph(f"Date: {date_text}", date_style)

    # Add the date to the elements list
    elements.append(date_paragraph)
    elements.append(Spacer(1, 12))

    # Sentence
    phrase_text = f"Validation des échantillons du run <b>{main.nom_run}</b> sur <b>{cutoff}</b> SNPs"
    phrase_style = getSampleStyleSheet()['Normal']
    phrase_paragraph = Paragraph(phrase_text, phrase_style)

    # Add the sentence to the elements list
    elements.append(phrase_paragraph)
    elements.append(Spacer(1, 25))

    # Convert DataFrame to a list of lists for the table
    table_data_list = [list(table_data.columns)] + [list(row) for row in table_data.itertuples(index=False)]

    # Create the table
    table = Table(table_data_list, colWidths=[2 * inch] * 3)

    # Style the table
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(table_style)

    # Style conditionel en fonction du seuil
    for row_index, row in enumerate(table_data_list[1:], start=1):
        for col_index, cell in enumerate(row):
            if col_index == 1:
                if int(cell) >= cutoff:
                    table_style.add('BACKGROUND', (col_index, row_index), (col_index, row_index), colors.green)

    # Mettre à jour le style
    table.setStyle(table_style)

    # Add the table to the elements list
    elements.append(table)

    # Resize and add the final image
    final_image_path = resource_path('tableau_final.png')
    final_image = Image.open(final_image_path)
    max_width, max_height = letter
    if final_image.width > max_width or final_image.height > max_height:
        final_image.thumbnail((max_width, max_height))

    elements.append(ReportLabImage(final_image_path, width=final_image.width, height=final_image.height))

    # Build the PDF
    doc.build(elements)

def export_pdf():
    pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                             filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
    if pdf_path:
        export_to_pdf(main.self_intersection_df, pdf_path)

# Function to update the canvas image
def update_canvas_image(image_path):
    # Load the new image
    new_image_path = resource_path('tableau_final.png')
    new_image = Image.open(new_image_path)
    # Resize the image to fit within the canvas size while preserving aspect ratio
    max_width = 1300
    max_height = 1300
    new_image.thumbnail((max_width, max_height), Image.Resampling.BICUBIC)

    tk_image = ImageTk.PhotoImage(new_image)

    # Update the canvas size to match the image size
    canvas.config(width=tk_image.width(), height=tk_image.height())

    # Update the canvas image
    canvas.delete("all")
    canvas.create_image(0, 0, anchor=NW, image=tk_image)
    canvas.image = tk_image  # Keep reference to avoid garbage collection

    # After updating canvas image, display the combobox
    afficherTableau.display_combobox_after_image(left_frame)

# Function to execute the main function
def execute_main():
    global file_path1, file_path2, df_unique
    if file_path1 and file_path2:
        cutoff = int(cutoff_combobox.get())
        main.creerCarteIdVigi(file_path1, file_path2, cutoff)
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
            cheminFichier2.grid(row=3, column=0, sticky=W, padx=(0, 0), pady=(10, 0))

# Create the window
window = Tk()
window.title("IDVigi | Générateur de matrice de concordance")
window.geometry("1920x1200")
window.config(background="#bfc2c7")

# Setting logo image
window.iconbitmap(resource_path("Images/logo.ico"))

# Create the frame
frame = Frame(window, bg="#bfc2c7")
frame.pack(fill=BOTH, expand=YES)

# Load the image
logo_image = Image.open(resource_path("Images/logo.png"))
width, height = logo_image.size
max_width, max_height = 600, 600
scale = min(max_width / width, max_height / height)
new_width = int(width * scale)
new_height = int(height * scale)
resized_logo = logo_image.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)
tk_logo = ImageTk.PhotoImage(resized_logo)

# Create canvas and display image
canvas = Canvas(frame, width=1200, height=600, bg="#bfc2c7", bd=0, highlightthickness=0)
canvas.create_image(300, 60, anchor=NW, image=tk_logo)
canvas.pack(side=RIGHT, fill=BOTH, expand=YES, padx=(20, 10), pady=(20, 10))

# Create sub-frame for labels and buttons
left_frame = Frame(frame, bg="#bfc2c7")
left_frame.pack(side=LEFT, fill=Y)

# Label
label1 = Label(left_frame, text="Fichier SNPx:", font=("Montserrat", 14), bg="#bfc2c7", fg="white")
label1.grid(row=0, column=0, sticky=W, padx=0, pady=(300, 0))  # Adjusted padding
label2 = Label(left_frame, text="Fichier MergeSNP:", font=("Montserrat", 14), bg="#bfc2c7", fg="white")
label2.grid(row=2, column=0, sticky=W, padx=0, pady=(10, 0))  # Adjusted padding

# Button to select file
select_button1 = Button(left_frame, text="Sélectionner fichier SNPx", command=lambda: select_file(1),
                        bg="#4CAF50", fg="white")
select_button1.grid(row=0, column=0, sticky=W, padx=170, pady=(300, 0))
select_button2 = Button(left_frame, text="Sélectionner fichier MergeSNP", command=lambda: select_file(2),
                        bg="#4CAF50", fg="white")
select_button2.grid(row=2, column=0, sticky=W, padx=170, pady=(12, 0))

# Label cutoff (Validation threshold)
label2 = Label(left_frame, text="Seuil de validation:", font=("Montserrat", 14), bg="#bfc2c7", fg="white")
label2.grid(row=4, column=0, sticky=W, padx=0, pady=(10, 0))  # Adjusted padding

# Button to select the cutoff
cutoff_combobox = ttk.Combobox(left_frame, values=list(range(16)), state="readonly", width=4)
cutoff_combobox.set(13)
cutoff_combobox.grid(row=4, column=0, sticky=W, padx=170, pady=(12, 0))

# Button to execute the comparison by calling the main function
execute_button = Button(left_frame, text="Comparer", command=execute_main, bg="#008CBA", fg="white")
execute_button.grid(row=5, column=0, sticky=W, padx=170, pady=(8, 0))

# Add menu
menu_bar = Menu(window)
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Quitter", command=window.quit)
menu_bar.add_cascade(label="Fichier", menu=file_menu)
menu_bar.add_command(label="Exporter en PDF", command=export_pdf)
window.config(menu=menu_bar)

window.mainloop()
