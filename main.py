import pandas as pd
import numpy as np


chemSNPx = "C:/Users/leozw/PycharmProjects/IDVigi/snpxplex_genotype_2024__04__12__154034-cloud.csv"
chemMergeSNP = "C:/Users/leozw/PycharmProjects/IDVigi/MergeSNPplex-xx-xxx.csv"

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

#Creation du nouveau tableau
snpxTrimmed = pd.DataFrame()

#Extraction du numero de sample et du rs complet
snpxTrimmed['Sample'] = snpxTable['Sample Name'].apply(lambda x: x[:x.find('-', x.find('-') + 1)])
snpxTrimmed['Variant'] = snpxTable['variant']


#Ordonner les nouveaux tableaux par sample et par rs
mergeSnpTrimmed.sort_values(['Sample', 'Variant'], inplace=True)
snpxTrimmed.sort_values(['Sample', 'Variant'], inplace=True, ignore_index=True)
#print(mergeSnpTrimmed)


# #Concaténer Sample et rs pour réaliser la première matrice
# mergeSnpTrimmed['SampleVar'] = mergeSnpTrimmed['Sample'] + mergeSnpTrimmed['Variant']
# snpxTrimmed['SampleVar'] = snpxTrimmed['Sample'] + snpxTrimmed['Variant']
#
#
# #Créer la matrice de corrélation:
# def variant_cor(df1, df2, col1, col2):
#     # Convertir les colonnes en liste
#     list1 = df1[col1].tolist()
#     list2 = df2[col2].tolist()
#
#     # Initialiser la matrice à 0
#     matrix = [[0 for _ in range(len(list2))] for _ in range(len(list1))]
#
#     # Comparer chaque élément des listes
#     for i in range(len(list1)):
#         for j in range(len(list2)):
#             # Si les chaines de caractère sont les mêmes, élément de la matrice = 1
#             if list1[i] == list2[j]:
#                 matrix[i][j] = 1
#
#     # Définir le header de la matrice
#     headers1 = df1[col1].tolist()
#     headers2 = df2[col2].tolist()
#
#     return matrix, headers1, headers2
#
# #Application de la fonction
# cor_matrix, headers1, headers2 = variant_cor(mergeSnpTrimmed, snpxTrimmed, 'SampleVar', 'SampleVar')
#
# # Afficher le header
# print("\t", end="")
# for header in headers2:
#     print(header, end="\t")
# print()
#
# # Afficher la matrice
# for i in range(len(cor_matrix)):
#     print(headers1[i], end="\t")
#     for j in range(len(cor_matrix[i])):
#         print(cor_matrix[i][j], end="\t")
#     print()
#
# dataframeMatrix = pd.DataFrame(cor_matrix)
# print(dataframeMatrix)
# corr = dataframeMatrix.corr()
# sns.heatmap(corr, cmap='coolwarm', annot=True, linewidths=0.9)
# plt.show()

# Group variants by sample in each table
snpxGrouped = snpxTrimmed.groupby('Sample')['Variant'].apply(set).reset_index()
mergeSnpGrouped = mergeSnpTrimmed.groupby('Sample')['Variant'].apply(set).reset_index()

# Initialize an empty list to store the dictionaries
result_data = []

# Compare each sample in snpxGrouped with each sample in mergeSnpGrouped
for index_1, row_1 in snpxGrouped.iterrows():
    sample_1 = row_1['Sample']
    variants_1 = row_1['Variant']

    # Initialize a dictionary to store intersection counts for current sample pair
    result_row = {'Sample_1': sample_1}

    # Iterate over rows of mergeSnpGrouped to find intersections with the current sample
    for index_2, row_2 in mergeSnpGrouped.iterrows():
        sample_2 = row_2['Sample']
        variants_2 = row_2['Variant']

        # Calculate the intersection of variants between sample_1 and sample_2
        intersection_count = len(variants_1.intersection(variants_2))

        # Store the intersection count for the current sample pair
        result_row[sample_2] = intersection_count

    # Append the dictionary for the current sample pair to the list
    result_data.append(result_row)

# Create the DataFrame using pd.DataFrame()
result_df = pd.DataFrame(result_data)

# Apply background gradient styling directly to the DataFrame
styled_df = result_df.style.background_gradient()

# Render the styled DataFrame as HTML and save it to a file
html = styled_df.to_html("styled_table.html", index=False)
