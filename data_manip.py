import csv
import math
import random
import itertools
import tkinter as tk
from collections import OrderedDict

off_data = 'resultats-par-niveau-dpt-t1-france-entiere.csv'
webplot = 'positionsCand.csv' #Webplotdigitizer to plot candidates from la boussole presidentille's graph
#nbRowMax = 107
#nbColMax = 89


#-----------------------------------------------------------------------------------------------------------


def CandidatestoCSV(off_data, webplot):
    """
        Returns the csv file with the french presidential
        elections candidates, locations inspired by La Boussole Presidentielle
        Data from data.gouv, sorted by departement and candidates
        :param off_data: csv file with the data
        :param webplot: csv file containing coordinates for each candidate in the order of their name in candNamesPos
        :return: csv file to generate candidate profils on graph
    """
    with open('CandidatsPresidentll.csv', 'w', newline='') as cfile:
        writer = csv.writer(cfile)
        candNamesPos = OrderedDict()
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

        with open(webplot, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row, candidat in zip(reader,candNamesPos.keys()):
                # Ignore first and third columns
                # Cut the string at 4 caracters
                str_x = row[1]
                str_x = str_x.replace(",", ".")

                str_y = row[3]
                str_y = str_y.replace(",", ".")

                x = float(str_x[:4])
                y = float(str_y[:4])

                candNamesPos[candidat].append(x)
                candNamesPos[candidat].append(y)
       
        for name, coord in candNamesPos.items() :
            writer.writerow([coord[0], coord[1], name])

    return cfile,candNamesPos


#-----------------------------------------------------------------------------------------------------------


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


#-----------------------------------------------------------------------------------------------------------


def shift_voters(from_dep, to_cand, from_cand, voters_by_dep, radius, generation_files):
    """
    Shifts a percentage of voters from one candidate to another within a specific department, and updates the corresponding
    CSV file containing the voters' positions.

    :param from_dep: The department code where the voters are being shifted from.
    :param to_cand: The name of the candidate that will receive the shifted voters.
    :param from_cand: The name of the candidate that the voters are being shifted from.
    :param voters_by_dep: The number of voters to generate around each candidate's position.
        It represents the percentage of the vote received by a candidate in a particular department.
    :param radius: The radius of the circle around each candidate position within which voters will be generated.
    :param generation_files: a dictionary containing the file names for the generated csv files, where the keys
        are department codes and the values are the corresponding file names.
    :return: None
    """

    _,candidate_positions = CandidatestoCSV() #Just { name : [x,y] }, not the csv file

    # load departements and corresponding exprimés values
    Code_DEP = {row['Code du département']: int(row['Libellé du département']) for row in off_data}
    Code_exprimes = {row['Code du département']: int(row['Exprimés']) for row in off_data}

    # calculate the number of voters to generate for each candidate in the specified departement
    voters_per_candidate = {}
    for dep in off_data:
        dep_code = dep['Code du département']
        if dep_code == from_dep:
            exprimes = int(dep['Exprimés'])
            for candidate, percent_vote in dep.items():
                if candidate not in ['Code du département', 'Exprimés']:
                    if candidate == from_cand:
                        voters_per_candidate[candidate] = {dep_code: 0}  # Don't generate voters for this candidate
                    elif candidate == to_cand:
                        voters_per_candidate[candidate] = {dep_code: int(percent_vote / 100 * exprimes * voters_by_dep)}
                    else:
                        voters_per_candidate[candidate] = {dep_code: int(percent_vote / 100 * exprimes)}
    # generate voters for the specified departement
    voters = []
    for candidate, num_voters in voters_per_candidate.items():
        if from_dep in num_voters:
            candidate_pos = candidate_positions[candidate]
            for i in range(num_voters[from_dep]):
                x = random.uniform(candidate_pos[0] - radius, candidate_pos[0] + radius)
                y_range = math.sqrt(radius ** 2 - (x - candidate_pos[0]) ** 2)
                y = random.uniform(candidate_pos[1] - y_range, candidate_pos[1] + y_range)
                voters.append((x, y, candidate))
    random.shuffle(voters)

    # update the corresponding CSV file containing the voters' positions
    with open(generation_files[from_dep], 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([x, y, candidate])
        writer.writerows(voters)




#------------------------------------------------Main-------------------------------------------------------
CandidatestoCSV(off_data, webplot)
#shift_voters('75', 'LASSALLE', 'ARTHAUD', 1, 0.01, {'75': 'voters75.csv'})