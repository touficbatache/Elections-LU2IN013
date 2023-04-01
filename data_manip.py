import csv
import random
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
        candNamesPos = dict()
        #First Candidate's index on the row : 18 then every 6 rows
        candIndex = 18
        f = csv.reader(open(off_data))
        #Selecting the first line to get candidates names
        for f_row in itertools.islice(f, 1,2):
            print(f_row)
            #Iterate on all rows(89) untill the end of line
            while(candIndex + 6 < 89) :
                #set names of candidates with an empty list which will have the postion
                candNamesPos[ f_row[candIndex] ] = []
                candIndex += 6
        
        #---------SET APPROX VALUES OF CANDIDATES' POSITIONS----------#

        for name, coord in candNamesPos.items() :
            writer.writerow([coord[0], coord[1], name])

    return cfile,candNamesPos


def makeProfilsbyDEP(generationfile, votersbyDep):
    """
        Returns the csv file with 'votersbyDep' number of candidates per departement (|1000/107| considering 
        a total of a 1000 candidates)
        Data from data.gouv, sorted by departement and candidates
        :param generationfile
        :param votersbyDep
        :return: csv file to generate candidate profils on graph
    """
    #Dict like {name : [x,y]}
    _ ,candNamesPos = CandidatestoCSV()

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
    

    #----------------------------------------------------------------------------------
    #Load voting percentages for each candidate by department from CSV file
    dept_votes = {}
    with open('resultats-par-niveau-dpt-t1-france-entiere.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        next(reader)
        for row in reader:
            deptcode = row['Code du département']
            if deptcode not in dept_votes:
                dept_votes[deptcode] = []
            for name in candNamesPos.keys() :
                cand = name
                pct = float(row[f'% Voix/Exp Candidat {i}'].replace(',', '.'))
                dept_votes[deptcode].append((cand, pct))

    # Generate voter positions for each department
    writer = csv.writer(generationfile)
    for dept, votes in dept_votes.items():
        for i in range(votersbyDep):
            total_votes = sum(pct for _, pct in votes)

            # randomly select candidate based on vote percentage
            candidate = random.choices(votes, [pct/total_votes for _, pct in votes])[0][0] 
            # use candidate's x and y position
            x, y = candidates[candidate - 1]  
            # add random noise to x and y positions
            x += random.uniform(-0.05, 0.05)  
            y += random.uniform(-0.05, 0.05)
            writer.writerow([x, y, dept, candidate])


    return generationfile


#--------------------------------------Main--------------------------------------------------
CandidatestoCSV()