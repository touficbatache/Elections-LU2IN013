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
nbCandidats = 7

# empty list to store the candidates' coordinates
candidats = []

# loop to generate random coordinates for the candidates
for i in range(nbCandidats):
    x = random.uniform(-1, 1)
    y = random.uniform(-1, 1)
    candidats.append((x, y))
    # plot the candidates on the graph
    ax.scatter(x, y, marker="s")
    # label the candidates on the graph
    ax.text(x - 0.02, y + 0.05, chr(ord('A') + i))

# draw the canvas
canvas.draw()

# let user add points by clicking on the graph:

# list to store the coordinates of the voters' clicks
votants = []


# function to handle click events on the graph
def on_click(event):
    # get the x and y coordinates of the click event
    x = event.xdata
    y = event.ydata

    # add the point to the list of points, only if clicked inside the graph
    if x is not None and -1 <= x <= 1 and y is not None and -1 <= y <= 1:
        votants.append((x, y))

        # plot the new point on the graph
        ax.scatter(x, y, color="black")

        # label the point on the graph
        ax.text(x - 0.02, y + 0.05, len(votants))

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


# generate the profiles on button click
button = tk.Button(root, text="Generer les profils", command=generer_profils)
button.place(relx=root.winfo_width() / 1000 - 0.2, rely=root.winfo_height() / 1000 * 4.5, relwidth=0.2, relheight=0.08)

# start the tkinter event loop
root.mainloop()
