#import MergeSNP table

import pandas as pd

chemMergeSNP = "C:/Users/leozw/PycharmProjects/IDVigi/MergeSNPplex-xx-xxx.csv"
mergeSNP = pd.read_csv(chemMergeSNP, sep=";")

#Creation du nouveau tableau
mergeSNPTrimmed = pd.DataFrame()

mergeSNPTrimmed['Sample'] = mergeSNP['Sample'].apply(lambda x: x.split('_')[0])
print(mergeSNPTrimmed.head())

