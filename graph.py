import math
import random

import ToolTip
import tkinter as tk

from candidate import Candidate
from graph_manager import GraphManager
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


def num_char(num_letters: int) -> int:
    num_letters_next = 0
    i = 0
    while num_letters_next < num_letters:
        i += 1
        num_letters_next += 26 ** i
    return i


def purify(number: int) -> int:
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
    label_num_char = num_char(new_candidate_index + 1)

    label = ""
    for i in reversed(range(1, label_num_char + 1)):
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
def valider(*args):
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
    number.trace_variable("w", valider)
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
def generer_profils():
    global top
    if top:
        top.destroy()

    # Dictionary to store the scores for each voter
    dico = dict()

    # Loop to calculate the scores for each voter
    for i in range(len(voters)):
        scores = []
        for j in range(len(candidates)):
            scores.append((chr(ord('A') + j), math.dist(voters[i].coordinates(), candidates[j].coordinates())))
        scores.sort(key=lambda x: x[1])
        dico[i] = scores

    if not dico or voters == [] or candidates == []:
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
        for c, d in dico.items():
            lab = tk.Label(top, text="Votant " + str(c + 1))
            lab.grid(row=0, column=c, sticky="NSEW")
            for e in range(len(candidates)):
                # Calculates the max distance (diagonal) of the plot
                maximum = math.sqrt(
                    (int(graph_manager.get_xlim()[1]) - int(graph_manager.get_xlim()[0])) ** 2 +
                    (int(graph_manager.get_ylim()[1]) - int(graph_manager.get_ylim()[0])) ** 2
                )
                # Calculates the percentage based on max distance
                res = ((maximum - d[e][1]) * 100) / maximum
                lab = tk.Label(top, text=str(d[e][0]))
                lab.grid(row=e + 1, column=c, sticky="NSEW")
                ToolTip.create_tool_tip(lab, text=str(round(res, 2)) + "%")


# Add the canvas to the tkinter window
graph_manager.get_tk_widget().grid(row=0, column=0, padx=20, pady=20)
graph_manager.get_tk_widget().pack()

# Generate the profiles on button click
generate_profiles = tk.Button(root, text="Generer les profils", command=generer_profils)
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

# Start the tkinter event loop
root.mainloop()
