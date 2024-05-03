from tkinter import *
from tkinter import ttk
import main

def display_combobox_after_image(left_frame):
    # Create a label for the dropdown list
    sample_label = Label(left_frame, text="Select Sample:")
    sample_label.grid(row=0, column=0, sticky=W, padx=50, pady=(0, 220))  # Adjusted padding

    samples = main.samples  # Update with your sample names
    sample_combobox = ttk.Combobox(left_frame, values=samples, state="readonly")
    sample_combobox.grid(row=0, column=0, sticky=W, padx=200, pady=(0, 220))  # Adjusted padding
    sample_combobox.bind("<<ComboboxSelected>>", lambda event, lf=left_frame, sc=sample_combobox: on_sample_select(event, lf, sc))

def display_dataframe_in_text_widget(dataframe, text_widget):
    """
    Display the DataFrame in a Text widget.
    """
    text_widget.config(state="normal")
    text_widget.delete('1.0', "end")
    text_widget.insert("end", dataframe.to_string())
    text_widget.config(state="disabled")


def on_sample_select(event, left_frame, sample_combobox):
    selected_sample = sample_combobox.get()
    df_unique = main.get_unique_variants_for_sample(selected_sample, main.snpxGrouped, main.mergeSnpGrouped)

    # Remove any existing text widget
    for widget in left_frame.winfo_children():
        if isinstance(widget, Text):
            widget.destroy()

    # Create and display the text widget
    text_widget = Text(left_frame)
    text_widget.place(x=55, y=80, width=300, height=180)  # Adjust the width and height as needed
    display_dataframe_in_text_widget(df_unique, text_widget)
