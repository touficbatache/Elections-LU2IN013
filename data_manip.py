import csv
import itertools
import tkinter as tk

off_data = 'resultats-par-niveau-dpt-t1-france-entiere.csv'

def CandidatestoCSV():
    """
        Returns the csv file with the french presidential
        elections candidates, locations inspired by La Boussole Presidentielle
        Data from data.gouv, sorted by departement and candidates

        :return: csv file to generate candidate profils on graph
    """
    with open('CandidatsPresidentll.csv', 'w', newline='') as cfile:
        writer = csv.writer(cfile)
        candNames = dict()
        #First Candidate's index on the row : 18 then every 6 rows
        candIndex = 18
        f = csv.reader(open(off_data))
        #Selecting the first line to get candidates names
        for f_row in itertools.islice(f, 1,2):
            print(f_row)
            #Iterate on all rows(89) untill the end of line
            while(candIndex + 6 < 89) :
                #set names of candidates with an empty list which will have the postion
                candNames[ f_row[candIndex] ] = []
                candIndex += 6
        
        #---------SET APPROX VALUES OF CANDIDATES' POSITIONS----------#

        for name, coord in candNames.items() :
            writer.writerow([coord[0], coord[1], name])

    return cfile,


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
    nbColMax = 89
    with open(off_data, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            department = row[0]
            # Iterate over the candidates' columns
            for i in range(18, 89, 6):
                # Extract the candidate name
                candidate = row[i]
                # Extract the percentage of voters for the candidate
                percentage = row[i+3]
                # Do something with the department, candidate, and percentage
                print(f"{department}: {candidate} - {percentage}")




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
CandidatestoCSV()