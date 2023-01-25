import math
import random
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Create the main tkinter window
root = tk.Tk()
root.title("Simulation Elections")
root.geometry("750x750")

# Create a figure and axis for the graph
fig = plt.figure()
ax = fig.add_subplot()
ax.set(xlim=(-1.1, 1.1), ylim=(-1.1, 1.1))

# Add text on top side of graph
ax.text(0.5, 1.05, "Libéralisme culturel", transform=ax.transAxes, ha="center", va="center", fontsize=12)
# Add text on right side of graph
ax.text(1.05, 0.5, "Libéralisme économique", transform=ax.transAxes, ha="center", va="center", rotation=270,
        fontsize=12)
# Add text on bottom side of graph
ax.text(0.5, -0.05, "Conservatisme culturel", transform=ax.transAxes, ha="center", va="center", fontsize=12)
# Add text on left side of graph
ax.text(-0.05, 0.5, "Interventionnisme étatique", transform=ax.transAxes, ha="center", va="center", rotation=90,
        fontsize=12)

# Remove value ticks from the x-axis and the y-axis
ax.set_xticks([])
ax.set_yticks([])

# Changing the position of the axes to the middle
ax.spines['left'].set_position('center')
ax.spines['bottom'].set_position('center')
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')

# Create a tkinter canvas to display the graph
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().grid(row=0, column=0, padx=20, pady=20)

nbCandidats = 7
candidats = []

for i in range(nbCandidats):
    x = random.uniform(-1, 1)
    y = random.uniform(-1, 1)
    candidats.append((x, y))
    ax.scatter(x, y, marker="s")
    ax.text(x - 0.02, y + 0.05, chr(64 + i + 1), fontsize=12)

canvas.draw()

# Add functionality to add points by clicking on the graph
votants = []


def on_click(event):
    # Get the x and y coordinates of the click event
    x = event.xdata
    y = event.ydata

    # Add the point to the list of points, only if clicked inside the graph
    if x is not None and -1 <= x <= 1 and y is not None and -1 <= y <= 1:
        votants.append((x, y))

        # Plot the new point on the graph
        ax.scatter(x, y, color="black")

        ax.text(x - 0.02, y + 0.05, len(votants), fontsize=12)

        # Redraw the canvas
        canvas.draw()


canvas.mpl_connect("button_press_event", on_click)
# add the canvas to the tkinter window
canvas.get_tk_widget().pack()


def genererProfils():
    dico = dict()
    for j in range(len(votants)):
        scores = []
        for i in range(len(candidats)):
            scores.append(("candidat " + chr(64 + i + 1), math.dist(votants[j], candidats[i])))
        scores.sort(key=lambda x: x[1])
        dico[j] = scores

    top = tk.Toplevel(root)
    if not dico:
        top.title("Pas de résultats")
    else:
        top.title("Les résultats")
        for a in range(len(votants)):
            tk.Grid.columnconfigure(top, a, weight=1)
        for b in range(len(candidats) + 1):
            tk.Grid.rowconfigure(top, b, weight=1)
        for c, d in dico.items():
            lab = tk.Label(top, text="Votant " + str(c + 1), font=('Mistral 12'))
            lab.grid(row=0, column=c, sticky="NSEW")
            for e in range(len(candidats)):
                res = ((math.sqrt(8) - round(d[e][1], 4)) * 100) / math.sqrt(8)
                lab = tk.Label(top, text=str(d[e][0]) + " • " + str(round(res, 2)) + "%", font=('Mistral 12'))
                lab.grid(row=e + 1, column=c, sticky="NSEW")


button = tk.Button(root, text="Generer les profils", command=genererProfils, bg="white").place(relx=root.winfo_width()/1000 - 0.2, rely=root.winfo_height()/1000 *4.5, relwidth=0.2, relheight=0.08)

# Start the tkinter event loop
root.mainloop()
