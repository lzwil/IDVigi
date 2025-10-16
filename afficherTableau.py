from tkinter import *
from tkinter import ttk
import main


def display_combobox_after_image(left_frame):

    # Create a label for the dropdown list
    sample_label = Label(left_frame, text="Discordances entre deux échantillons:")
    sample_label.grid(row=0, column=0, sticky=W, padx=20, pady=(0, 220))
    samples = main.samples.values.tolist()

    # Create the first combobox
    sample_combobox1 = ttk.Combobox(left_frame, values=samples, state="readonly")
    sample_combobox1.grid(row=0, column=0, sticky=W, padx=(250, 100), pady=(0, 220))

    # Create the second combobox
    sample_combobox2 = ttk.Combobox(left_frame, values=samples, state="readonly")
    sample_combobox2.grid(row=0, column=0, sticky=W, padx=(400, 100), pady=(0, 220))

    # Bind both comboboxes to the same event handler
    sample_combobox1.bind("<<ComboboxSelected>>",
                          lambda event, sc1=sample_combobox1, sc2=sample_combobox2, lf=left_frame:
                          on_sample_select(event, sc1, sc2, lf))
    sample_combobox2.bind("<<ComboboxSelected>>",
                          lambda event, sc1=sample_combobox1, sc2=sample_combobox2, lf=left_frame:
                          on_sample_select(event, sc1, sc2, lf))
def display_dataframe_in_text_widget(dataframe, text_widget):
    text_widget.config(state="normal")
    text_widget.delete('1.0', "end")
    text_widget.insert("end", dataframe.to_string(index=False))
    text_widget.config(state="disabled")


def on_sample_select(event, sample_combobox1, sample_combobox2, left_frame):
    selected_sample1 = sample_combobox1.get()
    selected_sample2 = sample_combobox2.get()

    # Continuer seulement si les deux samples sont sélectionnés
    if selected_sample1 and selected_sample2:
        df_unique = main.get_unique_variants_for_sample(selected_sample1, selected_sample2, main.snpxGrouped, main.mergeSnpGrouped)

        # Remove any existing text widget
        for widget in left_frame.winfo_children():
            if isinstance(widget, Text):
                widget.destroy()

        # Create and display the text widget
        text_widget = Text(left_frame)
        text_widget.place(x=274, y=80, width=250, height=140)  # Adjust the width and height as needed
        display_dataframe_in_text_widget(df_unique, text_widget)
