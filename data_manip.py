import csv
import itertools
import tkinter as tk

off_data = 'resultats-par-niveau-dpt-t1-france-entiere.csv'

def CandidatstoCSV():
    """
        Returns the csv file with the french presidential
        elections candidates, locations inspired by La Boussole Presidentielle
        Data from data.gouv, sorted by departement and candidates

        :return: csv file to generate candidate profils on graph
    """
    with open('CandidatsPresidentll.csv', 'w', newline='') as cfile:
        writer = csv.writer(cfile)
        candNames =[]
        #First Candidate's index on the row : 18 then every 6 rows
        candIndex = 18
        #Selecting the first line to get candidates names
        f = csv.reader(open(off_data))
        for f_row in itertools.islice(f, 1,2):
            print(f_row)
            #Iterate on all rows(89) untill the end of line
            while(candIndex + 6 < 89) :
                candNames.append(f_row[candIndex])
                candIndex += 6
        print(candNames)

    #return cfile


def makeProfilsbyDEP(generationfile, votersbyDep):
    """
        Returns the csv file with 'votersbyDep' number of candidates per departement (|1000/107| considering 
        a total of a 1000 candidates)
        Data from data.gouv, sorted by departement and candidates
        :param generationfile 
        :param votersbyDep
        :return: csv file to generate candidate profils on graph
    """
    nbRowMax = 107
    with open(off_data) as csvfile:
        reader_obj = csv.DictReader(csvfile)
        with open('CandidatsPresidentll.csv', 'w', newline='') as generationfile:
            for row in reader_obj :
                print(row)
                print("\n")

                #dict() = {code departement : nom dep , votes_exprimés : XXXXXX, nomcand1(ARTHAUD) : % Voix/Exp, ...  }


    #df = pd.read_csv('resultats-par-niveau-dpt-t1-france-entiere.csv')
    #renamecolumnN = 23
    #for i in range(11*5) :
    #    df.rename( columns={renamecolumnN :'Sexe'}, inplace=True )
    #    df.rename( columns={renamecolumnN+1 :'Nom'}, inplace=True )
    #    df.rename( columns={renamecolumnN+2 :'Prénom'}, inplace=True )
    #    df.rename( columns={renamecolumnN+3 :'% Voix/Ins'}, inplace=True )
    #    df.rename( columns={renamecolumnN+4 :'% Voix/Exp'}, inplace=True )
    #    renamecolumnN = renamecolumnN + 5

    #print("\nReading the CSV file ...\n",df)

#Test
CandidatstoCSV()