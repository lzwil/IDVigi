# imports

import pandas as pd

# import du fichier de SNPxplex
chemSNPx = "C:/Users/leozw/PycharmProjects/IDVigi/MergeSNPplex-xx-xxx.csv"
chemMergeSNP = "C:/Users/leozw/PycharmProjects/IDVigi/snpxplex_genotype_2024__04__12__154034-cloud.csv"

snpxTable = pd.read_csv(chemSNPx, sep=";")
mergeTable = pd.read_csv(chemMergeSNP, sep=";")

#Creation du nouveau tableau
snpxTrimmed = pd.DataFrame(snpxTable['Sample'])

#Extraction du numero de sample
snpxTrimmed['Sample'] = snpxTrimmed['Sample'].apply(lambda x: x.split('_')[0])
print(snpxTrimmed.head())

#Extraction du rs et du génotype

