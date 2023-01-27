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
numberCandidats = tk.StringVar()
# empty list to store the candidates' coordinates
candidats = []
# empty list to store the points of the candidates plotted on the graph
pt_candidats = []
# empty list to store the annotations of the points of the candidates plotted on the graph
ann_candidats = []

# number of voters
numberVoters = tk.StringVar()
# empty list to store the coordinates of the voters' coordinates
votants = []
# empty list to store the points of the voters plotted on the graph
pt_votants = []
# empty list to store the annotations of the points of the voters plotted on the graph
ann_votants = []


# function to validate the input given (the number of candidates or voters)
def validate(*args):
    if args[0] == 'PY_VAR1':
        value = numberVoters
    else:
        value = numberCandidats

    if not (value.get()).isdigit():
        tk.messagebox.showwarning(title='ERREUR DE SAISIE', message="Valeur entière uniquement")


# function to reinitialize the values of the 3 lists related to the candidats or voters
def reinitialiser(liste, pt_liste, ann_liste, a):
    if not liste and a == 0:
        tk.messagebox.showerror(title="Votants déja initialisé", message="Votants déja initialisé")
    elif not liste and a == 1:
        tk.messagebox.showerror(title="Candidats déja initialisé", message="Candidats déja initialisé")
    else:
        while pt_liste:
            pt_liste[-1].remove()
            pt_liste.remove(pt_liste[-1])
        while liste:
            liste.remove(liste[-1])
        while ann_liste:
            ann_liste[-1].remove()
            ann_liste.remove(ann_liste[-1])
        canvas.draw()


# function to handle input and call random() for candidates or voters
def distribuer(number, liste, pt_list, ann_list, a):
    if a == 0:
        s = "votants"
    else:
        s = "candidats"

    top_main = tk.Toplevel(root)
    top_main.title("Choisir nombre " + s)
    top_main.geometry("300x300")
    label_top = tk.Label(top_main, text="Donner le nombre de " + s + " :")
    label_top.place(x=0, y=0)
    label_top = tk.Label(top_main, text="Laisser vide pour valeur de défaut : 7")
    label_top.place(x=0, y=40)
    number.trace_variable("w", validate)
    entry = tk.Entry(top_main, width=20, textvariable=number)
    entry.place(x=0, y=80)
    button_dist = tk.Button(top_main, text="Distribuer les " + s,
                            command=lambda: [randomiser(number, liste, pt_list, ann_list, a), top_main.destroy()])
    button_dist.place(x=0, y=120)


# function to distribute the candidates or voters randomly on the graph
def randomiser(number, liste, pt_list, ann_list, n):
    if number.get() != "":
        nb = int(number.get())
    else:
        nb = 7

    for i in range(nb):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        liste.append((x, y))
        # plot the assets on the graph
        if n == 0:
            p, = ax.plot(x, y, 'o', color="black", zorder=10)
        else:
            p, = ax.plot(x, y, 's', zorder=10)
        pt_list.append(p)
        # label the assets on the graph
        if n == 0:
            a = ax.annotate(str(len(votants)), (x, y), (x - 0.02, y + 0.05), zorder=11)
        else:
            a = ax.annotate(chr(ord('A') + len(candidats) - 1), (x, y), (x - 0.02, y + 0.05), zorder=11)
        ann_list.append(a)
        # draw the canvas
        canvas.draw()


# function to handle click events on the graph
def on_click(event):
    # get the x and y coordinates of the click event
    x = event.xdata
    y = event.ydata

    # add the point to the list of points, only if clicked inside the graph
    if x is not None and -1 <= x <= 1 and y is not None and -1 <= y <= 1:
        votants.append((x, y))

        # plot the new point on the graph
        p, = ax.plot(x, y, 'o', color="black", zorder=10)
        pt_votants.append(p)

        # label the point on the graph
        ann = ax.annotate(str(len(votants)), (x, y), (x - 0.02, y + 0.05), zorder=11)
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

    if not dico or votants == [] or candidats == []:
        # if there are no results in the dictionary, show it in window title
        tk.messagebox.showwarning(title='Pas de résultats', message="Pas de résultats")
    else:
        # create a new top level window to display the results
        top = tk.Toplevel(root)
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


# generate the profiles on button click
GenererProfils = tk.Button(root, text="Generer les profils", command=generer_profils)
GenererProfils.place(relx=0, rely=1 - 0.05, relwidth=0.2, relheight=0.05)

DistribuerVotants = tk.Button(root, text="Distribuer les votants",
                              command=lambda: distribuer(numberVoters, votants, pt_votants, ann_votants, 0))
DistribuerVotants.place(relx=0.2, rely=1 - 0.05, relwidth=0.2, relheight=0.05)

ReinitialiserVotants = tk.Button(root, text="Réinitialiser les votants",
                                 command=lambda: reinitialiser(votants, pt_votants, ann_votants, 0))
ReinitialiserVotants.place(relx=0.8, rely=0, relwidth=0.2, relheight=0.05)

DistribuerCandidats = tk.Button(root, text="Distribuer les candidats",
                                command=lambda: distribuer(numberCandidats, candidats, pt_candidats, ann_candidats, 1))
DistribuerCandidats.place(relx=0.4, rely=1 - 0.05, relwidth=0.2, relheight=0.05)

ReinitialiserCandidats = tk.Button(root, text="Réinitialiser les candidats",
                                   command=lambda: reinitialiser(candidats, pt_candidats, ann_candidats, 1))
ReinitialiserCandidats.place(relx=0.58, rely=0, relwidth=0.22, relheight=0.05)

# start the tkinter event loop
root.mainloop()
