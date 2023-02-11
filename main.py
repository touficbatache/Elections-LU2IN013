import os.path
import math
import random
import time

import tkinter as tk

from candidate import Candidate
from graph_manager import GraphManager
from tooltip import bind_tooltip
from voter import Voter

# Create the main tkinter window
root = tk.Tk()
root.title("Simulation Elections")
root.geometry("750x750")
root.option_add('*Font', 'Mistral 12')

# Create a graph manager and build it
graph_manager = GraphManager(root)
graph_manager.build()

# Create the StringVar used to hold the requested number of candidates
number_candidates = tk.StringVar()
# Create the Candidate list
candidates = []

# Create the StringVar used to hold the requested number of voters
number_voters = tk.StringVar()
# Create the Voter list
voters = []

# Default value for nb candidates/voters
default_nb_candidates_voters = 7

# Variable to keep track of the "shift" key press
shift_is_held = False


def add_voter_on_graph(coordinates: tuple) -> int:
    """
    Adds a voter to the graph.

    :param coordinates: the coordinates of the voter
    :return: the index of the voter inside the list
    """

    # Create a new voter
    voter = Voter(label=str(len(voters) + 1), coordinates=coordinates)

    # Try to add voter to graph
    if graph_manager.add_voter(voter):
        # Add voter to the list
        voters.append(voter)

        # Return index in list
        return len(voters) - 1

    return -1


def get_letter_count(index: int) -> int:
    """
    Returns the letter count for a label at a given index.
    """
    labels_before_index = 0
    letter_count = 0

    # Search how many powers of 26 can fit before reaching the
    # given index. We don't want to use log_26 because if we have
    # a two-lettered label, then we would have already filled the
    # one-lettered possibilities. So if we have a 676 (26^2) index,
    # then that means it already contains the 26 one-lettered labels,
    # so the label only becomes three-lettered if 676+26=702 is reached.
    while labels_before_index < index:
        letter_count += 1
        labels_before_index += 26 ** letter_count
    return letter_count


def purify(number: int) -> int:
    """
    Returns the corresponding number based on the number of letters.

    Example:

    0 -> A
    25 -> Z

    If the given number is 26, that should correspond to A, and it returns 0.

    It may look like this is working the same as modulo because it's quite
    similar. The modulo operator gives us the remainder of the division by a
    number, by removing multiples of that number. This gives us the remainder
    by removing powers of the number.

    Now if the number is 676 for instance, this will return 650 and not 0. Why?
    Because if we have a two-lettered label, then we would have already filled the
    one-lettered possibilities. So if we have a 676 (26^2) index, then that means
    it already contains the 26 one-lettered labels, so the label only becomes
    three-lettered if 676+26=702 is reached. So if we reached 676, then that means
    we need to deal with one more set of 26s before resetting.
    """
    i = 1
    while number >= 26 ** i:
        number -= 26 ** i
        i += 1
    return number


def add_candidate_on_graph(coordinates: tuple) -> int:
    """
    Adds a candidate to the graph.

    :param coordinates: the coordinates of the candidate
    :return: the index of the candidate inside the list
    """

    # Generate an adequate label for the candidate
    new_candidate_index = len(candidates)
    label_letter_count = get_letter_count(new_candidate_index + 1)

    label = ""
    for i in reversed(range(1, label_letter_count + 1)):
        label += chr(ord('A') + (purify(new_candidate_index) % (26 ** i) // (26 ** (i - 1))))

    # Create a new candidate
    candidate = Candidate(label=label, coordinates=coordinates)

    # Try to add candidate to graph
    if graph_manager.add_candidate(candidate):
        # Add candidate to the list
        candidates.append(candidate)

        # Return index in list
        return len(candidates) - 1

    return -1


def import_from_file():
    """
    Shows popup explaining the format of the file to import.
    Handles user input.
    Calls import_objects_from_file() and gives it the name of a file as input.
    """
    top_main = tk.Toplevel(root)
    top_main.title("Lecture d'un fichier")
    top_main.geometry("600x420")

    label_title = tk.Label(top_main, text="Donner le nom du fichier avec l'extension .txt :")
    label_title.pack()

    file = tk.StringVar()
    entry = tk.Entry(top_main, width=20, textvariable=file)
    entry.pack()

    file_format = tk.Text(top_main, wrap=tk.WORD, bg='#ececec')
    file_format.insert(
        tk.INSERT,
        "Le fichier doit avoir le format suivant:\n\n"
        "Candidats\n"
        "-0.589,0.75\n"
        "0.32,0.740\n"
        "-0.483,-0.3904\n"
        "0.2350,-0.34\n"
        "Votants\n"
        "-0.198,0.32\n"
        "0.3548,0.311\n"
        "-0.04879,-0.432\n"
        "0.87826,-0.49\n\n"
         
        "La premiere ligne est soit \"Candidats\" soit \"Votants\".\n"
        "Chaque ligne qui suit contient les coordonnées d'un candidat/votant séparés d'une virgule.\n"
        "Ce format peut être répété dans le fichier autant de fois que possible, avec ou sans des lignes vides après passage d'un objet à un autre.\n\n"
        "Remarque: Les coordonnées sont comprises entre [-1,1]."
    )
    file_format.config(state=tk.DISABLED, height=20)
    file_format.pack()

    label_hint = tk.Label(
        top_main,
        text="Laisser vide pour valeur de défaut (default.txt)"
    )
    label_hint.pack()

    button = tk.Button(
        top_main,
        text="Importer le fichier",
        command=lambda: [import_objects_from_file(file), top_main.destroy()]
    )
    button.pack()


def import_objects_from_file(file):
    """
    Imports the coordinates of candidates and/or voters from file and plots them on the graph.
    If no file is given, the default one is used.

    :param file: name of the file to import from
    """
    if file.get() != "":
        file_name = str(file.get())
    else:
        file_name = "default.txt"

    path = "./files/" + file_name
    if not os.path.exists(path):
        tk.messagebox.showwarning(title='Erreur de lecture', message="Le fichier donné n'existe pas.")
    else:
        list_candidates = []
        list_voters = []

        f = open(path, "r")
        object = f.readline().strip('\n')
        i = 1
        for line in f:
            i += 1
            try:
                x, y = map(float, line.strip('\n').split(","))
                if x < -1 or x > 1 or y < -1 or y > 1:
                    tk.messagebox.showwarning(title='Erreur de lecture', message="Les coordonnées à la ligne " + str(i) + " sont invalides.")
                    return -1

                if object == "Candidats":
                    list_candidates.append((x, y))
                elif object == "Votants":
                    list_voters.append((x, y))
                else:
                    tk.messagebox.showwarning(title='Erreur de lecture', message="Le format de la ligne " + str(i - 1) + " est invalide.")
                    return -1
            except ValueError:
                object = line.strip('\n')
                if object != "Candidats" and object != "Votants" and object != "":
                    tk.messagebox.showwarning(title='Erreur de lecture',
                                              message="Le format de la ligne " + str(i) + " est invalide.")
                    return -1

        f.close()

        for candidate in list_candidates:
            add_candidate_on_graph(candidate)
        for voter in list_voters:
            add_voter_on_graph(voter)

        graph_manager.build()


def export_objects_to_file():
    """
    Creates a new file and writes the coordinates of the candidates and/or voters present on the graph in it.
    The file is created in the directory 'files'.
    """
    if candidates == [] and voters == []:
        tk.messagebox.showwarning(title='Erreur de sauvegarde',
                                  message="Il n'y a ni candidats ni votants sur le graphe.")
        return -1
    file_name = "donnees-" + time.strftime("%d%m%Y-%H%M%S") + ".txt"
    file = open("./files/" + file_name, "w")
    if candidates:
        file.write("Candidats\n")
        for candidate in candidates:
            x, y = candidate.coordinates()
            file.write(str(x) + "," + str(y) + "\n")

    if voters:
        if candidates:
            file.write("\n")
        file.write("Votants\n")
        for voter in voters:
            x, y = voter.coordinates()
            file.write(str(x) + "," + str(y) + "\n")

    tk.messagebox.showinfo(title="Sauvegarde réussie", message="Le fichier " + file_name + " a été créé dans le répertoire 'files'.")
    file.close()


# Function to handle the key press event
# Here, we're using it to update the shift press
def on_key_press(event):
    if event.key == 'shift':
        global shift_is_held
        shift_is_held = True


# Function to handle the key release event
# Here, we're using it to update the shift release
def on_key_release(event):
    if event.key == 'shift':
        global shift_is_held
        shift_is_held = False


# Connect the key press/release events to the on_key_press and on_key_release functions
graph_manager.bind('key_press_event', on_key_press)
graph_manager.bind('key_release_event', on_key_release)


# Function to handle click events on the graph
def on_click(event):
    # Get the x and y coordinates of the click event
    x = event.xdata
    y = event.ydata

    # Add the point to the list of points, only if clicked inside the graph
    if x is not None and -1 <= x <= 1 and y is not None and -1 <= y <= 1:
        # If the shift key is pressed, add candidates instead of voters
        if shift_is_held:
            # Candidate :
            add_candidate_on_graph((x, y))
        else:
            # Voter :
            add_voter_on_graph((x, y))

        # Build the graph: redraw the canvas
        graph_manager.build()


# Connect the click event to the on_click function
graph_manager.bind("button_press_event", on_click)


# Function to validate the input given (the number of candidates or voters)
def validate(*args):
    if args[0] == 'PY_VAR1':
        value = number_voters
    else:
        value = number_candidates

    if not (value.get()).isdigit() and value.get() != "":
        value.set(log.get())
    else:
        log.set(value.get())


# Function to clear the candidates/voters
def reset(is_voter: bool):
    if is_voter:
        # Voters :
        if not voters:
            tk.messagebox.showerror(title="Votants déjà réinitialisés", message="Votants déjà réinitialisés")
            return

        graph_manager.clear_voters()
        voters.clear()
    else:
        # Candidates :
        if not candidates:
            tk.messagebox.showerror(title="Candidats déjà réinitialisés", message="Candidats déjà réinitialisés")
            return

        graph_manager.clear_candidates()
        candidates.clear()

    graph_manager.build()


# Function to show a popup, handle the input and distribute candidates/voters
def show_distribute_popup(number, is_voter: bool):
    s = "votants" if is_voter else "candidats"

    top_main = tk.Toplevel(root)
    top_main.title("Choisir le nombre de " + s)
    top_main.geometry("250x150")

    label_title = tk.Label(top_main, text="Donner le nombre de " + s + " :")
    label_title.pack()

    global log
    log = tk.StringVar()
    number.trace_variable("w", validate)
    entry = tk.Entry(top_main, width=20, textvariable=number)
    entry.pack()

    label_hint = tk.Label(
        top_main,
        text="Laisser vide pour valeur de défaut (" + str(default_nb_candidates_voters) + ")"
    )
    label_hint.pack()

    button = tk.Button(
        top_main,
        text="Distribuer les " + s,
        command=lambda: [distribute(number, is_voter), top_main.destroy()]
    )
    button.pack()


# Function to distribute the candidates/voters randomly on the graph
def distribute(number, is_voter: bool):
    if number.get() != "":
        nb = int(number.get())
    else:
        nb = default_nb_candidates_voters

    for i in range(nb):
        # Random coordinates
        coordinates = (random.uniform(-1, 1), random.uniform(-1, 1))

        if is_voter:
            # Voter :
            add_voter_on_graph(coordinates)
        else:
            # Candidate :
            add_candidate_on_graph(coordinates)

    # Build the graph: redraw the canvas
    graph_manager.build()


# Variable to keep track of the top level window
top = None


# Function to generate the profiles
def generate_profils():
    global top
    if top:
        top.destroy()

    # Dictionary to store the scores for each voter
    profils = dict()

    # Loop to calculate the scores for each voter
    for voter in voters:
        profil = list(map(
            lambda candidate: (candidate.label(), math.dist(voter.coordinates(), candidate.coordinates())),
            candidates
        ))
        profil.sort(key=lambda x: x[1])
        profils[voter.label()] = profil

    if not profils or voters == [] or candidates == []:
        # If there are no results in the dictionary, show it in window title
        tk.messagebox.showwarning(title='Pas de résultats', message="Pas de résultats")
    else:
        # Create a new top level window to display the results
        top = tk.Toplevel(root)
        top.geometry(str(len(voters) * 90) + "x" + str(len(candidates) * 40))
        top.title("Les résultats")
        # Generate a table for each voter representing their profile
        for a in range(len(voters)):
            tk.Grid.columnconfigure(top, a, weight=1)
        for b in range(len(candidates) + 1):
            tk.Grid.rowconfigure(top, b, weight=1)
        for index, (label, profil) in enumerate(profils.items()):
            lab = tk.Label(top, text="Votant " + label)
            lab.grid(row=0, column=index, sticky="NSEW")
            for e in range(len(candidates)):
                # Calculates the max distance (diagonal) of the plot
                maximum = math.sqrt(
                    (int(graph_manager.get_xlim()[1]) - int(graph_manager.get_xlim()[0])) ** 2 +
                    (int(graph_manager.get_ylim()[1]) - int(graph_manager.get_ylim()[0])) ** 2
                )
                # Calculates the percentage based on max distance
                res = ((maximum - profil[e][1]) * 100) / maximum
                lab = tk.Label(top, text=str(profil[e][0]))
                lab.grid(row=e + 1, column=index, sticky="NSEW")
                bind_tooltip(widget=lab, text=str(round(res, 2)) + "%")


# Add the canvas to the tkinter window
graph_manager.get_tk_widget().grid(row=0, column=0, padx=20, pady=20)
graph_manager.get_tk_widget().pack()

# Generate the profiles on button click
generate_profiles = tk.Button(root, text="Generer les profils", command=generate_profils)
generate_profiles.place(relx=0, rely=1 - 0.05, relwidth=0.25, relheight=0.05)

# Distribute the voters on button click
distribute_voters = tk.Button(
    root,
    text="Distribuer les votants",
    command=lambda: show_distribute_popup(number_voters, is_voter=True)
)
distribute_voters.place(relx=0.25, rely=1 - 0.05, relwidth=0.25, relheight=0.05)

# Reset the voters on button click
reset_voters = tk.Button(root, text="Réinitialiser les votants", command=lambda: reset(is_voter=True))
reset_voters.place(relx=0.58, rely=0, relwidth=0.2, relheight=0.05)
reset_voters.configure(cursor="exchange")

# Distribute the candidates on button click
distribute_candidates = tk.Button(
    root,
    text="Distribuer les candidats",
    command=lambda: show_distribute_popup(number_candidates, is_voter=False)
)
distribute_candidates.place(relx=0.5, rely=1 - 0.05, relwidth=0.25, relheight=0.05)

# Reset the candidates on button click
reset_candidates = tk.Button(root, text="Réinitialiser les candidats", command=lambda: reset(is_voter=False))
reset_candidates.place(relx=0.78, rely=0, relwidth=0.22, relheight=0.05)
reset_candidates.configure(cursor="exchange")

# Import file on button click
import_file = tk.Button(root, text="Lire des données", command=lambda: import_from_file())
import_file.place(relx=0.36, rely=0, relwidth=0.22, relheight=0.05)

# Export file on button click
export_file = tk.Button(root, text="Sauvegarder les données", command=lambda: export_objects_to_file())
export_file.place(relx=0.14, rely=0, relwidth=0.22, relheight=0.05)

# Start the tkinter event loop
root.mainloop()
