import math
import random
import string

import numpy as np
import tkinter as tk
from tkinter import filedialog as fd
from tkinter.colorchooser import askcolor
from PIL import Image, ImageTk

from keyboard_manager import KeyboardManager
from candidate import Candidate
from data_manager import DataManager
from graph_manager import GraphManager
from file_manager import FileManager
from tooltip import bind_tooltip
from voter import Voter
from voting_manager import VotingManager, CondorcetMethod, CondorcetTieBreakingRule

# Create a Data Manager
data_manager = DataManager()

# Create a Voting Manager
voting_manager = VotingManager()

# Create a Keyboard Manager
keyboard_manager = KeyboardManager()

# Create a File Manager
file_manager = FileManager()

# Create a Details Voting Manager
voting_details_manager = voting_manager.voting_details_manager

# Create the main tkinter window
root = tk.Tk()
root.title("Simulation Elections")
root.geometry("900x750")
root.option_add('*Font', 'Mistral 12')

# Prepare base layout: PanedWindow capable of fitting two panels
root_container = tk.PanedWindow(root, orient=tk.HORIZONTAL)
root_container.pack(fill=tk.BOTH, expand=True)

# 1. Lay out left panel which allows candidate editing
left_panel = tk.Frame(root_container)
left_panel.pack(side=tk.LEFT, fill=tk.Y)

# 1.1. Add a title to the left panel
tk.Label(left_panel, text="Les candidats").pack(side=tk.TOP, pady=20)

# 1.2. Add the candidates list
list_box__candidates = tk.Listbox(left_panel, takefocus=0, selectmode=tk.SINGLE)
list_box__candidates.pack(side=tk.LEFT, fill=tk.BOTH)

# 2. Lay out main panel which shows the graph and other stuff
main_panel = tk.Frame(root_container)
main_panel.pack(side=tk.RIGHT)

# 2.1. Create a graph manager and build it
graph_manager = GraphManager(main_panel)
graph_manager.build()

# Variable to keep track of the "shift" key press
is_shift_pressed = False

# Variables to keep track of the popup windows
top = None
winner_dialog = None
combined_results_popup = None
edit_candidate_popup = None

# Create the StringVar used to hold the requested number of candidates
stringvar_number_candidates = tk.StringVar(name="number_candidates")

# Create the StringVar used to hold the requested number of voters
stringvar_number_voters = tk.StringVar(name="number_voters")

# Default value for nb candidates/voters
default_nb_candidates_voters = 10
gaussian_nb_voters = 50

# Create the DoubleVar used to track the spread percentage for the gaussian distribution
doublevar_spread_percentage_value = tk.DoubleVar(value=50)
# Min and max values for the slider
min_spread_percentage = 10
max_spread_percentage = 100

# Create the variables to keep track of the 'gaussian distribution' button press
is_clicked_gaussian = False
is_voter_gaussian = False

# Variables to keep track of height and width of buttons
button_height = 0.05
button_width = 0.25

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


def lift_window(window):
    """
    Disables the topmost attribute after it is at the front to prevent permanent focus.
    :param window: The frame to lift.
    """
    window.attributes('-topmost', True)
    window.attributes('-topmost', False)
    window.focus_force()
    window.bell()


def show_edit_candidate_popup(event):
    """
    Displays popup to edit candidates.
    """
    clicked_candidate_index, = list_box__candidates.curselection()
    clicked_candidate = data_manager.get_candidate_at(clicked_candidate_index)

    global edit_candidate_popup
    if edit_candidate_popup and edit_candidate_popup.winfo_exists():
        lift_window(edit_candidate_popup)
        if edit_candidate_popup.candidate_label == clicked_candidate.get_label():
            return

        discard_open_popup = tk.messagebox.askyesno(
            message="Un autre candidat est en cours de modification.\n"
                    "Voulez-vous les ignorer et modifier le candidat sélectionné ?"
        )
        if discard_open_popup:
            edit_candidate_popup.destroy()
        else:
            return

    edit_candidate_popup = tk.Toplevel(root)
    edit_candidate_popup.candidate_label = clicked_candidate.get_label()
    edit_candidate_popup.title("Modifier le candidat")

    label_title = tk.Label(edit_candidate_popup, text="Nom du candidat :")
    label_title.pack()

    stack_horizontal = tk.Frame(edit_candidate_popup)
    stack_horizontal.pack(padx=10)

    color_picker = tk.Frame(stack_horizontal, width=21, height=21, background=clicked_candidate.get_color(), cursor="spraycan")
    color_picker.pack(side=tk.LEFT)
    color_picker.bind("<Button-1>", lambda e: e.widget.configure(bg=askcolor(color=e.widget["bg"])[1]))

    stringvar_edit_candidate_name = tk.StringVar(name="edit_candidate_name", value=clicked_candidate.get_label())
    entry = tk.Entry(stack_horizontal, width=20, textvariable=stringvar_edit_candidate_name)
    entry.pack(side=tk.RIGHT)

    button = tk.Button(
        edit_candidate_popup,
        text="Valider",
        command=lambda: (edit_candidate_popup.destroy() if data_manager.edit_candidate_at(
            index=clicked_candidate_index,
            label=stringvar_edit_candidate_name.get(),
            color=color_picker["bg"]
        ) else None)
    )
    button.pack()


list_box__candidates.bind('<Double-1>', show_edit_candidate_popup)


def on_voter_added(voter: Voter, index: int):
    """
    Callback function for when a voter is added to the data.

    :param voter: newly added voter
    :param index: index of the new voter
    """
    # Add voter on the graph
    graph_manager.add_voter(voter)


def on_voters_cleared():
    """
    Callback function for when all voters are cleared from data.
    """
    graph_manager.clear_voters()
    graph_manager.build()


def on_candidate_added(candidate: Candidate, index: int):
    """
    Callback function for when a candidate is added to the data.

    :param candidate: newly added candidate
    :param index: index of the new candidate
    """
    # Add candidate on the graph
    graph_manager.add_candidate(candidate)

    # Add candidate in left panel
    list_box__candidates.insert(index, candidate.get_label())


def on_candidate_edited(candidate: Candidate, index: int):
    """
    Callback function for when a candidate is edited in the data.

    :param candidate: updated candidate data class
    :param index: index of the edited candidate
    """
    graph_manager.edit_candidate_at(index, candidate)
    graph_manager.build()

    list_box__candidates.delete(index)
    list_box__candidates.insert(index, candidate.get_label())


def on_candidates_cleared():
    """
    Callback function for when all candidates are cleared from data.
    """
    graph_manager.clear_candidates()
    graph_manager.build()
    list_box__candidates.delete(0, tk.END)


def on_candidate_error(error: str):
    """
    Callback function for when an error occurs with a candidate.
    """
    tk.messagebox.showerror(message=error)


# Bind callback functions with Data Manager
data_manager.set_voter_added_callback(on_voter_added)
data_manager.set_voters_cleared_callback(on_voters_cleared)
data_manager.set_candidate_added_callback(on_candidate_added)
data_manager.set_candidate_edited_callback(on_candidate_edited)
data_manager.set_candidates_cleared_callback(on_candidates_cleared)
data_manager.set_candidate_error_callback(on_candidate_error)


def on_key_press(event):
    """
    Callback function to handle the key press event.

    :param event: key press event
    """
    # Here, we're using it to keep track of shift press/release
    if "shift" in event.keysym.lower():
        global is_shift_pressed
        is_shift_pressed = True


def on_key_release(event):
    """
    Callback function to handle the key release event.

    :param event: key release event
    """
    # Here, we're using it to keep track of shift press/release
    if "shift" in event.keysym.lower():
        global is_shift_pressed
        is_shift_pressed = False


# Bind callback functions with KeyPress and KeyRelease events
root.bind("<KeyPress>", on_key_press)
root.bind("<KeyRelease>", on_key_release)


def disable_all_buttons(disable: bool):
    """
    Function to modify the state of all buttons (enable or disable).

    :param disable: bool - if True, disable all buttons, else return them to normal state
    """
    global reset_voters, reset_candidates, generate_utility, btn_show_voting_systems, \
        distribute_voters, distribute_candidates, export_file, import_file

    list_buttons = [reset_voters, reset_candidates, generate_utility, btn_show_voting_systems,
                    distribute_voters, distribute_candidates, export_file, import_file]

    for button in list_buttons:
        if disable:
            button.configure(state=tk.DISABLED, cursor="X_cursor")
        else:
            global is_clicked_gaussian
            is_clicked_gaussian = False
            if button == reset_voters or button == reset_candidates:
                button.configure(state=tk.NORMAL, cursor="exchange")
            else:
                button.configure(state=tk.NORMAL, cursor="arrow")

    if disable:
        root.bind("<Escape>", lambda e: disable_all_buttons(False))


def on_click_gaussian(is_voter: bool):
    """
    Function to update the value of global variables once 'gaussian distribution' button is clicked.
    These variables are then used to determine whether to plot a normal voter/candidate on click, or to apply a gaussian distribution.
    Disables all buttons until 'distribute_gaussian' function is called.

    :param is_voter: bool(voters?) - if True, distribute voters in gaussian distribution, else candidates
    """
    global is_clicked_gaussian
    is_clicked_gaussian = True

    global is_voter_gaussian
    is_voter_gaussian = is_voter

    disable_all_buttons(True)


def on_graph_click(event):
    """
    Callback function to handle clicking on the graph.

    :param event: click event
    """
    # Get the x and y coordinates of the click event
    x = event.xdata
    y = event.ydata

    # If gaussian distribution is activated, plot voters/candidates accordingly
    global is_clicked_gaussian
    if is_clicked_gaussian:
        is_clicked_gaussian = False
        distribute_gaussian(x, y)
        return

    # Add the point to the list of points, only if clicked inside the graph
    if x is not None and -1 <= x <= 1 and y is not None and -1 <= y <= 1:
        # If the shift key is pressed, add candidates instead of voters
        if is_shift_pressed:
            # Candidate :
            data_manager.add_candidate((x, y))
        else:
            # Voter :
            data_manager.add_voter((x, y))

        # Build the graph: redraw the canvas
        graph_manager.build()


# Bind the callback function with the button press event
graph_manager.bind("button_press_event", on_graph_click)


def validate_candidates_voters_number(*args):
    """
    Function to validate the given input (the number of candidates or voters).

    :param args: variable to validate
    """
    if args[0] == "number_voters":
        value = stringvar_number_voters
    elif args[0] == "number_candidates":
        value = stringvar_number_candidates

    if not (value.get()).isdigit() and value.get() != "":
        value.set(log.get())
    else:
        log.set(value.get())


def reset(candidates: bool = False, voters: bool = False):
    """
    Function to clear the candidates/voters.

    :param candidates: bool(should the function clear candidates?) - default is False
    :param voters: bool(should the function clear voters?) - default is False
    """
    if candidates:
        # Candidates :
        if data_manager.is_candidates_empty():
            tk.messagebox.showerror(title="Candidats déjà réinitialisés", message="Candidats déjà réinitialisés")
        else:
            data_manager.clear_candidates()

    if voters:
        # Voters :
        if data_manager.is_voters_empty():
            tk.messagebox.showerror(title="Votants déjà réinitialisés", message="Votants déjà réinitialisés")
        else:
            data_manager.clear_voters()


top_main = None


def show_distribute_popup(is_voter: bool):
    """
    Function to show a popup, handle the input and distribute candidates/voters.

    :param is_voter: bool(distribute voters?) - if False, will distribute candidates
    """
    s = "votants" if is_voter else "candidats"

    global top_main
    if top_main:
        top_main.destroy()

    top_main = tk.Toplevel(root)
    top_main.title("Choisir le nombre de " + s)
    top_main.geometry("255x230")

    label_title = tk.Label(top_main, text="Donner le nombre de " + s + " :")
    label_title.grid(row=0, column=0)

    global log
    log = tk.StringVar()
    stringvar_number = stringvar_number_voters if is_voter else stringvar_number_candidates
    stringvar_number.trace_variable("w", validate_candidates_voters_number)
    entry = tk.Entry(top_main, width=20, textvariable=stringvar_number)
    entry.grid(row=1, column=0)

    if is_voter:
        gaussian_nb = gaussian_nb_voters
    else:
        gaussian_nb = default_nb_candidates_voters

    label_hint = tk.Label(
        top_main,
        text="Laisser vide pour valeur de défaut:\n" + str(
            default_nb_candidates_voters) + " pour distribution uniforme\n" + str(
            gaussian_nb) + " pour distribution gaussienne"
    )
    label_hint.grid(row=2, column=0)

    button_uniforme = tk.Button(
        top_main,
        text="Distribution uniforme des " + s,
        command=lambda: [distribute(is_voter), top_main.destroy()]
    )
    button_uniforme.grid(row=3, column=0)

    tk.Label(top_main, text="Choisir la quantité de propagation (en %) :").grid(row=4, column=0)

    sigma = tk.Scale(top_main, from_=min_spread_percentage, to=max_spread_percentage, resolution=1, length=200,
                     orient=tk.HORIZONTAL, variable=doublevar_spread_percentage_value)
    sigma.grid(row=5, column=0)

    button_gaussian = tk.Button(
        top_main,
        text="Distribution gaussienne des " + s,
        command=lambda: [on_click_gaussian(is_voter), top_main.destroy()]
    )
    button_gaussian.grid(row=6, column=0)

    keyboard_manager.focus_enter_bind(top_main)
    keyboard_manager.esc_bind(top_main)


def distribute(is_voter: bool):
    """
    Function to distribute the candidates/voters randomly on the graph.

    :param is_voter: bool(distribute voters?) - if False, will distribute candidates
    """
    stringvar_number = stringvar_number_voters if is_voter else stringvar_number_candidates
    if stringvar_number.get() != "":
        nb = int(stringvar_number.get())
    else:
        nb = default_nb_candidates_voters

    for i in range(nb):
        # Random coordinates
        coordinates = (random.uniform(-1, 1), random.uniform(-1, 1))

        if is_voter:
            # Voter :
            data_manager.add_voter(coordinates)
        else:
            # Candidate :
            data_manager.add_candidate(coordinates)

    # Build the graph: redraw the canvas
    graph_manager.build()


def distribute_gaussian(x: float, y: float):
    """
    Function to distribute the candidates/voters on the graph from a normal (Gaussian) distribution.

    :param x: the x coordinate of the mean (“centre”) of the distribution.
    :param y: the y coordinate of the mean (“centre”) of the distribution.
    """
    if x is not None and y is not None and -1 <= x <= 1 and -1 <= y <= 1:
        stringvar_number = stringvar_number_voters if is_voter_gaussian else stringvar_number_candidates
        if stringvar_number.get() != "":
            nb = int(stringvar_number.get())
        else:
            if is_voter_gaussian:
                nb = gaussian_nb_voters
            else:
                nb = default_nb_candidates_voters

        spread_percentage = doublevar_spread_percentage_value.get()

        sigma = np.interp(spread_percentage, (min_spread_percentage, max_spread_percentage), (0.1, 0.7))

        x_values = np.random.normal(x, sigma, nb**2)
        y_values = np.random.normal(y, sigma, nb**2)

        i = 0
        for xs, ys in zip(x_values, y_values):
            if i == nb:
                break
            if -1 <= xs <= 1 and -1 <= ys <= 1:
                if is_voter_gaussian:
                    data_manager.add_voter((xs, ys))
                else:
                    data_manager.add_candidate((xs, ys))
                i += 1
        graph_manager.build()

    disable_all_buttons(False)


def show_profils_popup():
    """
    Function to show the scores in a popup.
    """
    # If a top level window is active, close it
    global top
    if top:
        top.destroy()

    # The scores for each voter
    profils = generate_profils()

    # List of voters
    voters = data_manager.get_voters()

    # List of candidates
    candidates = data_manager.get_candidates()

    if not profils or data_manager.is_voters_empty() or data_manager.is_candidates_empty():
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

        keyboard_manager.esc_bind(top)


def generate_profils():
    """
    Function to generate the scores.

    :return: dict({..., <voter label>: list(..., tuple(<candidate label>, <approval ratio>), ...), ...})
    """
    # Dictionary to store the scores for each voter
    profils = dict()

    # Calculates the max distance (diagonal) of the plot
    maximum = graph_manager.get_diagonal()

    # List of voters
    voters = data_manager.get_voters()

    # List of candidates
    candidates = data_manager.get_candidates()

    # Loop to calculate the scores for each voter
    for voter in voters:
        # profil = list(...tuple(<candidate label>, <approval ratio>)...)
        profil = list(map(
            lambda candidate:
            (
                candidate.get_label(),
                (maximum - math.dist(voter.coordinates(), candidate.coordinates())) / maximum
            ),
            candidates
        ))
        # Sort by closest match
        profil.sort(key=lambda x: x[1], reverse=True)
        # profils = dict({...<voter label>: <profil>...})
        profils[voter.get_label()] = profil

    return profils


def validate_approval_radius(*args):
    """
    Function to validate the input given (the number of candidates or voters).

    :param args: variable to validate
    """
    if (not (stringvar_approval_radius.get()).isdigit() or int(
            stringvar_approval_radius.get()) > 100) and stringvar_approval_radius.get() != "":
        stringvar_approval_radius.set(log.get())
    else:
        log.set(stringvar_approval_radius.get())


def show_approbation_popup(profils, is_multiple_method):
    """
    Show a popup asking the user for the approval circle's radius.

    :param profils: Scores for each voter
    :param is_multiple_method: boolean to check if we need the "multiple method" version or not
    """
    global top_approbation
    top_approbation = tk.Toplevel(root)
    top_approbation.title("Rayon d'approbation")

    tk.Label(top_approbation, text="Rayon d'approbation (pourcentage) :").pack()

    global log
    log = tk.StringVar()
    stringvar_approval_radius.trace_variable("w", validate_approval_radius)
    entry = tk.Entry(top_approbation, width=20, textvariable=stringvar_approval_radius)
    entry.pack()

    tk.Label(
        top_approbation,
        text="Laisser vide pour valeur de défaut (" + str(default_approval_radius) + "%)"
    ).pack()

    button = tk.Button(
        top_approbation, text="Valider", command=lambda: top_approbation.destroy()
    )
    button.pack()

    on_popup_closed = lambda e=None: on_multiple_mode_option_closed("approbation")

    if is_multiple_method:
        button.configure(command=lambda: top_approbation.destroy())
        top_approbation.protocol("WM_DELETE_WINDOW", on_popup_closed)
    else:
        button.configure(
            command=lambda: [
                calculate_approbation(
                    profils,
                    int(stringvar_approval_radius.get()) if stringvar_approval_radius.get() != "" else default_approval_radius
                ),
                top_approbation.destroy()
            ]
        )

    keyboard_manager.enter_bind(top_approbation, button)
    if is_multiple_method:
        keyboard_manager.esc_bind(top_approbation, on_popup_closed)
    else:
        keyboard_manager.esc_bind(top_approbation)


def validate_borda(*args):
    """
    Verify the entry in show_borda().
    The entry should be a digit, not equal to zero and less than the number of
    total candidates.
    The function sets the value of the stringvar at the end

    :param args: variable to validate
    """
    strvar = stringvar_borda_max if args[0] == "borda_max" else stringvar_borda_step

    if (not (strvar.get()).isdigit() or int(
            strvar.get()) > borda_max or int(strvar.get()) == 0) and strvar.get() != "":
        strvar.set(log.get())
    else:
        log.set(strvar.get())


def show_borda_popup(profils, is_multiple_method):
    """
    Show a popup asking the user for the maximum score attribution in borda.

    :param is_multiple_method: boolean to check if we need the "multiple method" version or not
    :param profils: Scores for each voter
    """
    global top_borda
    top_borda = tk.Toplevel(root)
    top_borda.title("Score maximum - Borda")

    global borda_max
    borda_max = len(data_manager.get_candidates())

    tk.Label(top_borda,
             text="Score maximum (inférieur au nombre de candidats : " + str(borda_max) + ") :").pack()

    global log
    log = tk.StringVar()
    stringvar_borda_max.trace_variable("w", validate_borda)
    entry = tk.Entry(top_borda, width=20, textvariable=stringvar_borda_max)
    entry.pack()

    tk.Label(top_borda, text="Pas de score entre deux candidats : ").pack()

    global log2
    log2 = tk.StringVar()
    stringvar_borda_step.trace_variable("w", validate_borda)
    entry2 = tk.Entry(top_borda, width=20, textvariable=stringvar_borda_step)
    entry2.pack()

    tk.Label(
        top_borda,
        text="Laisser vide pour valeur de défaut (nombre de candidats=" + str(borda_max) + ", pas=1)"
    ).pack()

    button = tk.Button(top_borda, text="Valider")
    button.pack()

    on_popup_closed = lambda e=None: on_multiple_mode_option_closed("borda")

    if is_multiple_method:
        button.configure(command=lambda: top_borda.destroy())
        top_borda.protocol("WM_DELETE_WINDOW", on_popup_closed)
    else:
        button.configure(
            command=lambda: [
                show_winner_popup(
                    voting_manager.borda(
                        profils,
                        int(stringvar_borda_max.get()) if stringvar_borda_max.get() != "" else borda_max,
                        int(stringvar_borda_step.get()) if stringvar_borda_step.get() != "" else 1
                    ), "Borda"
                ),
                top_borda.destroy()
            ]
        )

    keyboard_manager.enter_bind(top_borda, button)
    if is_multiple_method:
        keyboard_manager.esc_bind(top_borda, on_popup_closed)
    else:
        keyboard_manager.esc_bind(top_borda)


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
    show_winner_popup(winner, "Approbation")


def on_multiple_mode_option_closed(var):
    """
    Allows to uncheck the checkbox if user decides to close the window without validating input

    :param var: the concerned method StringVar
    """
    if var == "approbation":
        var_approbation.set(0)
        top_approbation.destroy()
    if var == "borda":
        var_borda.set(0)
        top_borda.destroy()
    if var == "condorcet":
        var_condorcet.set(0)
        top_condorcet.destroy()


def show_combined_voting_systems_popup():
    """
    Allows user to select different modes and calls show_mult_methods to display the different winners.
    """
    global top_combined_mode
    top_combined_mode = tk.Toplevel(root)
    top_combined_mode.title("Mode combiné")

    label_title = tk.Label(
        top_combined_mode, text="Choisir parmi les modes suivants ceux souhaités :"
    )
    label_title.pack()

    var_pluralite_simple = tk.IntVar(name="pluralite_simple")
    check_plualite_simple = tk.Checkbutton(
        top_combined_mode, text="Pluralité simple", variable=var_pluralite_simple, anchor="w"
    )
    check_plualite_simple.pack(fill="both")

    global var_approbation
    var_approbation = tk.IntVar(name="approbation")
    check_approbation = tk.Checkbutton(
        top_combined_mode, text="Approbation", variable=var_approbation, anchor="w"
    )
    check_approbation.pack(fill="both")
    var_approbation.trace(
        "w",
        lambda *args: [
            show_approbation_popup(generate_profils(), True) if var_approbation.get() == 1 else None
        ]
    )

    global var_borda
    var_borda = tk.IntVar(name="borda")
    var_borda.trace(
        "w",
        lambda *args: [
            show_borda_popup(generate_profils(), True) if var_borda.get() == 1 else None
        ]
    )
    check_borda = tk.Checkbutton(top_combined_mode, text="Borda", variable=var_borda, anchor="w")
    check_borda.pack(fill="both")

    var_elim_succ = tk.IntVar(name="elimination_successive")
    check_elim_succ = tk.Checkbutton(
        top_combined_mode, text="Elimination succéssive", variable=var_elim_succ, anchor="w"
    )
    check_elim_succ.pack(fill="both")

    var_veto = tk.IntVar(name="veto")
    check_veto = tk.Checkbutton(top_combined_mode, text="Veto", variable=var_veto, anchor="w")
    check_veto.pack(fill="both")

    global var_condorcet
    var_condorcet = tk.IntVar(name="condorcet")
    var_condorcet.trace(
        "w",
        lambda *args: [
            show_condorcet_popup(generate_profils(), True) if var_condorcet.get() == 1 else None
        ]
    )
    check_condorcet = tk.Checkbutton(top_combined_mode, text="Condorcet", variable=var_condorcet, anchor="w")
    check_condorcet.pack(fill="both")

    button = tk.Button(
        top_combined_mode,
        text="Valider",
        command=lambda: display_multiple_voting_systems_winner(
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

    keyboard_manager.focus_enter_bind(top_combined_mode)
    keyboard_manager.esc_bind(top_combined_mode)


def display_multiple_voting_systems_winner(list_of_checks: list):
    """
    Displays the winners according to different voting methods according to selection in combined_modes()

    :param list_of_checks: list of IntVars relative to each checkbox
    """
    global combined_results_popup
    if combined_results_popup:
        combined_results_popup.destroy()

    combined_results_popup = tk.Toplevel(root)
    combined_results_popup.title("Mode combiné - résultats")

    if all(element.get() == 0 for element in list_of_checks) or not generate_profils():
        tk.Label(combined_results_popup, text="Aucun résultat a communiqué").pack()
    else:
        tk.Label(combined_results_popup, text="Mode de vote").grid(row=0, column=0)
        tk.Label(combined_results_popup, text="Gagnant").grid(row=0, column=1)
        tk.Label(combined_results_popup, text="Départage ?").grid(row=0, column=2)
        row_index = 1
        for var_method in list_of_checks:
            if var_method.get() == 1:
                match var_method.__str__():
                    case "approbation":
                        result_approbation = voting_manager.approbation(generate_profils(),
                                                                        int(stringvar_approval_radius.get()) if stringvar_approval_radius.get() != "" else default_approval_radius
                                                                        )
                        tk.Label(combined_results_popup, text="Approbation", width=len("Approbation")).grid(
                            row=row_index,
                            column=0)
                        if result_approbation:
                            tk.Label(combined_results_popup, text=str(result_approbation[0]),
                                     font=("Mistral", "22", "bold"),
                                     width="5").grid(row=row_index, column=1)
                            tk.Label(combined_results_popup,
                                     text="Parmi " + str(result_approbation[2]) if result_approbation[1] else "Non",
                                     width=str(len(str(result_approbation[2]))) if result_approbation[1] else "5").grid(
                                row=row_index, column=2)
                        else:
                            tk.Label(combined_results_popup, text="Pas de gagnant", font=("Mistral", "15", "bold"),
                                     width="10").grid(
                                row=row_index, column=1)

                        row_index += 1
                    case "borda":
                        borda_max = len(data_manager.get_candidates())
                        result_borda = voting_manager.borda(generate_profils(),
                                                            int(stringvar_borda_max.get()) if stringvar_borda_max.get() != "" else borda_max,
                                                            int(stringvar_borda_step.get()) if stringvar_borda_step.get() != "" else 1
                                                            )
                        tk.Label(combined_results_popup, text="Borda", width=len("Borda")).grid(row=row_index,
                                                                                                column=0)
                        tk.Label(combined_results_popup, text=str(result_borda[0]), font=("Mistral", "22", "bold"),
                                 width="5").grid(
                            row=row_index, column=1)
                        tk.Label(combined_results_popup,
                                 text="Parmi " + str(result_borda[2]) if result_borda[1] else "Non",
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
                            tk.Label(combined_results_popup, text="Condorcet", width=len("Condorcet")).grid(
                                row=row_index,
                                column=0)
                            tk.Label(combined_results_popup, text=str(result_condorcet[0]),
                                     font=("Mistral", "22", "bold"),
                                     width="5").grid(row=row_index, column=1)
                            tk.Label(combined_results_popup, text="Non", width="5").grid(row=row_index, column=2)
                            row_index += 1
                        else:
                            title = "Condorcet - " + CondorcetMethod(var_condorcet_method.get()).name
                            if not result_condorcet[2]:
                                tk.Label(combined_results_popup, text=title, width=len(title)).grid(row=row_index,
                                                                                                    column=0)
                                tk.Label(combined_results_popup, text=str(result_condorcet[0]),
                                         font=("Mistral", "22", "bold"),
                                         width="5").grid(row=row_index, column=1)
                                tk.Label(combined_results_popup, text="Non", width="5").grid(row=row_index, column=2)
                                row_index += 1
                            else:
                                tk.Label(combined_results_popup, text=title, width=len(title)).grid(row=row_index,
                                                                                                    column=0)
                                tk.Label(combined_results_popup, text=str(result_condorcet[0]),
                                         font=("Mistral", "22", "bold"),
                                         width="5").grid(row=row_index, column=1)
                                tk.Label(combined_results_popup,
                                         text=CondorcetTieBreakingRule(var_condorcet_tie_breaking.get()).name,
                                         width="20").grid(row=row_index, column=2)
                                row_index += 1
                    case _:
                        func = "voting_manager." + var_method.__str__() + "(generate_profils())"
                        result = eval(func)
                        mode_text = string.capwords(var_method.__str__().replace('_', ' '))
                        tk.Label(combined_results_popup, text=mode_text,
                                 width=len(mode_text)).grid(row=row_index, column=0)
                        tk.Label(combined_results_popup, text=str(result[0]), font=("Mistral", "22", "bold"),
                                 width="5").grid(
                            row=row_index, column=1)
                        tk.Label(combined_results_popup, text="Parmi " + str(result[2]) if result[1] else "Non",
                                 width=str(len(str(result[2]))) if result[1] else "5").grid(row=row_index, column=2)
                        row_index += 1

    keyboard_manager.esc_bind(combined_results_popup)


def show_condorcet_popup(profils, is_multiple_method):
    """
    Show a popup asking the user to choose the Condorcet method and tie-breaking rule.

    :param profils: Scores for each voter
    :param is_multiple_method: boolean to check if we need the "multiple method" version or not
    """
    global top_condorcet
    top_condorcet = tk.Toplevel(root)
    top_condorcet.title("Condorcet")

    var_condorcet_tie_breaking.set(0)
    var_condorcet_method.set(0)

    tk.Label(top_condorcet, text="Choisir le mode de Condorcet souhaité :").pack()

    radio_copeland = tk.Radiobutton(
        top_condorcet, text="Méthode de Copeland", variable=var_condorcet_method, value=CondorcetMethod.COPELAND.value,
        anchor="w"
    )
    radio_copeland.pack(fill="both")

    radio_simpson = tk.Radiobutton(
        top_condorcet, text="Méthode de Simpson", variable=var_condorcet_method, value=CondorcetMethod.SIMPSON.value,
        anchor="w"
    )
    radio_simpson.pack(fill="both")

    tk.Label(top_condorcet, text="Choisir le mode de départage souhaité :").pack()

    radio_random = tk.Radiobutton(
        top_condorcet, text="Random", variable=var_condorcet_tie_breaking, value=CondorcetTieBreakingRule.RANDOM.value,
        anchor="w"
    )
    radio_random.pack(fill="both")

    radio_order = tk.Radiobutton(
        top_condorcet, text="Ordre lexicographique", variable=var_condorcet_tie_breaking,
        value=CondorcetTieBreakingRule.ORDRE_LEXICO.value, anchor="w"
    )
    radio_order.pack(fill="both")

    button = tk.Button(top_condorcet, text="Valider")
    button.pack()

    on_popup_closed = lambda e=None: on_multiple_mode_option_closed("condorcet")

    if is_multiple_method:
        button.configure(
            command=lambda: top_condorcet.destroy() if var_condorcet_tie_breaking.get() != 0 and var_condorcet_method.get() != 0 else None
        )
        top_condorcet.protocol("WM_DELETE_WINDOW", on_popup_closed)
    else:
        button.configure(command=lambda: [
            display_condorcet_winner_popup(
                voting_manager.condorcet(
                    profils,
                    CondorcetMethod(var_condorcet_method.get()),
                    CondorcetTieBreakingRule(var_condorcet_tie_breaking.get())
                ),
                CondorcetMethod(var_condorcet_method.get()),
                CondorcetTieBreakingRule(var_condorcet_tie_breaking.get())
            ),
            top_condorcet.destroy()
        ]
                         )

    keyboard_manager.focus_enter_bind(top_condorcet)
    if is_multiple_method:
        keyboard_manager.esc_bind(top_condorcet, on_popup_closed)
    else:
        keyboard_manager.esc_bind(top_condorcet)


def show_voting_systems_popup():
    """
    Displays all voting systems in a popup.
    """
    # If a top level window is active, close it
    global top
    if top:
        top.destroy()

    # If profils is null, there are no voters or no candidates: show an error dialog
    if not generate_profils() or data_manager.is_voters_empty() or data_manager.is_candidates_empty():
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
                                         command=lambda: show_winner_popup(
                                             voting_manager.pluralite_simple(generate_profils()), "Pluralité Simple"))
        btn_pluralite_simple.grid(row=0, column=0)

        # Approbation button
        btn_approbation = tk.Button(top, text="Approbation", height=7, width=20,
                                    command=lambda: show_approbation_popup(generate_profils(), False))
        btn_approbation.grid(row=0, column=1)

        # Borda button
        btn_borda = tk.Button(top, text="Borda", height=7, width=20,
                              command=lambda: show_borda_popup(generate_profils(), False))
        btn_borda.grid(row=1, column=0)

        # Élimination Successive button
        btn_elimination_successive = tk.Button(top, text="Élimination Successive", height=7, width=20,
                                               command=lambda: show_winner_popup(
                                                   voting_manager.elimination_successive(generate_profils()),
                                                   "Élimination Successive (STV)"))
        btn_elimination_successive.grid(row=1, column=1)

        # Veto button
        btn_veto = tk.Button(top, text="Veto", height=7, width=20,
                             command=lambda: show_winner_popup(voting_manager.veto(generate_profils()), "Veto"))
        btn_veto.grid(row=2, column=0)

        # Condorcet button
        btn_condorcet = tk.Button(top, text="Condorcet", height=7, width=20,
                                  command=lambda: show_condorcet_popup(generate_profils(), False))
        btn_condorcet.grid(row=2, column=1)

        # Combined mode button
        btn_multiple_voting_systems = tk.Button(
            top, text="Modes combinés", height=7, width=45, command=show_combined_voting_systems_popup
        )
        btn_multiple_voting_systems.grid(row=3, column=0, columnspan=2)

        keyboard_manager.focus_enter_bind(top)
        keyboard_manager.esc_bind(top)


def show_winner_popup(winner: tuple[str, bool, list] | None, method: str):
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

    width_height = 25

    details_image = ImageTk.PhotoImage(Image.open("icons/png_icons/details_icon.png").resize((width_height, width_height)))
    details_button = tk.Button(winner_dialog, image=details_image, command=lambda: voting_details_manager.show_remaining_methods_details(winner_dialog))
    details_button.image = details_image
    bind_tooltip(widget=details_button, text="Voir le détail des votes")
    details_button.grid(row=0, column=0, sticky=tk.W)

    info_image = ImageTk.PhotoImage(Image.open("icons/png_icons/info_icon.png").resize((width_height, width_height)))
    info_button = tk.Button(winner_dialog, image=info_image)
    info_button.image = info_image
    bind_tooltip(widget=info_button, text="Définition du mode de vote")
    info_button.grid(row=0, column=1, sticky=tk.E)

    if method == "Pluralité Simple":
        info_button.configure(command=lambda: voting_details_manager.show_pluralite_simple_information(winner_dialog))
    if method == "Borda":
        maximum = int(stringvar_borda_max.get()) if stringvar_borda_max.get() != '' else len(data_manager.get_candidates())
        step = int(stringvar_borda_step.get()) if stringvar_borda_step.get() != '' else 1
        info_button.configure(command=lambda: voting_details_manager.show_borda_information(maximum, step, winner_dialog))
    if method == "Approbation":
        radius = int(stringvar_approval_radius.get()) if stringvar_approval_radius.get() != '' else default_approval_radius
        info_button.configure(command=lambda: voting_details_manager.show_approbation_information(radius, winner_dialog))
    if method == "Élimination Successive (STV)":
        info_button.configure(command=lambda: voting_details_manager.show_elimination_successive_information(winner_dialog))
        details_button.configure(
            command=lambda: voting_details_manager.show_elimination_successive_steps(winner_dialog))
    if method == "Veto":
        info_button.configure(command=lambda: voting_details_manager.show_veto_information(winner_dialog))

    if winner is None:
        tk.Label(winner_dialog, text="Il n'y a pas de gagnant").grid(row=1, column=0, columnspan=2)
        winner_dialog.geometry("270x40")
    else:
        tk.Label(winner_dialog, text="Le gagnant selon le système " + method + " est :").grid(row=1, column=0, columnspan=2)

        tk.Label(winner_dialog, text=winner[0], font=("Mistral", "25", "normal")).grid(row=2, column=0, columnspan=2)

        if winner[1]:
            tk.Label(winner_dialog, text="Ce candidat a gagné par départage parmi les concurrents suivants :").grid(row=3, column=0, columnspan=2)
            tk.Label(winner_dialog, text=str(winner[2])).grid(row=4, column=0, columnspan=2)
            tk.Label(winner_dialog, text="La règle de départage utilisée correspond à l'ordre alphabétique").grid(row=5, column=0, columnspan=2)
        else:
            tk.Label(winner_dialog, text="Il n'y a pas eu de départage").grid(row=3, column=0, columnspan=2)

    keyboard_manager.focus_enter_bind(winner_dialog)
    event = lambda e: [graph_manager.clear_approbation_circles(), graph_manager.build(),
                       winner_dialog.destroy()]
    keyboard_manager.esc_bind(winner_dialog, event)


def display_condorcet_winner_popup(
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

    width_height = 25

    details_image = ImageTk.PhotoImage(Image.open("icons/png_icons/details_icon.png").resize((width_height, width_height)))
    details_button = tk.Button(winner_dialog, image=details_image, command=lambda: voting_details_manager.show_condorcet_steps(winner_dialog))
    details_button.image = details_image
    bind_tooltip(widget=details_button, text="Voir le détail des votes")
    details_button.grid(row=0, column=0, sticky=tk.W)

    info_image = ImageTk.PhotoImage(Image.open("icons/png_icons/info_icon.png").resize((width_height, width_height)))
    info_button = tk.Button(winner_dialog, image=info_image, command=lambda: voting_details_manager.show_condorcet_information(method, tie_breaking_rule, winner_dialog))
    info_button.image = info_image
    bind_tooltip(widget=info_button, text="Définition du mode de vote")
    info_button.grid(row=0, column=1, sticky=tk.E)

    if not is_method_used:
        tk.Label(winner_dialog, text="Il y a un vainqueur de Condorcet (gagne tous ses duels) :").grid(row=1, column=0, columnspan=2)
        tk.Label(winner_dialog, text=winner_label, font=("Mistral", "25", "normal")).grid(row=2, column=0, columnspan=2)
    else:
        tk.Label(winner_dialog,
                 text="Il n'y a pas eu de vainqueur de Condorcet, et la méthode utilisée est celle de " + method.name).grid(row=1, column=0, columnspan=2)

        if not is_tie_breaking_used:
            tk.Label(winner_dialog, text="Un unique candidat a gagné :").grid(row=2, column=0, columnspan=2)
            tk.Label(winner_dialog, text=winner_label, font=("Mistral", "25", "normal")).grid(row=3, column=0, columnspan=2)
            tk.Label(winner_dialog, text="Il n'y a pas eu de départage").grid(row=4, column=0, columnspan=2)
        else:
            tk.Label(winner_dialog, text="Un candidat a gagné par départage :").grid(row=2, column=0, columnspan=2)
            tk.Label(winner_dialog, text=winner_label, font=("Mistral", "25", "normal")).grid(row=3, column=0, columnspan=2)
            tk.Label(winner_dialog, text="La règle de départage utilisée est " + tie_breaking_rule.name).grid(row=4, column=0, columnspan=2)
            tk.Label(winner_dialog, text="Les concurrents suivants ont perdu à cause du départage :").grid(row=5, column=0, columnspan=2)
            all_winners.remove(winner_label)
            tk.Label(winner_dialog, text=str(all_winners)).grid(row=6, column=0, columnspan=2)

    keyboard_manager.focus_enter_bind(winner_dialog)
    keyboard_manager.esc_bind(winner_dialog)


def import_file_callback(frame):
    """
    Function called on press of 'import file' button.
    Allows user to choose a file and calls import_objects_from_file() function from FileManager.

    :param frame: The popup frame of import file.
    """
    filetypes = (
        ('csv files', '*.csv'),
    )
    name = fd.askopenfilename(initialdir='./files/', filetypes=filetypes)
    if name == '':
        return
    file_manager.import_objects_from_file(name, show_error, on_import_file_success)
    frame.destroy()


top_file = None


def show_import_file_popup():
    """
    Shows popup explaining the format of the file to import.
    Handles user input.
    Calls import_objects_from_file() and gives it the name of a file as input.
    """
    global top_file
    if top_file:
        top_file.destroy()

    top_file = tk.Toplevel(root)
    top_file.title("Lecture d'un fichier")
    top_file.geometry("560x490")

    tk.Label(
        top_file,
        text="Pour importer des données d'un fichier, il doit suivre le format suivant dans toutes ses lignes:\n\n" +
        "La premiere ligne est soit \"Candidats\" soit \"Votants\".\n" +
        "Celles qui suivent doivent avoir un format bien determiné selon le cas:\n" +
        "- Pour les candidats, le format est: \"x,y,nom_candidat,couleur\" avec nom_candidat et couleur des colonnes optionnelles (peuvent être non initialisées).\n" +
        "- Pour les votants, le format est: \"x,y\".\n" +
        "Les colonnes x et y représentent les coordonnées x et y qui doivent être comprises entre [-1,1].\n\n" +
        "Voici un example de fichier valable:\n\n" +
        "Candidats\n" +
        "0.9461039811039915,-0.7889275229678154,A,#ffa62b \
        0.042005706554823385,0.2998445121641913,B \
        0.08606445736472024,-0.5626141086518681 \
        -0.2690871826009764,-0.2698714634871553,D,rien \
        -0.258171091230772,-0.5569398723595189,E,#87a922 \
        -0.29257873438932536,0.7092589293675524,E,#95a3a6 \
        0.8782258064516126,-0.21785714285714275,G,#a87900\n\n" +
        "Votants\n" +
        "-0.6254032258064518,-0.8666666666666666 \
        -0.8471774193548389,0.466666666666667 \
        0.3370967741935482,0.7880952380952386 \
        0.7096774193548385,0.2345238095238098 \
        0.4391129032258063,-0.5809523809523809 \
        -0.3459677419354841,0.317857142857143 \
        -0.554435483870968,-0.2952380952380951 \
        0.20846774193548367,-0.15238095238095206",
        wraplength=530,
        justify="left"
    ).pack()

    import_button = tk.Button(
        top_file,
        text='Choisir un fichier',
        command=lambda: import_file_callback(top_file)
    )
    import_button.pack()
    keyboard_manager.enter_bind(top_file, import_button)
    keyboard_manager.esc_bind(top_file)


def on_import_file_success(file_voters: list[tuple[float, float]], file_candidates: list[tuple[float, float, str, str]]):
    """
    Function called when file is successfully imported. The list of variables/candidates is added on graph.

    :param file_voters: list of voters to add on graph
    :param file_candidates: list of candidates to add on graph
    """
    for x, y, label, color in file_candidates:
        data_manager.add_candidate((x, y), label=label, color=color)
    for voter in file_voters:
        data_manager.add_voter(voter)
    graph_manager.build()


def call_export_file():
    """
    Function that calls export_objects_to_file function in file_manager
    """
    file_manager.export_objects_to_file(data_manager.get_candidates(), data_manager.get_voters(), show_error, show_success)


def show_error(title: str, message: str):
    """
    Function to show error message.

    :param title: the title of message box
    :param message: the message to show in error box
    """
    tk.messagebox.showwarning(title=title, message=message)


def show_success(title: str, message: str):
    """
    Function to show success message.

    :param title: the title of message box
    :param message: the message to show in success box
    """
    tk.messagebox.showinfo(title=title, message=message)


def toggle(event):
    """
    Function to toggle the image shown on the toggle_annotations button depending on its state
    """
    # If toggle_annotations button is on
    if graph_manager.get_toggle_state():
        toggle_annotations.config(image=off)
        graph_manager.set_toggle_state(False)
    else:
        toggle_annotations.config(image=on)
        graph_manager.set_toggle_state(True)
    graph_manager.build()


# Define On/Off Images for toggle button
on = tk.PhotoImage(file="icons/png_icons/show.png")
off = tk.PhotoImage(file="icons/png_icons/hide.png")


def candidate_utility(candidate: Candidate) -> tuple[Candidate, float]:
    """
    Calculates the utility of the candidate given in parameters.
    Utility formula is :
        U = sum_forall_v_in_V(distance(c, v)^2) ÷ len(V)^2
    with : c - position of candidate
           v - position of voter
           V - list of voters

    :param candidate: Candidate whose utility is to be determined
    :return: candidate's utility or "MAX" if utility value is infinite
    """
    voters = data_manager.get_voters()
    utility = sum(math.dist(candidate.coordinates(), voter.coordinates())**2 for voter in voters) / (len(voters) ** 2)
    return candidate, utility


def percentage_utility(candidate: Candidate) -> str:
    """
    Converts the utility of a candidate to a percentage for display.

    :param candidate: Candidate whose utility percentage is to be determined
    :return: the percentage in string format
    """
    utilities = [utility for _, utility in map(candidate_utility, data_manager.get_candidates())]
    min_utility, max_utility = min(utilities), max(utilities)
    range_utility = max_utility - min_utility
    if range_utility == 0:
        percentage = 100
    else:
        percentage = 100 - round(((candidate_utility(candidate)[1] - min_utility) / range_utility) * 100)
    return str(percentage) + "%"


top_utility = None


def show_candidates_utility():
    """
    Display popup with the utilities of all the candidates.
    The maximum utility is displayed in bold.
    """
    global top_utility
    if top_utility:
        top_utility.destroy()

    if data_manager.is_voters_empty() or data_manager.is_candidates_empty():
        tk.messagebox.showwarning(
            title="Données insuffisantes",
            message="Données insuffisantes. Veuillez ajouter des votants et/ou des candidats."
        )
    else:
        top_utility = tk.Toplevel()
        top_utility.title("Utilité des candidats")

        list_utilities = sorted([candidate_utility(c) for c in data_manager.get_candidates()], key=lambda x: x[1])
        tk.Label(top_utility, text="Rang", font=("Mistral", "15", "bold")).grid(row=0, column=0)
        tk.Label(top_utility, text="Candidat", font=("Mistral", "15", "bold")).grid(row=0, column=1)
        tk.Label(top_utility, text="Pourcentage", font=("Mistral", "15", "bold")).grid(row=0, column=2)
        tk.Label(top_utility, text="Utilité", font=("Mistral", "15", "bold")).grid(row=0, column=3)

        for candidate_number, (candidate, c_utility) in enumerate(list_utilities, start=1):
            font_style = "normal"
            if percentage_utility(candidate) == "100%":
                font_style = "bold"
            tk.Label(top_utility, text=str(candidate_number), font=("Mistral", "15", font_style)).grid(row=candidate_number, column=0)
            tk.Label(top_utility, text=candidate.get_label(), font=("Mistral", "15", font_style)).grid(row=candidate_number, column=1)
            tk.Label(top_utility, text=str(percentage_utility(candidate)), font=("Mistral", "15", font_style)).grid(row=candidate_number, column=2)
            if c_utility == 0:
                tk.Label(top_utility, text="MAX", font=("Mistral", "15", font_style)).grid(row=candidate_number, column=3)
            else:
                tk.Label(top_utility, text=str(round(1/c_utility, 2)), font=("Mistral", "15", font_style)).grid(row=candidate_number, column=3)

    keyboard_manager.esc_bind(top_utility)


# Add the canvas to the tkinter window
graph_manager.get_tk_widget().grid(row=0, column=0, padx=20, pady=20)
graph_manager.get_tk_widget().pack()

# Import file on button click
import_file = tk.Button(main_panel, text="Lire des données", takefocus=0, highlightbackground="white", borderwidth=1,
                        command=lambda: show_import_file_popup())
import_file.place(relx=0, rely=0, relwidth=button_width, relheight=button_height)

# Export file on button click
export_file = tk.Button(main_panel, text="Sauvegarder les données", takefocus=0, highlightbackground="white", borderwidth=1,
                        command=lambda: call_export_file())
export_file.place(relx=0.25, rely=0, relwidth=button_width, relheight=button_height)

# Reset the voters on button click
reset_voters = tk.Button(main_panel, text="Réinitialiser les votants", takefocus=0, highlightbackground="white", borderwidth=1,
                         command=lambda: reset(voters=True))
reset_voters.place(relx=0.5, rely=0, relwidth=button_width, relheight=button_height)
reset_voters.configure(cursor="exchange")

# Reset the candidates on button click
reset_candidates = tk.Button(main_panel, text="Réinitialiser les candidats", takefocus=0, highlightbackground="white", borderwidth=1,
                             command=lambda: reset(candidates=True))
reset_candidates.place(relx=0.75, rely=0, relwidth=button_width, relheight=button_height)
reset_candidates.configure(cursor="exchange")

# Generate the utilities on button click
generate_utility = tk.Button(main_panel, text="Générer les utilités", takefocus=0, highlightbackground="white", borderwidth=1,
                             command=show_candidates_utility)
generate_utility.place(relx=0, rely=1 - button_height, relwidth=button_width, relheight=button_height)

# Generate the profiles on button click
btn_show_voting_systems = tk.Button(main_panel, text="Systèmes de vote", takefocus=0, highlightbackground="white", borderwidth=1,
                                    command=show_voting_systems_popup)
btn_show_voting_systems.place(relx=0.25, rely=1 - button_height, relwidth=button_width, relheight=button_height)

# Distribute the voters on button click
distribute_voters = tk.Button(main_panel, text="Distribuer les votants", takefocus=0, highlightbackground="white", borderwidth=1,
                              command=lambda: show_distribute_popup(is_voter=True)
)
distribute_voters.place(relx=0.5, rely=1 - button_height, relwidth=button_width, relheight=button_height)

# Distribute the candidates on button click
distribute_candidates = tk.Button(main_panel, text="Distribuer les candidats", takefocus=0, highlightbackground="white", borderwidth=1,
                                  command=lambda: show_distribute_popup(is_voter=False)
)
distribute_candidates.place(relx=0.75, rely=1 - button_height, relwidth=button_width, relheight=button_height)

# Toggle annotations of voters on button click
toggle_annotations = tk.Label(main_panel, image=on, borderwidth=0, background="white", height=50, width=55, cursor="target")
toggle_annotations.bind('<Button>', toggle)
bind_tooltip(toggle_annotations, text="Afficher/Masquer les annotations des votants")
toggle_annotations.place(relx=0.91, rely=0.06)

list_buttons = [import_file, export_file, reset_voters, reset_candidates, generate_utility,
                btn_show_voting_systems, distribute_voters, distribute_candidates, -1]
keyboard_manager.tab_bind(root, list_buttons)
keyboard_manager.shift_tab_bind(root, list_buttons)

# Start the tkinter event loop
root.mainloop()
