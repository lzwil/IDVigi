# imports

import pandas as pd

# import du fichier de SNPxplex
chemFichier = "C:/Users/leozw/PycharmProjects/IDVigi/MergeSNPplex-xx-xxx.csv"

snpxTable = pd.read_csv(chemFichier, sep = ";")

print(snpxTable.head())