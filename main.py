import pandas as pd
import numpy as np
from html2image import Html2Image as hti
import os
import sys

nom_run = ""
samples = []
snpxGrouped = pd.DataFrame()
mergeSnpGrouped = pd.DataFrame()
self_intersection_df = pd.DataFrame()
merge_output_df = pd.DataFrame()


def resource_path(relative_path):
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def creerCarteIdVigi(chemSNPx, chemMergeSNP, cutoff):
    global nom_run
    global samples
    global snpxGrouped
    global mergeSnpGrouped
    global self_intersection_df
    global merge_output_df

    # Extract run name
    prefix = "MergeSNPplex-"
    suffix = ".csv"
    nom_run = chemMergeSNP.replace(".csv", "").split("-", 1)[-1]

    mergeSNPTable = pd.read_csv(chemMergeSNP, sep=";")
    snpxTable = pd.read_csv(chemSNPx, sep=",")

    # Process mergeSNPTable
    mergeSNPTable['variant'] = mergeSNPTable["dbSNP"].apply(lambda x: x.split('https://www.ncbi.nlm.nih.gov/snp/')[-1])
    mergeSNPTable['Sample'] = mergeSNPTable['Sample'].astype(str)
    mergeSNPTable['Sample'] = mergeSNPTable['Sample'].str.extract(r'(A\d+-\d+)')[0].fillna(mergeSNPTable['Sample'])
    mergeSNPTable['Frequency'] = mergeSNPTable['Frequency'].str.replace(',', '.').astype(float)
    mergeSNPTable['Allele_passe_seuil'] = np.where(mergeSNPTable['Frequency'] >= 10, mergeSNPTable['Allele'], np.nan)

    # Trimmed mergeSNP table
    mergeSnpTrimmed = mergeSNPTable.groupby(['Sample', 'variant'])['Allele_passe_seuil'].apply(
        lambda x: ''.join(x.dropna())).reset_index()
    mergeSnpTrimmed['Variant'] = mergeSnpTrimmed['variant'] + mergeSnpTrimmed['Allele_passe_seuil']
    mergeSnpTrimmed = mergeSnpTrimmed.drop(columns=['Allele_passe_seuil', 'variant'])

    # Remove samples starting with "EAU"
    mergeSnpTrimmed = mergeSnpTrimmed[~mergeSnpTrimmed['Sample'].str.startswith('EAU')]

    # Process snpxTable: create variant column first
    snpxTable['variant'] = snpxTable['Marker Name'] + np.where(
        snpxTable['Allele 1'] == snpxTable['Allele 2'],
        snpxTable['Allele 1'],
        snpxTable['Allele 1'] + snpxTable['Allele 2']
    )

    # Trimmed SNPx table
    snpxTrimmed = pd.DataFrame({
        'Sample': snpxTable['Sample Name']
            .astype(str)
            .str.extract(r'(A\d+-\d+)')[0]
            .fillna(snpxTable['Sample Name']),
        'Variant': snpxTable['variant']
    })

    # Remove samples starting with "EAU"
    snpxTrimmed = snpxTrimmed[~snpxTrimmed['Sample'].str.startswith('EAU')]

    # Sort tables
    mergeSnpTrimmed.sort_values(['Sample', 'Variant'], inplace=True)
    snpxTrimmed.sort_values(['Sample', 'Variant'], inplace=True, ignore_index=True)

    # Group by Sample
    snpxGrouped = snpxTrimmed.groupby('Sample')['Variant'].apply(set).reset_index()
    mergeSnpGrouped = mergeSnpTrimmed.groupby('Sample')['Variant'].apply(set).reset_index()

    if len(mergeSnpGrouped) > len(snpxGrouped):
        samples = mergeSnpGrouped['Sample']
    else:
        samples = snpxGrouped['Sample']

    # Compare variants
    result_data = []
    self_intersection_data = []
    risque_data = []

    for _, row_1 in snpxGrouped.iterrows():
        sample_1 = row_1['Sample']
        variants_1 = row_1['Variant']
        result_row = {'Sample_1': sample_1}

        for _, row_2 in mergeSnpGrouped.iterrows():
            sample_2 = row_2['Sample']
            variants_2 = row_2['Variant']
            intersection_count = len(variants_1.intersection(variants_2))

            result_row[sample_2] = intersection_count

            if sample_1 == sample_2:
                self_intersection_data.append({'Echantillons': sample_1, 'Concordance': intersection_count})

            if sample_1 != sample_2 and intersection_count >= cutoff:
                risque_data.append({'Echantillons': sample_1,
                                    'Risque': str(intersection_count) + " SNPs avec " + str(sample_2)})

        result_data.append(result_row)

    # Build result DataFrame
    result_df = pd.DataFrame(result_data)
    result_df.columns.values[0] = ''
    result_df.set_index(result_df.columns[0], inplace=True)
    result_df.index.name = None

    self_intersection_df = pd.DataFrame(self_intersection_data, columns=["Echantillons", "Concordance"])
    risque_data_df = pd.DataFrame(risque_data, columns=["Echantillons", "Risque"])
    risque_data_df = risque_data_df.groupby('Echantillons')['Risque'].apply(lambda x: '\n'.join(x)).reset_index()
    merge_output_df = self_intersection_df.merge(risque_data_df, on="Echantillons", how="left").fillna(" ")

    # Style for HTML output
    styled_df = result_df.style.background_gradient(cmap='YlOrRd', vmin=0, vmax=19)
    for idx, row in result_df.iterrows():
        for col in result_df.columns:
            if idx == col and row[col] >= cutoff:
                styled_df.set_properties(**{'background-color': 'green'}, subset=pd.IndexSlice[idx, col])
    styled_df.set_properties(**{'text-align': 'center'})

    styled_html = (
        f'<html><head><style>'
        f'body {{margin: 0; padding: 0; justify-content: center; align-items: center; display: flex; flex-direction: column;}} '
        f'table {{width: 80%;}} '
        f'td, th {{text-align: center; padding: 5px;}} '
        f'h2, h3 {{ text-align: center; width: 100%; margin: 0;}} '
        f'</style></head>'
        f'<body>'
        f'<table>{styled_df.to_html(index=False)}</table>'
        f'</body></html>'
    )

    output_dir = resource_path('output')
    os.makedirs(output_dir, exist_ok=True)

    html_file_path = os.path.join(output_dir, 'styled_output.html')
    with open(html_file_path, 'w') as f:
        f.write(styled_html)

    # Screenshot
    hti_instance = hti(output_path=output_dir)
    hti_instance.browser.use_new_headless = None
    hti_instance.browser.print_command = True
    hti_instance.screenshot(html_file=html_file_path, save_as='tableau_final.png', size=(3000, 3000))



def get_unique_variants_for_sample(sample_name1, sample_name2, snpxGrouped, mergeSnpGrouped):
    """
    Returns a DataFrame with two columns:
    - SNPxPLEX (variants unique in snpx)
    - NGS (variants unique in mergeSNP)
    Variants are sorted alphabetically for better alignment.
    """
    # Extract variants for each sample
    snpx_series = snpxGrouped.loc[snpxGrouped['Sample'] == sample_name1, 'Variant']
    merge_series = mergeSnpGrouped.loc[mergeSnpGrouped['Sample'] == sample_name2, 'Variant']

    snpx_variants = set(snpx_series.iloc[0]) if not snpx_series.empty else set()
    merge_variants = set(merge_series.iloc[0]) if not merge_series.empty else set()

    # Compute unique variants
    snpx_unique = sorted(snpx_variants - merge_variants)
    merge_unique = sorted(merge_variants - snpx_variants)

    # Pad shorter list so both columns have the same length
    max_len = max(len(snpx_unique), len(merge_unique))
    snpx_unique += [""] * (max_len - len(snpx_unique))
    merge_unique += [""] * (max_len - len(merge_unique))

    return pd.DataFrame({
        "SNPxPLEX": snpx_unique,
        "NGS": merge_unique
    })





def display_dataframe_in_text_widget(data, text_widget):
    """
    Affiche un DataFrame ou une liste dans un widget texte Tkinter.
    """
    text_widget.delete("1.0", "end")

    if isinstance(data, pd.DataFrame):
        if not data.empty:
            text_widget.insert("end", data.to_string(index=False))
        else:
            text_widget.insert("end", "[INFO] Aucun variant à afficher.")
    elif isinstance(data, list):
        if data:
            text_widget.insert("end", "\n".join(map(str, data)))
        else:
            text_widget.insert("end", "[INFO] Aucun variant à afficher.")
    else:
        text_widget.insert("end", "[ERREUR] Type de données inattendu.")
