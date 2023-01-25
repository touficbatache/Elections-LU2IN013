import math
import random
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# create the main tkinter window
root = tk.Tk()
root.title("Simulation Elections")
root.geometry("750x750")
root.option_add('*Font', 'Mistral 12')

# create a figure and axis for the graph
fig = plt.figure()
ax = fig.add_subplot()
ax.set(xlim=(-1.1, 1.1), ylim=(-1.1, 1.1))

# add text on top side of graph
ax.text(0.5, 1.05, "Libéralisme culturel", transform=ax.transAxes, ha="center", va="center")
# add text on right side of graph
ax.text(1.05, 0.5, "Libéralisme économique", transform=ax.transAxes, ha="center", va="center", rotation=270)
# add text on bottom side of graph
ax.text(0.5, -0.05, "Conservatisme culturel", transform=ax.transAxes, ha="center", va="center")
# add text on left side of graph
ax.text(-0.05, 0.5, "Interventionnisme étatique", transform=ax.transAxes, ha="center", va="center", rotation=90)

# remove value ticks from the x-axis and the y-axis
ax.set_xticks([])
ax.set_yticks([])

# changing the position of the axes to the middle
ax.spines['left'].set_position('center')
ax.spines['bottom'].set_position('center')
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')

# create a tkinter canvas to display the graph
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().grid(row=0, column=0, padx=20, pady=20)

# number of candidates
nombreCandidats = tk.StringVar()

# empty list to store the candidates' coordinates
candidats = []
# empty list to store the points of the candidates plotted on the graph
pt_candidats = []
# empty list to store the annotations of the points of the candidates plotted on the graph
ann_candidats = []

t = None


# function to validate the input given (the number of candidates)
def validate_candidats(*args):
    global t
    if t:
        t.destroy()

    for c in nombreCandidats.get():
        if c.isdigit():
            continue
        else:
            t = tk.Toplevel(root)
            t.title("ERREUR DE SAISIE!")
            tk.Label(t, text="Uniquement des entiers!").pack(padx=5, pady=5)
            tk.Button(t, text="Ok", command=t.destroy).pack(padx=5, pady=5)
            break


# function to handle input and call random_candidats()
def distribuer_candidats():
    top_candidats = tk.Toplevel(root)
    top_candidats.title("Choisir nombre candidats")

    label_top = tk.Label(top_candidats, text="Donner le nombre de candidats:")
    label_top.place(x=0, y=0)

    nombreCandidats.trace_variable("w", validate_candidats)
    entry = tk.Entry(top_candidats, width=20, textvariable=nombreCandidats)
    entry.place(x=0, y=40)

    button_candidats = tk.Button(top_candidats, text="Distribuer les candidats", command=random_candidats)
    button_candidats.place(x=0, y=80)


letter = 'A'

# function to distribute the candidates randomly on the graph
def random_candidats():
    if nombreCandidats.get() != "":
        nbCandidats = int(nombreCandidats.get())
    else:
        nbCandidats = 7

    for i in range(nbCandidats):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        candidats.append((x, y))
        # plot the candidates on the graph

        c, = ax.plot(x, y, 's')
        pt_candidats.append(c)
        # label the candidates on the graph
        ann = ax.annotate(chr(ord(letter) + len(candidats) - 1), (x,y), (x - 0.02, y + 0.05))
        ann_candidats.append(ann)

        # draw the canvas
        canvas.draw()


# function to reinitialize the values of the 3 lists related to the candidats
def reinitialiser_candidats():
    while pt_candidats:
        pt_candidats[-1].remove()
        pt_candidats.remove(pt_candidats[-1])
    while candidats:
        candidats.remove(candidats[-1])
    while ann_candidats:
        ann_candidats[-1].remove()
        ann_candidats.remove(ann_candidats[-1])
    canvas.draw()

# list to store the coordinates of the voters' clicks
votants = []
pt_votants = []
ann_votants = []


# function to handle click events on the graph
def on_click(event):
    # get the x and y coordinates of the click event
    x = event.xdata
    y = event.ydata

    # add the point to the list of points, only if clicked inside the graph
    if x is not None and -1 <= x <= 1 and y is not None and -1 <= y <= 1:
        votants.append((x, y))

        # plot the new point on the graph
        p, = ax.plot(x, y, 'o', color="black")
        pt_votants.append(p)

        # label the point on the graph
        ann = ax.annotate(str(len(votants)), (x, y), (x - 0.02, y + 0.05))
        ann_votants.append(ann)

        # redraw the canvas
        canvas.draw()


# connect the click event to the on_click function
canvas.mpl_connect("button_press_event", on_click)

# add the canvas to the tkinter window
canvas.get_tk_widget().pack()

# variable to keep track of the top level window
top = None


# function to generate the profiles
def generer_profils():
    global top
    if top:
        top.destroy()

    # dictionary to store the scores for each voter
    dico = dict()

    # loop to calculate the scores for each voter
    for i in range(len(votants)):
        scores = []
        for j in range(len(candidats)):
            scores.append(("candidat " + chr(ord('A') + j), math.dist(votants[i], candidats[j])))
        scores.sort(key=lambda x: x[1])
        dico[i] = scores

    # create a new top level window to display the results
    top = tk.Toplevel(root)
    if not dico:
        # if there are no results in the dictionary, show it in window title
        top.title("Pas de résultats")
    else:
        top.title("Les résultats")
        # generate a table for each voter representing their profile
        for a in range(len(votants)):
            tk.Grid.columnconfigure(top, a, weight=1)
        for b in range(len(candidats) + 1):
            tk.Grid.rowconfigure(top, b, weight=1)
        for c, d in dico.items():
            lab = tk.Label(top, text="Votant " + str(c + 1))
            lab.grid(row=0, column=c, sticky="NSEW")
            for e in range(len(candidats)):
                res = ((math.sqrt(8) - d[e][1]) * 100) / math.sqrt(8)
                lab = tk.Label(top, text=str(d[e][0]) + " • " + str(round(res, 2)) + "%")
                lab.grid(row=e + 1, column=c, sticky="NSEW")


s = tk.StringVar()
t = None


def onvalidate(*args):
    global t
    if t:
        t.destroy()

    for c in s.get():
        if c.isdigit():
            continue
        t = tk.Toplevel(root)
        t.title("ERREUR de saisie")
        tk.Label(t, text="Uniquement des entiers!").pack(padx=5, pady=5)
        tk.Button(t, text="Ok", command=t.destroy).pack(padx=5, pady=5)
        break


def distribuer_votant():
    top2 = tk.Toplevel(root)
    top2.title("Choisir nombre votant")

    label_top2 = tk.Label(top2, text="Enter le nombre de votants:")
    label_top2.place(x=0, y=0)

    s.trace_variable("w", onvalidate)
    entry = tk.Entry(top2, width=20, textvariable=s)
    entry.place(x=0, y=40)

    button_top2 = tk.Button(top2, text="Distribuer les votants", command=random_votant)
    button_top2.place(x=0, y=80)


def random_votant():
    for i in range(int(s.get())):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        votants.append((x, y))
        # plot the candidates on the graph
        p, = ax.plot(x, y, 'o', color="black")
        pt_votants.append(p)
        # label the candidates on the graph
        ann = ax.annotate(str(len(votants)), (x, y), (x - 0.02, y + 0.05))
        ann_votants.append(ann)
        canvas.draw()


def reinitialiser_votant():
    while pt_votants:
        pt_votants[-1].remove()
        pt_votants.remove(pt_votants[-1])
    while votants:
        votants.remove(votants[-1])
    while ann_votants:
        ann_votants[-1].remove()
        ann_votants.remove(ann_votants[-1])
    canvas.draw()


# generate the profiles on button click
button = tk.Button(root, text="Generer les profils", command=generer_profils)
button.place(relx=root.winfo_width() / 1000 - 0.2, rely=root.winfo_height() / 1000 * 4.75, relwidth=0.2, relheight=0.05)
button2 = tk.Button(root, text="Distribuer les votants", command=distribuer_votant)
button2.place(relx=root.winfo_width() / 1000, rely=root.winfo_height() / 1000 * 4.75, relwidth=0.2, relheight=0.05)
button3 = tk.Button(root, text="Réinitialiser les votants", command=reinitialiser_votant)
button3.place(relx=0.8, rely=0, relwidth=0.2, relheight=0.05)
button4 = tk.Button(root, text="Distribuer les candidats", command=distribuer_candidats)
button4.place(relx=1-root.winfo_width() / 1000 - 0.2, rely=root.winfo_height() / 1000, relwidth=0.2, relheight=0.08)
button5 = tk.Button(root, text="Réinitialiser les candidats", command=reinitialiser_candidats)
button5.place(relx=1-root.winfo_width() / 1000 - 0.4, rely=root.winfo_height() / 1000, relwidth=0.2, relheight=0.08)


# start the tkinter event loop
root.mainloop()
