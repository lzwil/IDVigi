# imports

import pandas as pd

# import du fichier de SNPxplex
chemSNPx = "C:/Users/leozw/PycharmProjects/IDVigi/snpxplex_genotype_2024__04__12__154034-cloud.csv"

snpxTable = pd.read_csv(chemSNPx, sep=";")

#Creation du nouveau tableau
snpxTrimmed = pd.DataFrame()

#Extraction du numero de sample et du rs
snpxTrimmed['Sample'] = snpxTable['Sample Name'].apply(lambda x: x[:x.find('-', x.find('-') + 1)])
snpxTrimmed['variant'] = snpxTable['Marker Name']
snpxTrimmed.sort_values(by=['Sample'])
print(snpxTrimmed.head())


