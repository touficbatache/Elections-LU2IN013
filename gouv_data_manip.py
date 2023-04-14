import os
import csv
import math
import random
import itertools
from collections import OrderedDict

off_data = 'resultats-par-niveau-dpt-t1-france-entiere.csv'
#nbRowMax = 107
#nbColMax = 89

webplot = 'candidatsPlot.csv' #Webplotdigitizer to plot candidates from la boussole presidentille's graph



#-----------------------------------------------------------------------------------------------------------


def CandidatestoCSV(off_data, webplot):
    """
        Returns the csv file with the french presidential
        elections candidates, locations inspired by La Boussole Presidentielle
        Data from data.gouv, sorted by departement and candidates
        :param off_data: csv file with the data
        :param webplot: csv file containing coordinates for each candidate in the order of their name in candNamesPos
        :return: csv file to generate candidate profils on graph and a dictionnary (tuple)
    """
    with open('CandidatsPresidentll.csv', 'w', newline='') as cfile:
        writer = csv.writer(cfile)
        writer.writerow(['Candidats'])

        candNamesPos = OrderedDict()
        #First Candidate's index on the row : 18 then every 6 rows
        candIndex = 18
        f = csv.reader(open(off_data))
        #Selecting the first line to get candidates names
        for f_row in itertools.islice(f, 1,2):
            #Iterate on all rows(89) untill the end of line
            while(candIndex + 6 <= 90) :
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

def generate_voters_by_department(off_data, webplot, scaledown, radius):
    """
        Generates a csv file for each department with the coordinates of a certain number of voters. 
        In each departement, each candidate will generate voters with positions x and y within a radius of the candidate's positon.
        Uses data from the 'data.gouv' website, sorted by department and candidate. The generated csv files can be 
        used to generate candidate profiles on the graph.
        
        :param off_data: declared above, csv file we are extracting from
        :param webplot: csv file containing coordinates for each candidate in the order of their name in candNamesPos
        :param scaledown: max number of voters for the whole country
        :param radius: The radius of the circle around each candidate position within which voters will be generated.
        :return: Dictionnary associating a "departement code : numbers of voters" to each candidate
    """

    # load candidate positions with CandidatestoCSV()
    _,candidate_positions = CandidatestoCSV(off_data, webplot) #Just the dict { name : [x,y] }, not the csv file

    #Total votes "exprimés"
    total_exp = 0 

    with open(off_data, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            total_exp += int(row[14])

    # Read in the election results from the CSV file
    with open(off_data, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)

        # Initialize the voters_per_candidate dictionary
        voters_per_candidate = {}

        # Loop over each department in data
        for row in reader:
            # Define the number of voters by department
            nb_votants = 0
            dep_code = row[0]
            expr_dep = int(row[14])
            expr_dep_simul = scaledown*expr_dep/total_exp
            
            # Loop over each candidate in the department
            for index, roww in enumerate(row, start=18,):
                if index >= 89 :
                    break
                for candidate in list(candidate_positions.keys()):
                    if candidate in roww:
                        nb_votants = int((int(row[index + 2])*expr_dep_simul)/expr_dep)
                    if candidate not in voters_per_candidate:
                        voters_per_candidate[candidate] = {}

                    voters_per_candidate[candidate][dep_code] = nb_votants #within a departement

            # generate voters for each departement
            voters = []
            for candidate, num_voters in voters_per_candidate.items():
                if dep_code in num_voters:
                    candidate_pos = candidate_positions[candidate]
                    for i in range(num_voters[dep_code]):
                        x = random.uniform(candidate_pos[0] - radius, candidate_pos[0] + radius)
                        y_range = math.sqrt(radius ** 2 - (x - candidate_pos[0]) ** 2)
                        y = random.uniform(candidate_pos[1] - y_range, candidate_pos[1] + y_range)
                        voters.append((x/2, y/2))
            
            if voters == [] :
                print("Departement with code " + dep_code + " not heavy enough")
            else :
                # generate files for each departement
                filename = "voters" + dep_code + ".csv"
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Votants'])

                for x,y in voters :
                    writer.writerow([x/2, y/2])
                    writer.writerows(voters)

        return voters_per_candidate
            
#-----------------------------------------------------------------------------------------------------------

def shift_voters(off_data, webplot,scaledown, from_dep, to_dep, candidate, radius):
    """
    Shifts a percentage of voters from one candidate to another within a specific department, and updates the corresponding
    CSV file containing the voters' positions.

    :param off_data: declared above, csv file we are extracting from
    :param webplot: csv file containing coordinates for each candidate in the order of their name in candNamesPos
    :param scaledown: max number of voters for the whole country.
                    MUST BE THE SAME VALUE AS 'scaledown' GIVEN WHEN FIRST GENERATED THE FILES FOR ALL VOTERS.
    :param from_dep: The department code where the voters are being shifted from, must enter a string.
    :param from_dep: The department code where the voters are being shifted to, must enter a string.
    :param candidate: The name of the candidate that the voters are being shifted from, must enter a string.
    :param radius: The radius of the circle around each candidate position within which voters will be generated.
    :return: None
    """

    # load candidate positions with CandidatestoCSV()
    _,candidate_positions = CandidatestoCSV(off_data, webplot) #Just the dict { name : [x,y] }, not the csv file

    modifs = dict()

    # Delete the existing files 
    with open(off_data, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        filename1 = "voters" + from_dep + ".csv"
        filename2 = "voters" + from_dep + ".csv"

        if(os.path.exists(filename1) and os.path.isfile(filename1)):
            os.remove(filename1)
            print("file for departement " + from_dep + " deleted")
        else:
            print("no csv file to delete found for departement " + filename1)

        if(os.path.exists(filename2) and os.path.isfile(filename2)):
            os.remove(filename2)
            print("file for departement " + from_dep + " deleted")
        else:
            print("no csv file to delete found for departement " + filename2)
    
    # Generate the new files
    voters_per_candidate = generate_voters_by_department(off_data, webplot, scaledown, radius)

    #---------------------------------------------------------------------------------------------
    # useless ?
    for name, dictdep in voters_per_candidate.items() :
        if name == candidate :
            for code, nb_votants in dictdep.items() :
                if code == from_dep :
                    #tuple with the 'giving' dep and its number of voters AFTER giving out
                    modifs['giver'] = code, nb_votants
                if code == to_dep :
                    #tuple with the 'receiving' dep and its number of voters AFTER receiving out
                    nb_votants += modifs['giver'][1]
                    modifs['receiver'] = code, nb_votants
    #----------------------------------------------------------------------------------------------
    
    voters_per_candidate[candidate][to_dep] += voters_per_candidate[candidate][from_dep]
    voters_per_candidate[candidate][from_dep] = 0

    # generate voters for each departement
    dep_code = dict()
    voters = []
    for code_dep, nb_votants in voters_per_candidate[candidate] :
        if code_dep == to_dep or code_dep == from_dep :
            candidate_pos = candidate_positions[candidate]
            for i in range(nb_votants):
                x = random.uniform(candidate_pos[0] - radius, candidate_pos[0] + radius)
                y_range = math.sqrt(radius ** 2 - (x - candidate_pos[0]) ** 2)
                y = random.uniform(candidate_pos[1] - y_range, candidate_pos[1] + y_range)
                voters.append((x/2, y/2))
                
            # generate files for each departement
            dep_code[code_dep] = voters 
            filename = "voters" + code_dep + ".csv"
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Votants'])

                for x,y in voters :
                    writer.writerow([x/2, y/2])
                    writer.writerows(voters)

            return voters_per_candidate



#------------------------------------------------Main-------------------------------------------------------
#CandidatestoCSV(off_data, webplot) #works
#generate_voters_by_department(off_data,webplot, 10000, 0.5)
shift_voters(off_data, webplot, 10000, '75', 'ZX', 'LASSALLE', 0.5)