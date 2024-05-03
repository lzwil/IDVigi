from tkinter import *
from tkinter import ttk
import main
import generation


def display_combobox_after_image():
    # Create a label for the dropdown list
    sample_label = Label(generation.left_frame, text="Select Sample:")
    sample_label.grid(row=0, column=0, sticky=W, padx=50, pady=(0, 270))  # Adjusted padding

    samples = main.samples  # Update with your sample names
    sample_combobox = ttk.Combobox(generation.left_frame, values=samples, state="readonly")
    sample_combobox.grid(row=0, column=0, sticky=W, padx=200, pady=(0, 270))  # Adjusted padding
    sample_combobox.bind("<<ComboboxSelected>>", on_sample_select)

def display_dataframe_in_text_widget(dataframe, text_widget):
    """
    Display the DataFrame in a Text widget.
    """
    text_widget.config(state=ttk.NORMAL)
    text_widget.delete('1.0', ttk.END)
    text_widget.insert(ttk.END, dataframe.to_string())
    text_widget.config(state=ttk.DISABLED)
def on_sample_select(event):
    selected_sample = sample_combobox.get()
    df_unique = main.get_unique_variants_for_sample(selected_sample, main.snpxGrouped, main.mergeSnpGrouped)
    # Create a new window to display the DataFrame
    dataframe_window = ttk.Toplevel(generation.window)
    dataframe_window.title("DataFrame Viewer")
    # Display the DataFrame in the new window
    display_dataframe_in_text_widget(df_unique)



