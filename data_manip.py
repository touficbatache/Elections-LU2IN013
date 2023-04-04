import csv
import math
import random
import itertools
import tkinter as tk
from collections import OrderedDict

off_data = 'resultats-par-niveau-dpt-t1-france-entiere.csv'
#nbRowMax = 107
#nbColMax = 89

webplot = 'positionsCand.csv' #Webplotdigitizer to plot candidates from la boussole presidentille's graph



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

        #---------SET APPROX VALUES OF CANDIDATES' POSITIONS----------#

        with open(webplot, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row, candidat in zip(reader,candNamesPos.keys()):
                # Ignore first and third columns
                # Cut the string at 4 caracters
                str_x = row[0] + "." + row[1][:2].replace(",", "")

                str_y = row[2] + "." + row[3][:2].replace(",", "")
                
                x = float(str_x[:4])
                y = float(str_y[:4])

                candNamesPos[candidat].append(x/2)
                candNamesPos[candidat].append(y/2)
       
        for name, coord in candNamesPos.items() :
            writer.writerow([coord[0], coord[1], name])

    return cfile,candNamesPos


#-----------------------------------------------------------------------------------------------------------


def generate_voters_by_department(off_data, webplot, scaledown, radius, generation_files):
    """
        Generates a csv file for each department with the coordinates of a certain number of voters. 
        In each departement, each candidate will generate voters with positions x and y within a radius of the candidate's positon.
        Uses data from the 'data.gouv' website, sorted by department and candidate. The generated csv files can be 
        used to generate candidate profiles on the graph.
        
        :param off_data: declared above, csv file we are extracting from
        :param webplot: csv file containing coordinates for each candidate in the order of their name in candNamesPos
        :param scaledown: max number of voters for the whole country
        :param radius: The radius of the circle around each candidate position within which voters will be generated.
        :param generation_files: a dictionary containing the file names for the generated csv files, where the keys 
            are department codes and the values are the corresponding file names. Needs to be initialized.
        :return: None
    """
    generation_files = {}

    # load candidate positions with CandidatestoCSV()
    _,candidate_positions = CandidatestoCSV(off_data, webplot) #Just the dict { name : [x,y] }, not the csv file

    #Total votes "exprimés"
    total_exp = 0 

    exp_per_dpt = OrderedDict() # {'1':68869, ... , 'ZZ':6543}
    code_name_dpt = OrderedDict() # {'1':'Ain', ..., 'ZZ':'Français établis hors de France'}

    with open(off_data, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            total_exp += int(row[14])
            #exp_per_dpt[row[0]] = int(row[14])
            #code_name_dpt[row[0]] = row[1]

    # Read in the election results from the CSV file
    with open(off_data, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)

        # Initialize the voters_per_candidate dictionary
        voters_per_candidate = {}

        # Loop over each department in data
        for row in reader:
            # Define the number of voters by department
            voters_by_dep = int(row[14])/total_exp
            dep_code = row[0]
            dep_name = row[1]
            expr_dep = int(row[14])
            exp_dep_simul = scaledown*expr_dep/total_exp
            
            # Loop over each candidate in the department
            Vo_per_Exp = 0.0

            for index, roww in enumerate(row):
                for candidate in list(candidate_positions.keys()):
                    if candidate in roww:
                        Vo_per_Exp = float(row[index + 4].replace(",", ".")) # '%Voix/exp'
                        break
                    if candidate not in voters_per_candidate:
                        voters_per_candidate[candidate] = {}
                    voters_per_candidate[candidate][dep_code] = math.ceil(exp_dep_simul*Vo_per_Exp)


            # generate voters for each departement
        
            voters = []
            for candidate, num_voters in voters_per_candidate.items():
                if dep_code in num_voters:
                    candidate_pos = candidate_positions[candidate]
                    for i in range(num_voters[dep_code]):
                        x = random.uniform(candidate_pos[0] - radius, candidate_pos[0] + radius)
                        y_range = math.sqrt(radius ** 2 - (x - candidate_pos[0]) ** 2)
                        y = random.uniform(candidate_pos[1] - y_range, candidate_pos[1] + y_range)
                        voters.append((x, y, candidate))
                        print(voters)
            random.shuffle(voters)

            filename = dep_code
            #with open(generation_files[dep_code], 'w', newline='') as f:
            #    writer = csv.writer(f)
            #    writer.writerow([x, y, candidate])
            #    writer.writerows(voters)


#-----------------------------------------------------------------------------------------------------------


def shift_voters(off_data, webplot, from_dep, to_cand, from_cand, voters_by_dep, radius):
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

    _,candidate_positions = CandidatestoCSV(off_data, webplot) #Just { name : [x,y] }, not the csv file

    # load departements and corresponding exprimés values
    #Code_DEP = {row['Code du département']: int(row['Libellé du département']) for row in off_data}
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
        print(candidate)
        if from_dep in num_voters:
            candidate_pos = candidate_positions[candidate]
            for i in range(num_voters[from_dep]):
                x = random.uniform(candidate_pos[0] - radius, candidate_pos[0] + radius)
                y_range = math.sqrt(radius ** 2 - (x - candidate_pos[0]) ** 2)
                y = random.uniform(candidate_pos[1] - y_range, candidate_pos[1] + y_range)
                voters.append((x, y, candidate))
                print(voters)
    random.shuffle(voters)

    # update the corresponding CSV file containing the voters' positions
    with open(generation_files[from_dep], 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([x, y, candidate])
        writer.writerows(voters)




#------------------------------------------------Main-------------------------------------------------------
CandidatestoCSV(off_data, webplot) #works

generate_voters_by_department(off_data,webplot, 800, 0.5)

#shift_voters('75', 'LASSALLE', 'ARTHAUD', 1, 0.01, {'75': 'voters75.csv'})