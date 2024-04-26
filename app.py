import generation
import main

def principale():
    chemSNPx = generation.file_path1
    chemMergeSNP = generation.file_path2
    main.creerCarteIdVigi(chemSNPx, chemMergeSNP)

if __name__ == "__main__":
    principale()
