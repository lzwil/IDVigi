import pandas as pd


chemSNPx = "C:/Users/leozw/PycharmProjects/IDVigi/snpxplex_genotype_2024__04__12__154034-cloud.csv"
chemMergeSNP = "C:/Users/leozw/PycharmProjects/IDVigi/MergeSNPplex-xx-xxx.csv"

mergeSNPTable = pd.read_csv(chemMergeSNP, sep=";")
snpxTable = pd.read_csv(chemSNPx, sep=";")

#Recupération du rs de mergeSNP
mergeSNPTable['variant'] = mergeSNPTable["dbSNP"].apply(lambda x: x.split('https://www.ncbi.nlm.nih.gov/snp/')[-1])

#Creation du nouveau tableau
snpxTrimmed = pd.DataFrame()
mergeSNPTrimmed = pd.DataFrame()

#Extraction du numero de sample et du rs
snpxTrimmed['Sample'] = snpxTable['Sample Name'].apply(lambda x: x[:x.find('-', x.find('-') + 1)])
snpxTrimmed['variant'] = snpxTable['Marker Name']
snpxTrimmed.sort_values(by=['Sample'])


mergeSNPTrimmed['Sample'] = mergeSNPTable['Sample'].apply(lambda x: x.split('_')[0])
mergeSNPTrimmed['variant'] = mergeSNPTable['variant']
print(snpxTrimmed.head())
print(mergeSNPTrimmed)
