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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage, PageBreak
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
    max_width = 150
    max_height = 150
    if logo_image.width > max_width or logo_image.height > max_height:
        logo_image.thumbnail((max_width, max_height))

    logo_reportlab_image = ReportLabImage(logo_path, width=logo_image.width, height=logo_image.height)

    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []

    # Paragraphs séparés pour le titre et le sous-titre
    title_paragraph = Paragraph(
        "Validation technique de l'identitovigilance",
        getSampleStyleSheet()['Title']
    )
    title_paragraph.style.alignment = 1  # centrer

    subtitle_paragraph = Paragraph(
        "Comparaison entre SNPxPlex et le résultat de NGS",
        getSampleStyleSheet()['BodyText']
    )
    subtitle_paragraph.style.fontSize = 12  # taille un peu plus petite
    subtitle_paragraph.style.alignment = 1  # centrer

    # Inclure les deux Paragraphs dans le header avec le logo
    header_table = Table(
        [[logo_reportlab_image, [title_paragraph, subtitle_paragraph]]],
        colWidths=[logo_image.width + 10, doc.width - logo_image.width - 20]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (0, 0), 0),
        ('RIGHTPADDING', (0, 0), (0, 0), 0),
        ('TOPPADDING', (0, 0), (0, 0), 0),
        ('BOTTOMPADDING', (0, 0), (0, 0), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 25))

    # Date
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    date_text = datetime.now().strftime("%d %B %Y")
    date_paragraph = Paragraph(f"Date: {date_text}", getSampleStyleSheet()['Normal'])
    elements.append(date_paragraph)
    elements.append(Spacer(1, 12))

    phrase_text = f"Validation des échantillons du run <b>{main.nom_run}</b> sur <b>{cutoff}</b> SNPs"
    phrase_paragraph = Paragraph(phrase_text, getSampleStyleSheet()['Normal'])
    elements.append(phrase_paragraph)
    elements.append(Spacer(1, 25))

    # Table
    table_data_list = [list(table_data.columns)] + [list(row) for row in table_data.itertuples(index=False)]
    table = Table(table_data_list, colWidths=[2 * inch] * len(table_data_list[0]))
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

    for row_index, row in enumerate(table_data_list[1:], start=1):
        for col_index, cell in enumerate(row):
            if col_index == 1:
                if int(cell) >= cutoff:
                    table_style.add('BACKGROUND', (col_index, row_index), (col_index, row_index), colors.green)
                if int(cell) < cutoff:
                    table_style.add('BACKGROUND', (col_index, row_index), (col_index, row_index), colors.firebrick)
    table.setStyle(table_style)
    elements.append(table)
    elements.append(PageBreak())

    # Image finale
    output_dir = resource_path('output')
    final_image_path = os.path.join(output_dir, "tableau_final.png")
    final_image = Image.open(final_image_path)
    max_width, max_height = letter[0] - 100, letter[1] - 200
    if final_image.width > max_width or final_image.height > max_height:
        final_image.thumbnail((max_width, max_height))
    centered_image = ReportLabImage(final_image_path, width=final_image.width, height=final_image.height)

    legends_and_image_table = Table(
        [[Paragraph("", getSampleStyleSheet()['BodyText'])], [centered_image]],
        colWidths=[final_image.width],
        rowHeights=[20, final_image.height]
    )
    legends_and_image_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('VALIGN', (0, 0), (0, 0), 'TOP'),
        ('ALIGN', (0, 1), (0, 1), 'CENTER'),
        ('VALIGN', (0, 1), (0, 1), 'MIDDLE'),
    ]))
    elements.append(legends_and_image_table)

    doc.build(elements)

def export_pdf():
    pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                             filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
    if pdf_path:
        export_to_pdf(main.merge_output_df, pdf_path)

# Function to update the canvas image with scrollbars
def update_canvas_image(image_path):
    output_dir = resource_path('output')
    new_image_path = os.path.join(output_dir, image_path)
    new_image = Image.open(new_image_path)

    # Get canvas size
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()

    if canvas_width == 1 and canvas_height == 1:
        # Canvas not yet rendered, force update
        window.update_idletasks()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

    # Scale image proportionally to fit canvas
    scale = min(canvas_width / new_image.width, canvas_height / new_image.height, 1.0)
    new_width = int(new_image.width * scale)
    new_height = int(new_image.height * scale)

    resized_image = new_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    tk_image = ImageTk.PhotoImage(resized_image)

    canvas.delete("all")
    canvas.create_image(0, 0, anchor=NW, image=tk_image)
    canvas.image = tk_image  # keep reference

    # Update scroll region (for panning if image is larger)
    canvas.config(scrollregion=(0, 0, new_width, new_height))

    # Show comboboxes after image
    afficherTableau.display_combobox_after_image(left_frame)


def execute_main():
    global file_path1, file_path2, df_unique
    if file_path1 and file_path2:
        cutoff = int(cutoff_combobox.get())
        main.creerCarteIdVigi(file_path1, file_path2, cutoff)
        update_canvas_image("tableau_final.png")
    else:
        print("Veuillez sélectionner les fichiers SNPx et MergeSNP.")

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

# Window
window = Tk()
window.title("IDVigi | Générateur de matrice de concordance")
window.geometry("1920x1200")
window.config(background="#bfc2c7")
window.iconbitmap(resource_path("Images/logo.ico"))

frame = Frame(window, bg="#bfc2c7")
frame.pack(fill=BOTH, expand=YES)

# Logo (à gauche par défaut)
logo_image = Image.open(resource_path("Images/logo.png"))
width, height = logo_image.size
max_width, max_height = 600, 600
scale = min(max_width / width, max_height / height)
new_width = int(width * scale)
new_height = int(height * scale)
resized_logo = logo_image.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)
tk_logo = ImageTk.PhotoImage(resized_logo)

# Canvas + scrollbars
canvas = Canvas(frame, bg="#bfc2c7", bd=0, highlightthickness=0)
scroll_x = Scrollbar(frame, orient="horizontal", command=canvas.xview)
scroll_y = Scrollbar(frame, orient="vertical", command=canvas.yview)
canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

canvas.pack(side=RIGHT, fill=BOTH, expand=YES, padx=(20, 10), pady=(20, 10))
scroll_x.pack(side=BOTTOM, fill=X)
scroll_y.pack(side=RIGHT, fill=Y)

# Affiche logo par défaut
canvas.create_image(300, 60, anchor=NW, image=tk_logo)

# Left frame
left_frame = Frame(frame, bg="#bfc2c7")
left_frame.pack(side=LEFT, fill=Y)

label1 = Label(left_frame, text="Fichier SNPxPlex:", font=("Montserrat", 14), bg="#bfc2c7", fg="white")
label1.grid(row=0, column=0, sticky=W, padx=0, pady=(300, 0))
label2 = Label(left_frame, text="Fichier NGS:", font=("Montserrat", 14), bg="#bfc2c7", fg="white")
label2.grid(row=2, column=0, sticky=W, padx=0, pady=(10, 0))

select_button1 = Button(left_frame, text="Sélectionner fichier SNPxPlex", command=lambda: select_file(1),
                        bg="#4CAF50", fg="white")
select_button1.grid(row=0, column=0, sticky=W, padx=170, pady=(300, 0))
select_button2 = Button(left_frame, text="Sélectionner fichier NGS", command=lambda: select_file(2),
                        bg="#4CAF50", fg="white")
select_button2.grid(row=2, column=0, sticky=W, padx=170, pady=(12, 0))

label2 = Label(left_frame, text="Seuil de validation:", font=("Montserrat", 14), bg="#bfc2c7", fg="white")
label2.grid(row=4, column=0, sticky=W, padx=0, pady=(10, 0))

cutoff_combobox = ttk.Combobox(left_frame, values=list(range(16)), state="readonly", width=4)
cutoff_combobox.set(13)
cutoff_combobox.grid(row=4, column=0, sticky=W, padx=170, pady=(12, 0))

execute_button = Button(left_frame, text="Comparer", command=execute_main, bg="#008CBA", fg="white")
execute_button.grid(row=5, column=0, sticky=W, padx=170, pady=(8, 0))

menu_bar = Menu(window)
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Quitter", command=window.quit)
menu_bar.add_cascade(label="Fichier", menu=file_menu)
menu_bar.add_command(label="Exporter en PDF", command=export_pdf)
window.config(menu=menu_bar)

window.mainloop()
