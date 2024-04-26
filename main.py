import pandas as pd
import numpy as np

def creerCarteIdVigi(chemSNPx,chemMergeSNP):

    mergeSNPTable = pd.read_csv(chemMergeSNP, sep=";")
    snpxTable = pd.read_csv(chemSNPx, sep=";")


    #Recupération du rs de mergeSNP
    mergeSNPTable['variant'] = mergeSNPTable["dbSNP"].apply(lambda x: x.split('https://www.ncbi.nlm.nih.gov/snp/')[-1])
    mergeSNPTable['Sample'] = mergeSNPTable['Sample'].apply(lambda x: x.split('_')[0])

    #Convertir la fréquence en float
    mergeSNPTable['Frequency'] = mergeSNPTable['Frequency'].str.replace(',', '.').astype(float)

    #Ajouter une colonne avec les alleles retenus
    mergeSNPTable['Allele_passe_seuil'] = np.where(mergeSNPTable['Frequency'] >= 10,
                                                   mergeSNPTable['Allele'],
                                                   np.nan)

    #Grouper par sample et variant et concaténer les valeurs de Allele_passe_seuil
    mergeSnpTrimmed = mergeSNPTable.groupby(['Sample', 'variant'])['Allele_passe_seuil'].apply(lambda x: ''.join(x.dropna())
                                                                                               ).reset_index()

    #Concaténer rs et génotype dans la même colonne
    mergeSnpTrimmed['Variant'] = mergeSnpTrimmed['variant'] + mergeSnpTrimmed['Allele_passe_seuil']
    mergeSnpTrimmed = mergeSnpTrimmed.drop(columns=['Allele_passe_seuil', 'variant'])


    #Recuperation rs et genotype du snpx
    snpxTable['variant'] = snpxTable['Marker Name'] + np.where(snpxTable['Allele 1'] == snpxTable['Allele 2'],
                                                           snpxTable['Allele 1'],
                                                           snpxTable['Allele 1'] + snpxTable['Allele 2'])

    #Creation du nouveau tableau snpx
    snpxTrimmed = pd.DataFrame()

    #Extraction du numero de sample et du rs complet
    snpxTrimmed['Sample'] = snpxTable['Sample Name'].apply(lambda x: x[:x.find('-', x.find('-') + 1)])
    snpxTrimmed['Variant'] = snpxTable['variant']


    #Ordonner les nouveaux tableaux par sample et par rs
    mergeSnpTrimmed.sort_values(['Sample', 'Variant'], inplace=True)
    snpxTrimmed.sort_values(['Sample', 'Variant'], inplace=True, ignore_index=True)


    # Grouper les variants par sample dans chaque table
    snpxGrouped = snpxTrimmed.groupby('Sample')['Variant'].apply(set).reset_index()
    mergeSnpGrouped = mergeSnpTrimmed.groupby('Sample')['Variant'].apply(set).reset_index()

    # Initialiser une liste vide pour stocker les dictionnaires
    result_data = []

    # Comparer chaque sample de snpxGrouped avec chaque sample de mergeSnpGrouped
    for index_1, row_1 in snpxGrouped.iterrows():
        sample_1 = row_1['Sample']
        variants_1 = row_1['Variant']
        # Initialiser un dictionnaire
        result_row = {'Sample_1': sample_1}

        # Itérer sur les lignes de mergeSnpGrouped pour trouver le nombre d'intersection avec le sample actuel de snpxGrouped
        for index_2, row_2 in mergeSnpGrouped.iterrows():
            sample_2 = row_2['Sample']
            variants_2 = row_2['Variant']

            # Calculer l'intersection de variants entre sample_1 and sample_2
            intersection_count = len(variants_1.intersection(variants_2))

            # Stocker le nombre d'intersection de la paire de variants
            result_row[sample_2] = intersection_count

        # Ajouter au dictionnaire les intersections avec le sample de mergeSnpGrouped et tous les autres samples (on ajoute un {} au dictionnaire)
        result_data.append(result_row)

    # Créer le dataframe à partir de la liste de dictionnaire
    result_df = pd.DataFrame(result_data)
    print(result_df)

    # Appliquer le gradient de couleur au tableau
    styled_df = result_df.style.background_gradient()

    # Render the styled DataFrame as HTML and save it to a file
    html = styled_df.to_html("styled_table.html", index=False)
