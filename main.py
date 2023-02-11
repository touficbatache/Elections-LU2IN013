import math
import random

import tkinter as tk

from typing import Tuple

from candidate import Candidate
from graph_manager import GraphManager
from tooltip import bind_tooltip
from voter import Voter
from voting_manager import VotingManager

# Create the main tkinter window
root = tk.Tk()
root.title("Simulation Elections")
root.geometry("750x750")
root.option_add('*Font', 'Mistral 12')

# Create a graph manager and build it
graph_manager = GraphManager(root)
graph_manager.build()

# Create the StringVar variables used to hold the requested number of candidates for the normal and parameterized distributions
number_candidates = tk.StringVar()
number_candidates_random = tk.StringVar()

# Create the Candidate list
candidates = []

# Create the StringVar variables used to hold the requested number of voters for the normal and parameterized distributions
number_voters = tk.StringVar()
number_voters_random = tk.StringVar()

# Create the Voter list
voters = []

# Default value for nb candidates/voters
default_nb_candidates_voters = 7

# Variable to keep track of the "shift" key press
shift_is_held = False

# Create a voting manager
voting_manager = VotingManager()


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


def validate(*args):
    """
    Validates the input given (the number of candidates or voters).
    """
    if args[0] == 'PY_VAR0':
        value = number_candidates
    elif args[0] == 'PY_VAR1':
        value = number_candidates_random
    elif args[0] == 'PY_VAR2':
        value = number_voters
    else:
        value = number_voters_random

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
        command=lambda: [distribute(number, is_voter, ((-1, 1), (-1, 1))), top_main.destroy()]
    )
    button.pack()


def distribute_with_parameters(number, object):
    """
    Distributes the object passed in parameter on the graph based on chosen parameters.

    The user is asked for the number of objects (candidates or voters) to distribute.
    If no input is given, the number is by default 7.
    There are 9 buttons which represent the different regions of the graph. Once the
    input is entered, the user presses on one of the buttons. distribute() is then
    called with the coordinates of the region to populate most as parameters.
    Points will still be scattered on the rest of the graph, but with a lower proportion.
    """
    global top
    if top:
        top.destroy()

    top = tk.Toplevel(root)
    top.title("Paramètres de distribution des " + object)

    is_voter = True
    if object == "candidats":
        is_voter = False

    label = tk.Label(top, text="Donner le nombre de " + object + ":")
    label.grid(row=0, column=1)

    global log
    log = tk.StringVar()
    number.trace_variable("w", validate)

    entry = tk.Entry(top, width=20, textvariable=number)
    entry.grid(row=1, column=1)

    btn_top_left = tk.Button(top, text="TOP LEFT", height=7, width=20, command=lambda: [distribute(number, is_voter, ((-1, 0), (0, 1))), top.destroy()])
    btn_top_left.grid(row=2, column=0)

    btn_top_middle = tk.Button(top, text="TOP MIDDLE", height=7, width=20, command=lambda: [distribute(number, is_voter, ((-0.5, 0.5), (0, 1))), top.destroy()])
    btn_top_middle.grid(row=2, column=1)

    btn_top_right = tk.Button(top, text="TOP RIGHT", height=7, width=20, command=lambda: [distribute(number, is_voter, ((0, 1), (0, 1))), top.destroy()])
    btn_top_right.grid(row=2, column=2)

    btn_middle_left = tk.Button(top, text="MIDDLE LEFT", height=7, width=20, command=lambda: [distribute(number, is_voter, ((-1, 0), (-0.5, 0.5))), top.destroy()])
    btn_middle_left.grid(row=3, column=0)

    btn_center = tk.Button(top, text="CENTER", height=7, width=20, command=lambda: [distribute(number, is_voter, ((-0.5, 0.5), (-0.5, 0.5))), top.destroy()])
    btn_center.grid(row=3, column=1)

    btn_middle_right = tk.Button(top, text="MIDDLE RIGHT", height=7, width=20, command=lambda: [distribute(number, is_voter, ((0, 1), (-0.5, 0.5))), top.destroy()])
    btn_middle_right.grid(row=3, column=2)

    btn_bottom_left = tk.Button(top, text="BOTTOM LEFT", height=7, width=20, command=lambda: [distribute(number, is_voter, ((-1, 0), (-1, 0))), top.destroy()])
    btn_bottom_left.grid(row=4, column=0)

    btn_bottom_middle = tk.Button(top, text="BOTTOM MIDDLE", height=7, width=20, command=lambda: [distribute(number, is_voter, ((-0.5, 0.5), (-1, 0))), top.destroy()])
    btn_bottom_middle.grid(row=4, column=1)

    btn_bottom_right = tk.Button(top, text="BOTTOM RIGHT", height=7, width=20, command=lambda: [distribute(number, is_voter, ((0, 1), (-1, 0))), top.destroy()])
    btn_bottom_right.grid(row=4, column=2)


def show_distribution_with_parameters():
    """
    Allows the user to choose between candidates or voters to ditribute on the graph.
    """
    # If a top level window is active, close it
    global top
    if top:
        top.destroy()

    top = tk.Toplevel(root)
    top.title("Paramètres de distribution")

    btn_candidates = tk.Button(top, text="Candidats", height=7, width=20,
                               command=lambda candidate="candidats": distribute_with_parameters(number_candidates_random, candidate))
    btn_candidates.grid(row=0, column=0)

    btn_voters = tk.Button(top, text="Votants", height=7, width=20,
                           command=lambda voter="votants": distribute_with_parameters(number_voters_random, voter))
    btn_voters.grid(row=0, column=1)


# Function to distribute the candidates/voters randomly on the graph
def distribute(number, is_voter: bool, density_position: Tuple[Tuple[float, float], Tuple[float, float]]):
    if number.get() != "":
        nb = int(number.get())
    else:
        nb = default_nb_candidates_voters

    for i in range(nb):
        # Random coordinates
        if random.random() > 0.3:
            x_lower = density_position[0][0]
            x_upper = density_position[0][1]
            y_lower = density_position[1][0]
            y_upper = density_position[1][1]
            coordinates = (random.uniform(x_lower, x_upper), random.uniform(y_lower, y_upper))
        else:
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
winner_dialog = None


# Function to show the scores
def show_profils():
    # If a top level window is active, close it
    global top
    if top:
        top.destroy()

    # The scores for each voter
    profils = generate_profils()

    if not profils or voters == [] or candidates == []:
        # If there are no results in the dictionary, show it in window title
        tk.messagebox.showwarning(
            title="Données insuffisantes",
            message="Pas de résultats. Veuillez ajouter des votants et des candidats."
        )
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


# Function to generate the scores
def generate_profils():
    # Dictionary to store the scores for each voter
    profils = dict()

    # Loop to calculate the scores for each voter
    for voter in voters:
        # profil = list(...tuple(<candidate label>, <distance between candidate and voter>)...)
        profil = list(map(
            lambda candidate: (candidate.label(), math.dist(voter.coordinates(), candidate.coordinates())),
            candidates
        ))
        # Sort by closest match
        profil.sort(key=lambda x: x[1])
        # profils = {...<voter label>: <profil>...}
        profils[voter.label()] = profil

    return profils


def show_voting_systems():
    # If a top level window is active, close it
    global top
    if top:
        top.destroy()

    # The scores for each voter
    profils = generate_profils()

    # If profils is null, there are no voters or no candidates: show an error dialog
    if not profils or len(voters) == 0 or len(candidates) == 0:
        tk.messagebox.showwarning(
            title="Données insuffisantes",
            message="Veuillez ajouter des votants et des candidats."
        )
    else:
        # Create a new top level window to display the different voting systems to choose from
        top = tk.Toplevel(root)
        top.title("Systèmes de vote")

        # Pluralité Simple button
        # TODO #22: connect button to logic: show popup with results. use `profils` (already defined)
        btn_pluralite_simple = tk.Button(top, text="Pluralité Simple", height=7, width=20)
        btn_pluralite_simple.grid(row=0, column=0)

        # Approbation button
        # TODO #21: connect button to logic: show popup with results. use `profils` (already defined)
        btn_approbation = tk.Button(top, text="Approbation", height=7, width=20)
        btn_approbation.grid(row=0, column=1)

        # Borda button
        # TODO #23: connect button to logic: show popup with results. use `profils` (already defined)
        btn_borda = tk.Button(top, text="Borda", height=7, width=20)
        btn_borda.grid(row=1, column=0)

        # Élimination Successive button
        # TODO #25: connect button to logic: show popup with results. use `profils` (already defined)
        btn_elimination_successive = tk.Button(top, text="Élimination Successive", height=7, width=20)
        btn_elimination_successive.grid(row=1, column=1)

        # Veto button
        # TODO #24: connect button to logic: show popup with results. use `profils` (already defined)
        btn_veto = tk.Button(top, text="Veto", height=7, width=20)
        btn_veto.grid(row=2, column=0)

        # Condorcet button
        # TODO #26: connect button to logic: show popup with results. use `profils` (already defined)
        btn_condorcet = tk.Button(top, text="Condorcet", height=7, width=20)
        btn_condorcet.grid(row=2, column=1)


def display_winner(winner: Tuple[str, bool, list], method: str):
    """
    Display winner in a popup.

    :param winner: Tuple of winner, boolean specifying if raw-win or not, list of opponents if not raw-win
    :param method: The name of the voting method
    """
    global winner_dialog
    if winner_dialog:
        winner_dialog.destroy()

    winner_dialog = tk.Toplevel(root)
    winner_dialog.title("Vainceur selon " + method)
    tk.Label(winner_dialog, text="Le gagnant selon de système " + method + " est :").pack()

    tk.Label(winner_dialog, text=winner[0], font=("Mistral", "25", "normal")).pack()

    if winner[1]:
        tk.Label(winner_dialog, text="Ce candidat a gagné par départage parmi les concurrents suivant :").pack()
        tk.Label(winner_dialog, text=str(winner[2])).pack()
        tk.Label(winner_dialog, text="La règle de départage utilisée correspond à l'ordre alphabétique").pack()
    else:
        tk.Label(winner_dialog, text="Il n'y a pas eu de départage").pack()


# Add the canvas to the tkinter window
graph_manager.get_tk_widget().grid(row=0, column=0, padx=20, pady=20)
graph_manager.get_tk_widget().pack()

# Reset the voters on button click
reset_voters = tk.Button(root, text="Réinitialiser les votants", command=lambda: reset(is_voter=True))
reset_voters.place(relx=0.58, rely=0, relwidth=0.2, relheight=0.05)
reset_voters.configure(cursor="exchange")

# Reset the candidates on button click
reset_candidates = tk.Button(root, text="Réinitialiser les candidats", command=lambda: reset(is_voter=False))
reset_candidates.place(relx=0.78, rely=0, relwidth=0.22, relheight=0.05)
reset_candidates.configure(cursor="exchange")

# Generate the profiles on button click
generate_profiles = tk.Button(root, text="Génerer les profils", command=show_profils)
generate_profiles.place(relx=0, rely=1 - 0.05, relwidth=0.25, relheight=0.05)

btn_distribution_with_parameters = tk.Button(root, text="Paramètres de distribution", command=show_distribution_with_parameters)
btn_distribution_with_parameters.place(relx=0, rely=0, relwidth=0.25, relheight=0.05)

# Generate the profiles on button click
btn_show_voting_systems = tk.Button(root, text="Systèmes de vote", command=show_voting_systems)
btn_show_voting_systems.place(relx=0.25, rely=1 - 0.05, relwidth=0.25, relheight=0.05)

# Distribute the voters on button click
distribute_voters = tk.Button(
    root,
    text="Distribuer les votants",
    command=lambda: show_distribute_popup(number_voters, is_voter=True)
)
distribute_voters.place(relx=0.5, rely=1 - 0.05, relwidth=0.25, relheight=0.05)

# Distribute the candidates on button click
distribute_candidates = tk.Button(
    root,
    text="Distribuer les candidats",
    command=lambda: show_distribute_popup(number_candidates, is_voter=False)
)
distribute_candidates.place(relx=0.75, rely=1 - 0.05, relwidth=0.25, relheight=0.05)

# Start the tkinter event loop
root.mainloop()
