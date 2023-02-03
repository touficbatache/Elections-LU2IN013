import math
import random
import ToolTip
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Create the main tkinter window
root = tk.Tk()
root.title("Simulation Elections")
root.geometry("750x750")
root.option_add('*Font', 'Mistral 12')

# Create a figure and axes for the graph
fig = plt.figure()
axes = fig.add_subplot()
axes.set(xlim=(-1.1, 1.1), ylim=(-1.1, 1.1))

# Add text on top, right, bottom and left side of graph respectively
axes.text(0.5, 1.05, "Libéralisme culturel", transform=axes.transAxes, ha="center", va="center")
axes.text(1.05, 0.5, "Libéralisme économique", transform=axes.transAxes, ha="center", va="center", rotation=270)
axes.text(0.5, -0.05, "Conservatisme culturel", transform=axes.transAxes, ha="center", va="center")
axes.text(-0.05, 0.5, "Interventionnisme étatique", transform=axes.transAxes, ha="center", va="center", rotation=90)

# Remove value ticks from the x-axes and the y-axes
axes.set_xticks([])
axes.set_yticks([])

# Change the position of the axes to the middle
axes.spines['left'].set_position('center')
axes.spines['bottom'].set_position('center')
axes.spines['right'].set_color('none')
axes.spines['top'].set_color('none')
axes.xaxis.set_ticks_position('bottom')
axes.yaxis.set_ticks_position('left')

# Create a tkinter canvas to display the graph
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().grid(row=0, column=0, padx=20, pady=20)

# Number of candidates and empty lists to store the coordinates, the points and the annotations of the candidates on the graph
number_candidates = tk.StringVar()
candidates = []
points_candidates = []
annotations_candidates = []

# Number of voters and empty lists to store the coordinates, the points and the annotations of the voters on the graph
number_voters = tk.StringVar()
voters = []
points_voters = []
annotations_voters = []

# Default value for insert
default = 7


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


# Function to reinitialize the values of the 3 lists related to the candidates or voters
def reinitialiser(list_assets, pt_list, ann_list, a):
    if not list_assets and a == 0:
        tk.messagebox.showerror(title="Votants déjà réinitialisés", message="Votants déjà réinitialisés")
    elif not list_assets and a == 1:
        tk.messagebox.showerror(title="Candidats déjà réinitialisés", message="Candidats déjà réinitialisés")
    else:
        while pt_list:
            pt_list[-1].remove()
            pt_list.remove(pt_list[-1])
        while list_assets:
            list_assets.remove(list_assets[-1])
        while ann_list:
            ann_list[-1].remove()
            ann_list.remove(ann_list[-1])
        canvas.draw()


# Function to handle input and call random() for candidates or voters
def distribuer(number, list_assets, pt_list, ann_list, a):
    if a == 0:
        s = "votants"
    else:
        s = "candidats"

    top_main = tk.Toplevel(root)
    top_main.title("Choisir nombre " + s)
    top_main.geometry("250x150")
    label_top = tk.Label(top_main, text="Donner le nombre de " + s + " :")
    label_top.pack()
    global log
    log = tk.StringVar()
    number.trace_variable("w", valider)
    entry = tk.Entry(top_main, width=20, textvariable=number)
    entry.pack()
    label_top2 = tk.Label(top_main, text="Laisser vide pour valeur de défaut (" + str(default) + ")")
    label_top2.pack()
    button_dist = tk.Button(top_main, text="Distribuer les " + s,
                            command=lambda: [randomiser(number, list_assets, pt_list, ann_list, a), top_main.destroy()])
    button_dist.pack()


# Function to distribute the candidates or voters randomly on the graph
def randomiser(number, list_assets, pt_list, ann_list, n):
    if number.get() != "":
        nb = int(number.get())
    else:
        nb = default

    for i in range(nb):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        list_assets.append((x, y))
        # plot the assets on the graph
        if n == 0:
            p, = axes.plot(x, y, 'o', color="black", zorder=10)
        else:
            p, = axes.plot(x, y, 's', zorder=10)
        pt_list.append(p)
        # label the assets on the graph
        if n == 0:
            a = axes.annotate(str(len(voters)), (x, y), (x - 0.02, y + 0.05), zorder=11)
        else:
            a = axes.annotate(chr(ord('A') + len(candidates) - 1), (x, y), (x - 0.02, y + 0.05), zorder=11)
        ann_list.append(a)
        # draw the canvas
        canvas.draw()


# Variable to keep track of the "shift" key press
shift_is_held = False


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
canvas.mpl_connect('key_press_event', on_key_press)
canvas.mpl_connect('key_release_event', on_key_release)


# Function to handle click events on the graph
def on_click(event):
    # Get the x and y coordinates of the click event
    x = event.xdata
    y = event.ydata

    # Add the point to the list of points, only if clicked inside the graph
    if x is not None and -1 <= x <= 1 and y is not None and -1 <= y <= 1:
        # If the shift key is pressed, add candidates instead of voters
        if shift_is_held:
            # Add candidates to the list
            candidates.append((x, y))

            # Plot the new point on the graph
            p, = axes.plot(x, y, 's', zorder=10)
            points_candidates.append(p)

            # Label the point on the graph
            ann = axes.annotate(chr(ord('A') + len(candidates) - 1), (x, y), (x - 0.02, y + 0.05), zorder=11)
            annotations_candidates.append(ann)
        else:
            # Add voters to the list
            voters.append((x, y))

            # Plot the new point on the graph
            p, = axes.plot(x, y, 'o', color="black", zorder=10)
            points_voters.append(p)

            # Label the point on the graph
            ann = axes.annotate(str(len(voters)), (x, y), (x - 0.02, y + 0.05), zorder=11)
            annotations_voters.append(ann)

        # Redraw the canvas
        canvas.draw()


# Connect the click event to the on_click function
canvas.mpl_connect("button_press_event", on_click)

# Add the canvas to the tkinter window
canvas.get_tk_widget().pack()

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
            scores.append((chr(ord('A') + j), math.dist(voters[i], candidates[j])))
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
                maximum = math.sqrt((int(axes.get_xlim()[1]) - int(axes.get_xlim()[0]))**2 + (int(axes.get_ylim()[1]) - int(axes.get_ylim()[0]))**2)
                # Calculates the percentage based on max distance
                res = ((maximum - d[e][1]) * 100) / maximum
                lab = tk.Label(top, text=str(d[e][0]))
                lab.grid(row=e + 1, column=c, sticky="NSEW")
                ToolTip.create_tool_tip(lab, text=str(round(res, 2)) + "%")


# Generate the profiles on button click
generate_profiles = tk.Button(root, text="Generer les profils", command=generer_profils)
generate_profiles.place(relx=0, rely=1 - 0.05, relwidth=0.25, relheight=0.05)

distribute_voters = tk.Button(root, text="Distribuer les votants",
                              command=lambda: distribuer(number_voters, voters, points_voters, annotations_voters, 0))
distribute_voters.place(relx=0.25, rely=1 - 0.05, relwidth=0.25, relheight=0.05)

reinitialize_voters = tk.Button(root, text="Réinitialiser les votants",
                                command=lambda: reinitialiser(voters, points_voters, annotations_voters, 0))
reinitialize_voters.place(relx=0.58, rely=0, relwidth=0.2, relheight=0.05)
reinitialize_voters.configure(cursor="exchange")

distribute_candidates = tk.Button(root, text="Distribuer les candidats",
                                  command=lambda: distribuer(number_candidates, candidates, points_candidates,
                                                             annotations_candidates, 1))
distribute_candidates.place(relx=0.5, rely=1 - 0.05, relwidth=0.25, relheight=0.05)

reinitialize_candidates = tk.Button(root, text="Réinitialiser les candidats",
                                    command=lambda: reinitialiser(candidates, points_candidates, annotations_candidates,
                                                                  1))
reinitialize_candidates.place(relx=0.78, rely=0, relwidth=0.22, relheight=0.05)
reinitialize_candidates.configure(cursor="exchange")

# Start the tkinter event loop
root.mainloop()
