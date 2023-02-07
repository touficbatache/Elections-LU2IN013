from tkinter import Tk, Canvas
from typing import Callable

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from candidate import Candidate
from voter import Voter


class GraphManager:
    """
    Class to manage the graph.

    ! This class should not expose private variables such as
    fig, axes or canvas with getters. It should create an
    abstraction layer over them to limit and control the usage
    of internal and private features. Ex: we abstract canvas
    re-drawing with build() and click-handling with bind(). !
    """

    # Store the voters' data (points and annotations) in the form of:
    # dict ({ str("voter_label") : tuple(point, annotation) })
    __voters = dict()

    # Store the candidates' data (points and annotations) in the form of:
    # dict ({ str("candidate_label") : tuple(point, annotation) })
    __candidates = dict()

    def __init__(self, tk_root: Tk):
        # Create a figure
        self.__fig = plt.figure()

        # Create and configure axes for the graph
        self.__axes = self.__fig.add_subplot()
        self.__axes.set(xlim=(-1.1, 1.1), ylim=(-1.1, 1.1))
        # Add text on top, right, bottom and left side of graph respectively
        self.__axes.text(0.5, 1.05, "Libéralisme culturel", transform=self.__axes.transAxes, ha="center", va="center")
        self.__axes.text(1.05, 0.5, "Libéralisme économique", transform=self.__axes.transAxes, ha="center", va="center",
                         rotation=270)
        self.__axes.text(0.5, -0.05, "Conservatisme culturel", transform=self.__axes.transAxes, ha="center",
                         va="center")
        self.__axes.text(-0.05, 0.5, "Interventionnisme étatique", transform=self.__axes.transAxes, ha="center",
                         va="center", rotation=90)
        # Remove value ticks from the x-axes and the y-axes
        self.__axes.set_xticks([])
        self.__axes.set_yticks([])
        # Change the position of the axes to the middle
        self.__axes.spines['left'].set_position('center')
        self.__axes.spines['bottom'].set_position('center')
        self.__axes.spines['right'].set_color('none')
        self.__axes.spines['top'].set_color('none')
        self.__axes.xaxis.set_ticks_position('bottom')
        self.__axes.yaxis.set_ticks_position('left')

        # Create a tkinter canvas to display the graph
        self.__canvas = FigureCanvasTkAgg(self.__fig, master=tk_root)

    def add_voter(self, voter: Voter) -> bool:
        """
        Adds the voter to the graph (point and annotation), without building it.
        Calling build() is necessary to see the updated changes.
        """
        if voter.label() in self.__voters:
            return False

        # Plot the voter on the graph
        point, = self.__axes.plot(voter.coordinates()[0], voter.coordinates()[1], 'o', color="black")
        # Label the point on the graph
        annotation = self.__axes.annotate(
            text=voter.label(),
            xy=voter.coordinates(),
            xytext=(voter.coordinates()[0] - 0.02, voter.coordinates()[1] + 0.05),
            zorder=11
        )
        # Add voter to the dict
        self.__voters[voter.label()] = (point, annotation)

        return True

    def clear_voters(self):
        """
        Clears all the voters from the graph, without building it.
        Calling build() is necessary to see the updated changes.
        """
        for (point, annotation) in self.__voters.values():
            point.remove()
            annotation.remove()

        self.__voters.clear()

    def add_candidate(self, candidate: Candidate) -> bool:
        """
        Adds the candidate to the graph (point and annotation), without building it.
        Calling build() is necessary to see the updated changes.
        """

        if candidate.label() in self.__candidates:
            return False

        # Plot the candidate on the graph
        point, = self.__axes.plot(candidate.coordinates()[0], candidate.coordinates()[1], 's')
        # Label the point on the graph
        annotation = self.__axes.annotate(
            text=candidate.label(),
            xy=candidate.coordinates(),
            xytext=(candidate.coordinates()[0] - 0.02, candidate.coordinates()[1] + 0.05),
            zorder=11
        )
        # Add candidate to the dict
        self.__candidates[candidate.label()] = (point, annotation)

        return True

    def clear_candidates(self):
        """
        Clears all the candidates from the graph, without building it.
        Calling build() is necessary to see the updated changes.
        """
        for (point, annotation) in self.__candidates.values():
            point.remove()
            annotation.remove()

        self.__candidates.clear()

    def build(self):
        """
        Builds the updated graph by calling canvas.draw().
        """
        self.__canvas.draw()

    def get_tk_widget(self) -> Canvas:
        """
        Return the Tk widget used to implement FigureCanvasTkAgg.

        ! This method exposes the Tk widget, but I believe this
        is the only instance where it's fine because it's necessary !
        """
        return self.__canvas.get_tk_widget()

    def bind(self, event: str, callable: Callable):
        """
        Bind an event to a callable.
        """
        self.__canvas.mpl_connect(event, callable)

    def get_xlim(self):
        """
        Return the x-axis view limits.
        """
        return self.__axes.get_xlim()

    def get_ylim(self):
        """
        Return the x-axis view limits.
        """
        return self.__axes.get_ylim()
