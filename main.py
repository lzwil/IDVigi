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


def resource_path(relative_path):
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def creerCarteIdVigi(chemSNPx,chemMergeSNP, cutoff):
    global nom_run
    global samples
    global snpxGrouped
    global mergeSnpGrouped
    global self_intersection_df

    # Récupérer le nom du run pour l'output pdf
    prefix = "MergeSNPplex-"
    suffix = ".csv"
    nom_run = chemMergeSNP.split(prefix)[-1][:-len(suffix)]

    mergeSNPTable = pd.read_csv(chemMergeSNP, sep=";")
    snpxTable = pd.read_csv(chemSNPx, sep=";")

    # Process mergeSNPTable
    mergeSNPTable['variant'] = mergeSNPTable["dbSNP"].apply(lambda x: x.split('https://www.ncbi.nlm.nih.gov/snp/')[-1])
    mergeSNPTable['Sample'] = mergeSNPTable['Sample'].apply(lambda x: x.split('_')[0])
    mergeSNPTable['Frequency'] = mergeSNPTable['Frequency'].str.replace(',', '.').astype(float)
    mergeSNPTable['Allele_passe_seuil'] = np.where(mergeSNPTable['Frequency'] >= 10, mergeSNPTable['Allele'], np.nan)

    mergeSnpTrimmed = mergeSNPTable.groupby(['Sample', 'variant'])['Allele_passe_seuil'].apply(
        lambda x: ''.join(x.dropna())).reset_index()
    mergeSnpTrimmed['Variant'] = mergeSnpTrimmed['variant'] + mergeSnpTrimmed['Allele_passe_seuil']
    mergeSnpTrimmed = mergeSnpTrimmed.drop(columns=['Allele_passe_seuil', 'variant'])

    # Process snpxTable
    snpxTable['variant'] = snpxTable['Marker Name'] + np.where(snpxTable['Allele 1'] == snpxTable['Allele 2'],
                                                               snpxTable['Allele 1'],
                                                               snpxTable['Allele 1'] + snpxTable['Allele 2'])
    snpxTrimmed = pd.DataFrame({
        'Sample': snpxTable['Sample Name'].apply(lambda x: x[:x.find('-', x.find('-') + 1)]),
        'Variant': snpxTable['variant']
    })


    #Ordonner les nouveaux tableaux par sample et par rs
    mergeSnpTrimmed.sort_values(['Sample', 'Variant'], inplace=True)
    snpxTrimmed.sort_values(['Sample', 'Variant'], inplace=True, ignore_index=True)

    # Grouper les variants par sample dans chaque table
    snpxGrouped = snpxTrimmed.groupby('Sample')['Variant'].apply(set).reset_index()
    mergeSnpGrouped = mergeSnpTrimmed.groupby('Sample')['Variant'].apply(set).reset_index()

    # Alimenter la liste de samples pour la fonction afficher les rs differents
    # Initialiser une liste vide pour stocker les dictionnaires
    # Liste vide pour stocker les intersections à afficher dans l'output pdf
    samples = snpxGrouped['Sample']
    result_data = []
    self_intersection_data = []


    # Comparer chaque sample de snpxGrouped avec chaque sample de mergeSnpGrouped
    for index_1, row_1 in snpxGrouped.iterrows():
        sample_1 = row_1['Sample']
        variants_1 = row_1['Variant']
        # Initialiser un dictionnaire
        result_row = {'Sample_1': sample_1}

        # Itérer sur les lignes de mergeSnpGrouped pour trouver le nombre
        # d'intersection avec le sample actuel de snpxGrouped
        for index_2, row_2 in mergeSnpGrouped.iterrows():
            sample_2 = row_2['Sample']
            variants_2 = row_2['Variant']

            # Calculer l'intersection de variants entre sample_1 and sample_2
            intersection_count = len(variants_1.intersection(variants_2))

            # Stocker le nombre d'intersection de la paire de variants
            result_row[sample_2] = intersection_count

            # Stocker la somme des intersection des mêmes échantillons pour la sortie pdf
            if sample_1 == sample_2:
                self_intersection_data.append({'Echantillons': sample_1, 'Concordance': intersection_count})
        # Ajouter au dictionnaire les intersections avec le sample de mergeSnpGrouped et tous les autres samples
        # (on ajoute un {} au dictionnaire)
        result_data.append(result_row)

    # Créer le dataframe à partir de la liste de dictionnaire
    result_df = pd.DataFrame(result_data)

    # Remove the first row (Sample_1)
    # Remove "Sample_1" from the column headers
    # Set the first column as the index
    result_df = result_df.iloc[0:]
    result_df.columns.values[0] = ''
    result_df.set_index(result_df.columns[0], inplace=True)
    result_df.index.name = None

    # Create a DataFrame for the intersection counts of the same samples for the pdf output
    self_intersection_df = pd.DataFrame(self_intersection_data, columns=["Echantillons", "Concordance"])

    # Apply the gradient of color to the dataframe
    styled_df = result_df.style.background_gradient(cmap='YlOrRd', vmin=0, vmax=19)

    # Apply green background to cells with values >= 13 (chosen cutoff) at the intersection of matching headers
    for idx, row in result_df.iterrows():
        for col in result_df.columns:
            if idx == col and row[col] >= cutoff:
                styled_df.set_properties(**{'background-color': 'green'}, subset=pd.IndexSlice[idx, col])

    # Center all numbers in the DataFrame
    styled_df.set_properties(**{'text-align': 'center'})

    # Save styled dataframe to HTML file
    styled_df.to_html('styled_output.html')

    html_path = resource_path('styled_output.html')
    # Take screenshot of HTML and save as image, adjusting height and width to include headers
    hti().screenshot(html_file=html_path, save_as='tableau_final.png')


def get_unique_variants_for_sample(sample_name1, sample_name2, snpxGrouped, mergeSnpGrouped):

    snpx_variants = snpxGrouped.loc[snpxGrouped['Sample'] == sample_name1, 'Variant'].iloc[0]
    merge_snp_variants = mergeSnpGrouped.loc[mergeSnpGrouped['Sample'] == sample_name2, 'Variant'].iloc[0]

    df_unique = pd.DataFrame({'SNPx': sorted(snpx_variants - merge_snp_variants), 'NGS': sorted(merge_snp_variants - snpx_variants)})

    return df_unique