import csv
import math
import random
import itertools
import tkinter as tk

off_data = 'resultats-par-niveau-dpt-t1-france-entiere.csv'
#nbRowMax = 107
#nbColMax = 89
    

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
            #Iterate on all rows(89) untill the end of line
            while(candIndex + 6 < 89) :
                #set names of candidates with an empty list which will have the postion
                candNamesPos[ f_row[candIndex] ] = []
                candIndex += 6
        print(candNamesPos)
        #---------SET APPROX VALUES OF CANDIDATES' POSITIONS----------#

        for name, coord in candNamesPos.items() :
            writer.writerow([coord[0], coord[1], name])

    return cfile,candNamesPos


def generate_voters_by_department(off_data, voters_by_dep, radius, generation_files):
    """
        Generates a csv file for each department with 'votersbyDep' number of voters' positions randomly distributed 
        around each candidate's position, determined by the percentage of votes they received in that department.
        Uses data from the 'data.gouv' website, sorted by department and candidate. The generated csv files can be 
        used to generate candidate profiles on the graph.
        
        :param off_data: declared above, csv file we are extracting from
        :param voters_by_dep: The number of voters to generate around each candidate's position.
            It represents the percentage of the vote received by a candidate in a particular department.
        :param radius: The radius of the circle around each candidate position within which voters will be generated.
        :param generation_files: a dictionary containing the file names for the generated csv files, where the keys 
            are department codes and the values are the corresponding file names.
        :return: None
    """
    # load candidate positions CandidatestoCSV()
    _,candidate_positions = CandidatestoCSV() #Just { name : [x,y] }, not the csv file
    
    # load departements and corresponding exprimés values
    Code_DEP = {row['Code du département']: int(row['Libellé du département']) for row in off_data}
    Code_exprimes = {row['Code du département']: int(row['Exprimés']) for row in off_data}
    
    # calculate the number of voters to generate for each candidate in each departement
    voters_per_candidate = {}
    for dep in off_data:
        dep_code = dep['Code du département']
        exprimes = int(dep['Exprimés'])
        for candidate, percent_vote in dep.items():
            if candidate not in ['Code du département', 'Exprimés']:
                if candidate not in voters_per_candidate:
                    voters_per_candidate[candidate] = {}
                voters_per_candidate[candidate][dep_code] = int(percent_vote / 100 * exprimes[dep_code] * voters_by_dep)
    
    # generate voters for each departement
    for dep in off_data:
        dep_code = dep['Code du département']
        voters = []
        for candidate, num_voters in voters_per_candidate.items():
            if dep_code in num_voters:
                candidate_pos = candidate_positions[candidate]
                for i in range(num_voters[dep_code]):
                    x = random.uniform(candidate_pos[0] - radius, candidate_pos[0] + radius)
                    y_range = math.sqrt(radius ** 2 - (x - candidate_pos[0]) ** 2)
                    y = random.uniform(candidate_pos[1] - y_range, candidate_pos[1] + y_range)
                    voters.append((x, y, candidate))
        random.shuffle(voters)
        with open(generation_files[dep_code], 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['x', 'y', 'candidate'])
            writer.writerows(voters)


#--------------------------------------Main--------------------------------------------------
CandidatestoCSV()