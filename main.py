import math
import random
import string

import tkinter as tk

from candidate import Candidate
from graph_manager import GraphManager
from tooltip import bind_tooltip
from voter import Voter
from voting_manager import VotingManager, CondorcetMethod, CondorcetTieBreakingRule

# Create the main tkinter window
root = tk.Tk()
root.title("Simulation Elections")
root.geometry("750x750")
root.option_add('*Font', 'Mistral 12')

# Create a graph manager and build it
graph_manager = GraphManager(root)
graph_manager.build()

# Create the StringVar used to hold the requested number of candidates
stringvar_number_candidates = tk.StringVar(name="number_candidates")
# Create the Candidate list
candidates = []

# Create the StringVar used to hold the requested number of voters
stringvar_number_voters = tk.StringVar(name="number_voters")
# Create the Voter list
voters = []

# Default value for nb candidates/voters
default_nb_candidates_voters = 7

# Variable to keep track of the "shift" key press
shift_is_held = False

# Create a voting manager
voting_manager = VotingManager()

# Create the StringVar used to hold the approval radius around candidates
stringvar_approval_radius = tk.StringVar(name="approval_radius")
# Default value for nb candidates/voters
default_approval_radius = 10

# Create the StringVar used to hold the maximum borda score
stringvar_borda_max = tk.StringVar(name="borda_max")
# Create the StringVar used to hold the step borda score
stringvar_borda_step = tk.StringVar(name="borda_step")

# Create the IntVar to track which condercet method
var_condorcet_method = tk.IntVar(name="var_condorcet_method")
# Create the IntVar to track which tie-breaking condercet method
var_condorcet_tie_breaking = tk.IntVar(name="var_condorcet_tie_breaking")


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


# Function to validate the input given (the number of candidates or voters)
def validate(*args):
    if args[0] == "number_voters":
        value = stringvar_number_voters
    elif args[0] == "number_candidates":
        value = stringvar_number_candidates

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
def show_distribute_popup(stringvar_number, is_voter: bool):
    s = "votants" if is_voter else "candidats"

    top_main = tk.Toplevel(root)
    top_main.title("Choisir le nombre de " + s)
    top_main.geometry("250x150")

    label_title = tk.Label(top_main, text="Donner le nombre de " + s + " :")
    label_title.pack()

    global log
    log = tk.StringVar()
    stringvar_number.trace_variable("w", validate)
    entry = tk.Entry(top_main, width=20, textvariable=stringvar_number)
    entry.pack()

    label_hint = tk.Label(
        top_main,
        text="Laisser vide pour valeur de défaut (" + str(default_nb_candidates_voters) + ")"
    )
    label_hint.pack()

    button = tk.Button(
        top_main,
        text="Distribuer les " + s,
        command=lambda: [distribute(stringvar_number, is_voter), top_main.destroy()]
    )
    button.pack()


# Function to distribute the candidates/voters randomly on the graph
def distribute(stringvar_number, is_voter: bool):
    if stringvar_number.get() != "":
        nb = int(stringvar_number.get())
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
top_main = None
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
                # Calculates the percentage based on max distance
                lab = tk.Label(top, text=str(profil[e][0]))
                lab.grid(row=e + 1, column=index, sticky="NSEW")
                bind_tooltip(widget=lab, text=str(round(profil[e][1] * 100, 2)) + "%")


# Function to generate the scores
def generate_profils():
    # Dictionary to store the scores for each voter
    profils = dict()

    # Calculates the max distance (diagonal) of the plot
    maximum = graph_manager.get_diagonal()

    # Loop to calculate the scores for each voter
    for voter in voters:
        # profil = list(...tuple(<candidate label>, <distance between candidate and voter>)...)
        profil = list(map(
            lambda candidate:
            (
                candidate.label(),
                (maximum - math.dist(voter.coordinates(), candidate.coordinates())) / maximum
            ),
            candidates
        ))
        # Sort by closest match
        profil.sort(key=lambda x: x[1], reverse=True)
        # profils = {...<voter label>: <profil>...}
        profils[voter.label()] = profil

    return profils


# Function to validate the input given (the number of candidates or voters)
def validate_approval_radius(*args):
    if (not (stringvar_approval_radius.get()).isdigit() or int(
            stringvar_approval_radius.get()) > 100) and stringvar_approval_radius.get() != "":
        stringvar_approval_radius.set(log.get())
    else:
        log.set(stringvar_approval_radius.get())


# Function to show a popup, handle the input and distribute candidates/voters
def show_approbation(profils):
    """
    Show a popup asking the user for the approval circle's radius.

    :param profils: Scores for each voter
    """
    top_main = tk.Toplevel(root)
    top_main.title("Rayon d'approbation")

    label_title = tk.Label(top_main, text="Rayon d'approbation (pourcentage) :")
    label_title.pack()

    global log
    log = tk.StringVar()
    stringvar_approval_radius.trace_variable("w", validate_approval_radius)
    entry = tk.Entry(top_main, width=20, textvariable=stringvar_approval_radius)
    entry.pack()

    label_hint = tk.Label(
        top_main,
        text="Laisser vide pour valeur de défaut (" + str(default_approval_radius) + "%)"
    )
    label_hint.pack()

    button = tk.Button(
        top_main,
        text="Définir",
        command=lambda: [
            calculate_approbation(
                profils,
                int(stringvar_approval_radius.get()) if stringvar_approval_radius.get() != "" else default_approval_radius
            ),
            top_main.destroy()
        ]
    )
    button.pack()


# Function to validate the input given (the number of candidates or voters)
def validate_borda(*args):
    """
    Verify the entry in show_borda().
    The entry should be a digit, not equal to zero and less than the number of
    total candidates.
    The function sets the value of the stringvar at the end
    """
    strvar = stringvar_borda_max if args[0] == "borda_max" else stringvar_borda_step

    if (not (strvar.get()).isdigit() or int(
            strvar.get()) > borda_max or int(strvar.get()) == 0) and strvar.get() != "":
        strvar.set(log.get())
    else:
        log.set(strvar.get())


# Function to show a popup, handle the input and distribute candidates/voters
def show_borda(profils):
    """
    Show a popup asking the user for the maximum score attribution in borda.

    :param profils: Scores for each voter
    """
    global borda_max
    borda_max = len(candidates)
    top_main = tk.Toplevel(root)
    top_main.title("Score maximum - Borda")

    label_title = tk.Label(top_main, text="Score maximum (inférieur au nombre de candidats : " + str(borda_max) + ") :")
    label_title.pack()

    global log
    log = tk.StringVar()
    stringvar_borda_max.trace_variable("w", validate_borda)
    entry = tk.Entry(top_main, width=20, textvariable=stringvar_borda_max)
    entry.pack()

    label_title = tk.Label(top_main, text="Pas de score entre deux candidats : ")
    label_title.pack()

    global log2
    log2 = tk.StringVar()
    stringvar_borda_step.trace_variable("w", validate_borda)
    entry2 = tk.Entry(top_main, width=20, textvariable=stringvar_borda_step)
    entry2.pack()

    label_hint = tk.Label(
        top_main,
        text="Laisser vide pour valeur de défaut (nombre de candidats=" + str(borda_max) + ", pas=1)"
    )
    label_hint.pack()

    button = tk.Button(
        top_main,
        text="Valider",
        command=lambda: [
            display_winner(
                voting_manager.borda(
                    profils,
                    int(stringvar_borda_max.get()) if stringvar_borda_max.get() != "" else borda_max,
                    int(stringvar_borda_step.get()) if stringvar_borda_step.get() != "" else 1
                ), "Borda"
            ),
            top_main.destroy()
        ]
    )
    button.pack()


def calculate_approbation(profils, approval_radius):
    """
    Determine winner using the approval voting system (système de vote par approbation).

    :param profils: Scores for each voter
    :param approval_radius: Radius of the approval circle
    """
    # Show circles on the graph
    graph_manager.add_approbation_circles(approval_radius)
    graph_manager.build()

    # Calculates the max distance (diagonal) of the plot
    winner = voting_manager.approbation(profils, approval_radius)
    display_winner(winner, "Approbation")


def select_maxval_radius(*args):
    """
    Display popup when selecting checkboxes for approbation and borda in combined mode in order
    to choose the radius of approbation or the maximum score accordingly.
    """
    global top_select_max
    top_select_max = tk.Toplevel(root)
    global log
    log = tk.StringVar()

    if args[0] == "approbation":
        top_select_max.title("Choisir le diamètre d'approbation")
        label_title = tk.Label(
            top_select_max, text="Rayon d'approbation (pourcentage) :"
        )
        label_title.pack()

        stringvar_approval_radius.trace_variable("w", validate_approval_radius)
        entry = tk.Entry(
            top_select_max, width=20, textvariable=stringvar_approval_radius
        )
        entry.pack()
        label_hint = tk.Label(
            top_select_max,
            text="Laisser vide pour valeur de défaut ("
                 + str(default_approval_radius)
                 + "%)"
        )
        label_hint.pack()

    if args[0] == "borda":
        top_select_max.title("Choisir le score maximum")
        borda_max = len(candidates)
        label_title = tk.Label(
            top_select_max,
            text="Score maximum (inférieur au nombre de candidats : "
                 + str(borda_max)
                 + ") :"
        )
        label_title.pack()

        stringvar_borda_max.trace_variable("w", validate_borda)
        entry = tk.Entry(top_select_max, width=20, textvariable=stringvar_borda_max)
        entry.pack()

        label_title = tk.Label(
            top_select_max, text="Pas de score entre deux candidats : "
        )
        label_title.pack()

        global log2
        log2 = tk.StringVar()
        stringvar_borda_step.trace_variable("w", validate_borda)
        entry2 = tk.Entry(top_select_max, width=20, textvariable=stringvar_borda_step)
        entry2.pack()

        label_hint = tk.Label(
            top_select_max,
            text="Laisser vide pour valeur de défaut (nombre de candidats="
                 + str(borda_max)
                 + ", pas=1)"
        )
        label_hint.pack()

    button = tk.Button(
        top_select_max, text="Valider", command=lambda: top_select_max.destroy()
    )
    button.pack()

    top_select_max.protocol("WM_DELETE_WINDOW", lambda: on_closing(args[0]))


def select_condorcet(*args):
    global top_select_condorcet
    top_select_condorcet = tk.Toplevel(root)
    top_select_condorcet.title("Condorcet")

    var_condorcet_tie_breaking.set(0)
    var_condorcet_method.set(0)

    tk.Label(top_select_condorcet, text="Choisir le mode de Condorcet souhaité :").pack()

    tk.Radiobutton(
        top_select_condorcet, text="Méthode de Copeland", variable=var_condorcet_method,
        value=CondorcetMethod.COPELAND.value,
        anchor="w"
    ).pack(fill="both")

    tk.Radiobutton(
        top_select_condorcet, text="Méthode de Simpson", variable=var_condorcet_method,
        value=CondorcetMethod.SIMPSON.value,
        anchor="w"
    ).pack(fill="both")

    tk.Label(top_select_condorcet, text="Choisir le mode de départage souhaité :").pack()

    tk.Radiobutton(
        top_select_condorcet, text="Random", variable=var_condorcet_tie_breaking,
        value=CondorcetTieBreakingRule.RANDOM.value,
        anchor="w"
    ).pack(fill="both")

    tk.Radiobutton(
        top_select_condorcet, text="Ordre lexicographique", variable=var_condorcet_tie_breaking,
        value=CondorcetTieBreakingRule.ORDRE_LEXICO.value, anchor="w"
    ).pack(fill="both")

    tk.Button(
        top_select_condorcet,
        text="Valider",
        command=lambda: top_select_condorcet.destroy() if var_condorcet_tie_breaking.get() != 0 and var_condorcet_method.get() != 0 else None
    ).pack()

    top_select_condorcet.protocol("WM_DELETE_WINDOW", lambda: on_closing(args[0]))


def on_closing(var):
    if var == "approbation":
        var_approbation.set(0)
        top_select_max.destroy()
    if var == "borda":
        var_borda.set(0)
        top_select_max.destroy()
    if var == "condorcet":
        var_condorcet.set(0)
        top_select_condorcet.destroy()


def combined_modes():
    """
    Allows user to select different modes and calls show_mult_methods to display the different winners.
    """
    global top_main
    top_main = tk.Toplevel(root)
    top_main.title("Mode combiné")

    label_title = tk.Label(
        top_main, text="Choisir parmi les modes suivants ceux souhaités :"
    )
    label_title.pack()

    var_pluralite_simple = tk.IntVar(name="pluralite_simple")
    tk.Checkbutton(
        top_main, text="Pluralité simple", variable=var_pluralite_simple, anchor="w"
    ).pack(fill="both")

    global var_approbation
    var_approbation = tk.IntVar(name="approbation")
    tk.Checkbutton(
        top_main, text="Approbation", variable=var_approbation, anchor="w"
    ).pack(fill="both")
    var_approbation.trace(
        "w",
        lambda arg0, arg1, arg2: [
            select_maxval_radius(arg0, arg1, arg2) if var_approbation.get() == 1 else None
        ]
    )

    global var_borda
    var_borda = tk.IntVar(name="borda")
    var_borda.trace(
        "w",
        lambda arg0, arg1, arg2: [
            select_maxval_radius(arg0, arg1, arg2) if var_borda.get() == 1 else None
        ]
    )
    tk.Checkbutton(top_main, text="Borda", variable=var_borda, anchor="w").pack(
        fill="both"
    )

    var_elim_succ = tk.IntVar(name="elimination_successive")
    tk.Checkbutton(
        top_main, text="Elimination succéssive", variable=var_elim_succ, anchor="w"
    ).pack(fill="both")

    var_veto = tk.IntVar(name="veto")
    tk.Checkbutton(top_main, text="Veto", variable=var_veto, anchor="w").pack(
        fill="both"
    )

    global var_condorcet
    var_condorcet = tk.IntVar(name="condorcet")
    var_condorcet.trace(
        "w",
        lambda arg0, arg1, arg2: [
            select_condorcet(arg0, arg1, arg2) if var_condorcet.get() == 1 else None
        ]
    )
    tk.Checkbutton(top_main, text="Condorcet", variable=var_condorcet, anchor="w").pack(
        fill="both"
    )

    button = tk.Button(
        top_main,
        text="Valider",
        command=lambda: show_mult_methods(
            [var_pluralite_simple,
             var_approbation,
             var_borda,
             var_elim_succ,
             var_veto,
             var_condorcet]
        )
        if not all(element.get() == 0 for element in
                   [var_pluralite_simple, var_approbation, var_borda, var_elim_succ, var_veto, var_condorcet])
        else None
    )
    button.pack()


def show_mult_methods(list_of_checks: list):
    """
    Displays the winners according to different voting methods according to selection in combined_modes()

    :param list_of_checks: list of IntVars relative to each checkbox
    """
    global top_main
    if top_main:
        top_main.destroy()

    top_main = tk.Toplevel(root)
    top_main.title("Mode combiné - résultats")

    if all(element.get() == 0 for element in list_of_checks) or not generate_profils():
        tk.Label(top_main, text="Aucun résultat a communiqué").pack()
    else:
        tk.Label(top_main, text="Mode de vote").grid(row=0, column=0)
        tk.Label(top_main, text="Gagnant").grid(row=0, column=1)
        tk.Label(top_main, text="Départage ?").grid(row=0, column=2)
        row_index = 1
        for var_method in list_of_checks:
            if var_method.get() == 1:
                match var_method.__str__():
                    case "approbation":
                        result_approbation = voting_manager.approbation(generate_profils(),
                                                                        int(stringvar_approval_radius.get()) if stringvar_approval_radius.get() != "" else default_approval_radius
                                                                        )
                        tk.Label(top_main, text="Approbation", width=len("Approbation")).grid(row=row_index,
                                                                                              column=0)
                        if result_approbation:
                            tk.Label(top_main, text=str(result_approbation[0]), font=("Mistral", "22", "bold"),
                                     width="5").grid(row=row_index, column=1)
                            tk.Label(top_main,
                                     text="Parmi " + str(result_approbation[2]) if result_approbation[1] else "Non",
                                     width=str(len(str(result_approbation[2]))) if result_approbation[1] else "5").grid(
                                row=row_index, column=2)
                        else:
                            tk.Label(top_main, text="Pas de gagnant", font=("Mistral", "15", "bold"), width="10").grid(
                                row=row_index, column=1)

                        row_index += 1
                    case "borda":
                        borda_max = len(candidates)
                        result_borda = voting_manager.borda(generate_profils(),
                                                            int(stringvar_borda_max.get()) if stringvar_borda_max.get() != "" else borda_max,
                                                            int(stringvar_borda_step.get()) if stringvar_borda_step.get() != "" else 1
                                                            )
                        tk.Label(top_main, text="Borda", width=len("Borda")).grid(row=row_index,
                                                                                  column=0)
                        tk.Label(top_main, text=str(result_borda[0]), font=("Mistral", "22", "bold"), width="5").grid(
                            row=row_index, column=1)
                        tk.Label(top_main, text="Parmi " + str(result_borda[2]) if result_borda[1] else "Non",
                                 width=str(len(str(result_borda[2]))) if result_borda[1] else "5").grid(
                            row=row_index, column=2)
                        row_index += 1
                    case "condorcet":
                        result_condorcet = voting_manager.condorcet(
                            generate_profils(),
                            CondorcetMethod(var_condorcet_method.get()),
                            CondorcetTieBreakingRule(var_condorcet_tie_breaking.get())
                        )
                        if not result_condorcet[1]:
                            tk.Label(top_main, text="Condorcet", width=len("Condorcet")).grid(row=row_index,
                                                                                              column=0)
                            tk.Label(top_main, text=str(result_condorcet[0]), font=("Mistral", "22", "bold"),
                                     width="5").grid(row=row_index, column=1)
                            tk.Label(top_main, text="Non", width="5").grid(row=row_index, column=2)
                            row_index += 1
                        else:
                            if not result_condorcet[2]:
                                tk.Label(top_main, text="Condorcet", width=len("Condorcet")).grid(row=row_index,
                                                                                                  column=0)
                                tk.Label(top_main, text=str(result_condorcet[0]), font=("Mistral", "22", "bold"),
                                         width="5").grid(row=row_index, column=1)
                                tk.Label(top_main, text="Méthode de condorcet utilisée", width="20").grid(
                                    row=row_index + 1, column=0)
                                tk.Label(top_main, text=CondorcetMethod(var_condorcet_method.get()).name,
                                         width="20").grid(row=row_index + 1, column=1)
                                tk.Label(top_main, text="Non", width="5").grid(row=row_index, column=2)
                                row_index += 2
                            else:
                                tk.Label(top_main, text="Condorcet", width=len("Condorcet")).grid(row=row_index,
                                                                                                  column=0)
                                tk.Label(top_main, text=str(result_condorcet[0]), font=("Mistral", "22", "bold"),
                                         width="5").grid(row=row_index, column=1)
                                tk.Label(top_main, text="Méthode de condorcet utilisée", width="25").grid(
                                    row=row_index + 1, column=0)
                                tk.Label(top_main, text=CondorcetMethod(var_condorcet_method.get()).name,
                                         width="20").grid(row=row_index + 1, column=1)
                                tk.Label(top_main, text=CondorcetTieBreakingRule(var_condorcet_tie_breaking.get()).name,
                                         width="20").grid(row=row_index, column=2)
                                row_index += 2
                    case _:
                        func = "voting_manager." + var_method.__str__() + "(generate_profils())"
                        result = eval(func)
                        mode_text = string.capwords(var_method.__str__().replace('_', ' '))
                        tk.Label(top_main, text=mode_text,
                                 width=len(mode_text)).grid(row=row_index, column=0)
                        tk.Label(top_main, text=str(result[0]), font=("Mistral", "22", "bold"), width="5").grid(
                            row=row_index, column=1)
                        tk.Label(top_main, text="Parmi " + str(result[2]) if result[1] else "Non",
                                 width=str(len(str(result[2]))) if result[1] else "5").grid(row=row_index, column=2)
                        row_index += 1


def show_condorcet(profils):
    """
    Show a popup asking the user to choose the Condorcet method and tie-breaking rule.

    :param profils: Scores for each voter
    """
    top_main = tk.Toplevel(root)
    top_main.title("Condorcet")

    var_condorcet_tie_breaking.set(0)
    var_condorcet_method.set(0)

    tk.Label(top_main, text="Choisir le mode de Condorcet souhaité :").pack()

    tk.Radiobutton(
        top_main, text="Méthode de Copeland", variable=var_condorcet_method, value=CondorcetMethod.COPELAND.value,
        anchor="w"
    ).pack(fill="both")

    tk.Radiobutton(
        top_main, text="Méthode de Simpson", variable=var_condorcet_method, value=CondorcetMethod.SIMPSON.value,
        anchor="w"
    ).pack(fill="both")

    tk.Label(top_main, text="Choisir le mode de départage souhaité :").pack()

    tk.Radiobutton(
        top_main, text="Random", variable=var_condorcet_tie_breaking, value=CondorcetTieBreakingRule.RANDOM.value,
        anchor="w"
    ).pack(fill="both")

    tk.Radiobutton(
        top_main, text="Ordre lexicographique", variable=var_condorcet_tie_breaking,
        value=CondorcetTieBreakingRule.ORDRE_LEXICO.value, anchor="w"
    ).pack(fill="both")

    tk.Button(
        top_main,
        text="Valider",
        command=lambda: [
            display_condorcet_winner(
                voting_manager.condorcet(
                    profils,
                    CondorcetMethod(var_condorcet_method.get()),
                    CondorcetTieBreakingRule(var_condorcet_tie_breaking.get())
                ),
                CondorcetMethod(var_condorcet_method.get()),
                CondorcetTieBreakingRule(var_condorcet_tie_breaking.get())
            ),
            top_main.destroy(),
        ],
    ).pack()


def show_voting_systems():
    # If a top level window is active, close it
    global top
    if top:
        top.destroy()

    # If profils is null, there are no voters or no candidates: show an error dialog
    if not generate_profils() or len(voters) == 0 or len(candidates) == 0:
        tk.messagebox.showwarning(
            title="Données insuffisantes",
            message="Veuillez ajouter des votants et des candidats.",
        )
    else:
        # Create a new top level window to display the different voting systems to choose from
        top = tk.Toplevel(root)
        top.title("Systèmes de vote")

        # Pluralité Simple button
        btn_pluralite_simple = tk.Button(top, text="Pluralité Simple", height=7, width=20,
                                         command=lambda: display_winner(
                                             voting_manager.pluralite_simple(generate_profils()), "Pluralité Simple"))
        btn_pluralite_simple.grid(row=0, column=0)

        # Approbation button
        btn_approbation = tk.Button(top, text="Approbation", height=7, width=20,
                                    command=lambda: show_approbation(generate_profils()))
        btn_approbation.grid(row=0, column=1)

        # Borda button
        btn_borda = tk.Button(top, text="Borda", height=7, width=20,
                              command=lambda: show_borda(generate_profils()))
        btn_borda.grid(row=1, column=0)

        # Élimination Successive button
        btn_elimination_successive = tk.Button(top, text="Élimination Successive", height=7, width=20,
                                               command=lambda: display_winner(
                                                   voting_manager.elimination_successive(generate_profils()),
                                                   "Élimination Successive (STV)"))
        btn_elimination_successive.grid(row=1, column=1)

        # Veto button
        btn_veto = tk.Button(top, text="Veto", height=7, width=20,
                             command=lambda: display_winner(voting_manager.veto(generate_profils()), "Veto"))
        btn_veto.grid(row=2, column=0)

        # Condorcet button
        btn_condorcet = tk.Button(top, text="Condorcet", height=7, width=20,
                                  command=lambda: show_condorcet(generate_profils()))
        btn_condorcet.grid(row=2, column=1)

        # Combined mode button
        btn_mult = tk.Button(
            top, text="Modes combinés", height=7, width=45, command=combined_modes
        )
        btn_mult.grid(row=3, column=0, columnspan=2)


def display_winner(winner: tuple[str, bool, list] | None, method: str):
    """
    Display winner in a popup.

    :param winner: Tuple of (winner, boolean specifying if raw-win or not, list of opponents if not raw-win)
    :param method: The name of the voting method
    """
    global winner_dialog
    if winner_dialog:
        winner_dialog.destroy()

    winner_dialog = tk.Toplevel(root)
    winner_dialog.protocol('WM_DELETE_WINDOW',
                           lambda: [graph_manager.clear_approbation_circles(), graph_manager.build(),
                                    winner_dialog.destroy()])
    winner_dialog.title("Vainqueur selon " + method)

    if winner is None:
        tk.Label(winner_dialog, text="Il n'y a pas de gagnant").pack()
        winner_dialog.geometry("270x40")
    else:
        tk.Label(winner_dialog, text="Le gagnant selon le système " + method + " est :").pack()

        tk.Label(winner_dialog, text=winner[0], font=("Mistral", "25", "normal")).pack()

        if winner[1]:
            tk.Label(winner_dialog, text="Ce candidat a gagné par départage parmi les concurrents suivants :").pack()
            tk.Label(winner_dialog, text=str(winner[2])).pack()
            tk.Label(winner_dialog, text="La règle de départage utilisée correspond à l'ordre alphabétique").pack()
        else:
            tk.Label(winner_dialog, text="Il n'y a pas eu de départage").pack()


def display_condorcet_winner(
        winner: tuple[str, bool, bool, list | None] | None,
        method: CondorcetMethod,
        tie_breaking_rule: CondorcetTieBreakingRule
):
    """
    Display Condorcet winner in a popup.

    :param winner: Tuple of (
                    winner,
                    boolean specifying if the condorcet method has been used or not,
                    boolean specifying if raw-win or not,
                    list of opponents if not raw-win
                )
    :param method: Method to use in case there is no Condorcet winner
    :param tie_breaking_rule: Tie-breaking rule to use in order to decide who wins
    """
    winner_label, is_method_used, is_tie_breaking_used, all_winners = winner

    global winner_dialog
    if winner_dialog:
        winner_dialog.destroy()

    winner_dialog = tk.Toplevel(root)
    winner_dialog.protocol('WM_DELETE_WINDOW', lambda: winner_dialog.destroy())
    winner_dialog.title("Gagnant selon Condorcet")

    if not is_method_used:
        tk.Label(winner_dialog, text="Il y a un vainqueur de Condorcet (gagne tous ses duels) :").pack()
        tk.Label(winner_dialog, text=winner_label, font=("Mistral", "25", "normal")).pack()
    else:
        tk.Label(winner_dialog,
                 text="Il n'y a pas eu de vainqueur de Condorcet, et la méthode utilisée est celle de " + method.name).pack()

        if not is_tie_breaking_used:
            tk.Label(winner_dialog, text="Un unique candidat a gagné :").pack()
            tk.Label(winner_dialog, text=winner_label, font=("Mistral", "25", "normal")).pack()
            tk.Label(winner_dialog, text="Il n'y a pas eu de départage").pack()
        else:
            tk.Label(winner_dialog, text="Un candidat a gagné par départage :").pack()
            tk.Label(winner_dialog, text=winner_label, font=("Mistral", "25", "normal")).pack()
            tk.Label(winner_dialog, text="La règle de départage utilisée est " + tie_breaking_rule.name).pack()
            tk.Label(winner_dialog, text="Les concurrents suivants ont perdu à cause du départage :").pack()
            all_winners.remove(winner_label)
            tk.Label(winner_dialog, text=str(all_winners)).pack()


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

# Generate the profiles on button click
btn_show_voting_systems = tk.Button(root, text="Systèmes de vote", command=show_voting_systems)
btn_show_voting_systems.place(relx=0.25, rely=1 - 0.05, relwidth=0.25, relheight=0.05)

# Distribute the voters on button click
distribute_voters = tk.Button(
    root,
    text="Distribuer les votants",
    command=lambda: show_distribute_popup(stringvar_number_voters, is_voter=True)
)
distribute_voters.place(relx=0.5, rely=1 - 0.05, relwidth=0.25, relheight=0.05)

# Distribute the candidates on button click
distribute_candidates = tk.Button(
    root,
    text="Distribuer les candidats",
    command=lambda: show_distribute_popup(stringvar_number_candidates, is_voter=False)
)
distribute_candidates.place(relx=0.75, rely=1 - 0.05, relwidth=0.25, relheight=0.05)

# Start the tkinter event loop
root.mainloop()
