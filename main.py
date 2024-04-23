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
merge_snp_trimmed = mergeSNPTable.groupby(['Sample', 'variant'])['Allele_passe_seuil'].apply(lambda x: ''.join(x.dropna())).reset_index()

#Concaténer rs et génotype dans la même colonne
merge_snp_trimmed['Variant'] = merge_snp_trimmed['variant'] + merge_snp_trimmed['Allele_passe_seuil']
merge_snp_trimmed = merge_snp_trimmed.drop(columns=['Allele_passe_seuil', 'variant'])


#Recuperation rs et genotype du snpx
snpxTable['variant'] = snpxTable['Marker Name'] + np.where(snpxTable['Allele 1'] == snpxTable['Allele 2'],
                                                       snpxTable['Allele 1'],
                                                       snpxTable['Allele 1'] + snpxTable['Allele 2'])

#Creation du nouveau tableau
snpxTrimmed = pd.DataFrame()

#Extraction du numero de sample et du rs complet
snpxTrimmed['Sample'] = snpxTable['Sample Name'].apply(lambda x: x[:x.find('-', x.find('-') + 1)])
snpxTrimmed['variant'] = snpxTable['variant']

#Ordonner les nouveaux tableaux par sample et par rs
merge_snp_trimmed.sort_values(['Sample, variant'])
snpxTrimmed.sort_values(['Sample, Variant'])

print(snpxTrimmed)
print(merge_snp_trimmed)

