import random
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Create the main tkinter window
root = tk.Tk()
root.title("Interactive 2D Graph")

# Create a figure and axis for the graph
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set(xlim=(-1.1, 1.1), ylim=(-1.1, 1.1))

# Add text on top side of graph
ax.text(0.5, 1.05, "Libéralisme culturel", transform=ax.transAxes, ha="center", va="center", fontsize=12)

# Add text on right side of graph
ax.text(1.05, 0.5, "Libéralisme économique", transform=ax.transAxes, ha="center", va="center", rotation=270, fontsize=12)

# Add text on bottom side of graph
ax.text(0.5, -0.05, "Conservatisme culturel", transform=ax.transAxes, ha="center", va="center", fontsize=12)

# Add text on left side of graph
ax.text(-0.05, 0.5, "Interventionnisme étatique", transform=ax.transAxes, ha="center", va="center", rotation=90, fontsize=12)

# Add a title and labels to the graph
# ax.set_title("Sample 2D Graph")
# ax.set_xlabel("X-axis", loc="left")
# ax.set_ylabel("Y-axis", loc="top")

ax.set_xticks([])
ax.set_yticks([])

# Changing the position of the spines
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

        # Redraw the canvas
        canvas.draw()


canvas.mpl_connect("button_press_event", on_click)

# Start the tkinter event loop
root.mainloop()
