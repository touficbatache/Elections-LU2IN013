import math
from tkinter import Widget, Canvas
from typing import Callable

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patheffects import withStroke

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
    # list (tuple(str("voter_label"), tuple(point, annotation)))
    __voters = list()

    # Store the candidates' data (points and annotations) in the form of:
    # list (tuple(str("candidate_label"), tuple(point, annotation)))
    __candidates = list()

    # Store the plotted approbation approval circles
    __approbation_circles = list()

    # Font and marker size for annotations
    __font_size = 8
    __marker_size = 4

    # Variable to keep track of the toggle button state
    __toggle_state = False

    def __init__(self, tk_root: Widget):
        # Create a figure
        self.__fig = plt.figure()

        # Create and configure axes for the graph
        self.__axes = self.__fig.add_subplot()
        self.__axes.set(xlim=(-1.1, 1.1), ylim=(-1.1, 1.1))
        # Add text on top, right, bottom and left side of graph respectively
        self.__axes.text(
            0.5,
            1.05,
            "Libéralisme culturel",
            transform=self.__axes.transAxes,
            ha="center",
            va="center",
            fontsize=self.__font_size,
        )
        self.__axes.text(
            1.05,
            0.5,
            "Libéralisme économique",
            transform=self.__axes.transAxes,
            ha="center",
            va="center",
            fontsize=self.__font_size,
            rotation=270,
        )
        self.__axes.text(
            0.5,
            -0.05,
            "Conservatisme culturel",
            transform=self.__axes.transAxes,
            ha="center",
            va="center",
            fontsize=self.__font_size,
        )
        self.__axes.text(
            -0.05,
            0.5,
            "Interventionnisme étatique",
            transform=self.__axes.transAxes,
            ha="center",
            va="center",
            fontsize=self.__font_size,
            rotation=90,
        )
        # Remove value ticks from the x-axes and the y-axes
        self.__axes.set_xticks([])
        self.__axes.set_yticks([])
        # Change the position of the axes to the middle
        self.__axes.spines["left"].set_position("center")
        self.__axes.spines["bottom"].set_position("center")
        self.__axes.spines["right"].set_color("none")
        self.__axes.spines["top"].set_color("none")
        self.__axes.xaxis.set_ticks_position("bottom")
        self.__axes.yaxis.set_ticks_position("left")

        # Create a tkinter canvas to display the graph
        self.__canvas = FigureCanvasTkAgg(self.__fig, master=tk_root)

    def add_voter(self, voter: Voter) -> bool:
        """
        Adds the voter to the graph (point and annotation), without building it.
        Calling build() is necessary to see the updated changes.

        :param voter: the voter to add
        :return: whether the voter was successfully added or not
        """
        if voter.get_label() in self.__voters:
            return False

        # Plot the voter on the graph
        point, = self.__axes.plot(
            voter.coordinates()[0],
            voter.coordinates()[1],
            "o",
            markersize=self.__marker_size,
            color="black",
            zorder=10,
            alpha=0.5 if voter.has_delegated_vote() else 1
        )
        # Label the point on the graph
        annotation = self.__axes.annotate(
            text=voter.get_label(),
            xy=voter.coordinates(),
            xytext=(voter.coordinates()[0] - 0.02, voter.coordinates()[1] + 0.05),
            fontsize=self.__font_size,
            zorder=11,
            alpha=0.5 if voter.has_delegated_vote() else 1
        )
        # Add voter to the dict
        self.__voters.append((voter.get_label(), (point, annotation)))

        return True

    def edit_voter_at(self, index: int, voter: Voter):
        """
        Edits the voter at a given index on the graph, without building it.
        Calling build() is necessary to see the updated changes.

        :param index: index of the desired voter
        :param voter: new voter data
        """
        label, (point, annotation) = self.__voters[index]
        point.remove()
        annotation.remove()

        # Plot the voter on the graph
        point, = self.__axes.plot(
            voter.coordinates()[0],
            voter.coordinates()[1],
            'o',
            markersize=self.__marker_size,
            color="black",
            zorder=10,
            alpha=0.5 if voter.has_delegated_vote() else 1
        )
        # Label the point on the graph
        annotation = self.__axes.annotate(
            text=voter.get_label(),
            xy=voter.coordinates(),
            xytext=(voter.coordinates()[0] - 0.02, voter.coordinates()[1] + 0.05),
            fontsize=self.__font_size,
            zorder=10,
            alpha=0.5 if voter.has_delegated_vote() else 1
        )
        # Replace voter in the dict
        self.__voters[index] = (voter.get_label(), (point, annotation))

    def clear_voters(self):
        """
        Clears all the voters from the graph, without building it.
        Calling build() is necessary to see the updated changes.
        """
        for (label, (point, annotation)) in self.__voters:
            point.remove()
            annotation.remove()

        self.__voters.clear()

    def add_candidate(self, candidate: Candidate) -> bool:
        """
        Adds the candidate to the graph (point and annotation), without building it.
        Calling build() is necessary to see the updated changes.

        :param candidate: the candidate to add
        :return: whether the candidate was successfully added or not
        """

        if candidate.get_label() in self.__candidates:
            return False

        # Plot the candidate on the graph
        point, = self.__axes.plot(
            candidate.coordinates()[0],
            candidate.coordinates()[1],
            's',
            markersize=self.__marker_size,
            color=candidate.get_color(),
            zorder=11
        )
        
        # Label the point on the graph
        annotation = self.__axes.annotate(
            text=candidate.get_label(),
            xy=candidate.coordinates(),
            xytext=(candidate.coordinates()[0] - 0.02, candidate.coordinates()[1] + 0.05),
            fontsize=self.__font_size,
            zorder=11,
            path_effects=[withStroke(linewidth=2, foreground="white")]
        )
        # Add candidate to the dict
        self.__candidates.append((candidate.get_label(), (point, annotation)))

        return True

    def edit_candidate_at(self, index: int, candidate: Candidate):
        """
        Edits the candidate at a given index on the graph, without building it.
        Calling build() is necessary to see the updated changes.

        :param index: index of the desired candidate
        :param candidate: new candidate data
        """
        label, (point, annotation) = self.__candidates[index]
        point.remove()
        annotation.remove()

        # Plot the candidate on the graph
        point, = self.__axes.plot(
            candidate.coordinates()[0],
            candidate.coordinates()[1],
            's',
            markersize=self.__marker_size,
            color=candidate.get_color(),
            zorder=11
        )

        # Label the point on the graph
        annotation = self.__axes.annotate(
            text=candidate.get_label(),
            xy=candidate.coordinates(),
            xytext=(candidate.coordinates()[0] - 0.02, candidate.coordinates()[1] + 0.05),
            fontsize=self.__font_size,
            zorder=11,
            path_effects=[withStroke(linewidth=2, foreground="white")]
        )
        # Replace candidate in the dict
        self.__candidates[index] = (candidate.get_label(), (point, annotation))

    def clear_candidates(self):
        """
        Clears all the candidates from the graph, without building it.
        Calling build() is necessary to see the updated changes.
        """
        for (label, (point, annotation)) in self.__candidates:
            point.remove()
            annotation.remove()

        self.__candidates.clear()
        self.clear_approbation_circles()

    def build(self):
        """
        Toggles the visibility of the annotations of all voters based on the value of __toggle_state.
        Builds the updated graph by calling canvas.draw().
        """
        if self.__toggle_state:
            # Shows annotations
            for (_, (_, annotation)) in self.__voters:
                annotation.set_visible(True)
        else:
            # Hides annotations
            for (_, (_, annotation)) in self.__voters:
                annotation.set_visible(False)
        self.__canvas.draw()

    def get_toggle_state(self) -> bool:
        """
        Return the boolean value of toggle_state
        :return: True if __toggle_state == True, False otherwise
        """
        return self.__toggle_state

    def set_toggle_state(self, value: bool):
        """
        Sets the boolean value of toggle_state to that of value
        :param value: the value to affect to toggle_state
        """
        self.__toggle_state = value

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
        :param event: the event to bind
        :param callable: the callable to which the event is binded
        """
        self.__canvas.mpl_connect(event, callable)

    def get_diagonal(self):
        """
        Return the diagonal size of the graph.

        :return: the diagonal size of the graph
        """
        return math.sqrt(
            (int(self.__axes.get_xlim()[1]) - int(self.__axes.get_xlim()[0])) ** 2
            + (int(self.__axes.get_ylim()[1]) - int(self.__axes.get_ylim()[0])) ** 2
        )

    def add_approbation_circles(self, approval_radius: int):
        """
        Adds the approval circles around candidates on the graph.
        Voters inside a candidate's circle are approving of them.

        :param approval_radius: Radius of the approval circle
        """
        # Remove the already plotted approval circles
        self.clear_approbation_circles()

        # Calculate the multiplier in order to fill the diagonal:
        #   - radius multiplier: diagonal size / x-axis size
        #   - diameter multiplier: 2 * radius multiplier
        multiplier = (
            2
            * self.get_diagonal()
            / (int(self.__axes.get_xlim()[1]) - int(self.__axes.get_xlim()[0]))
        )

        # For each candidate, plot the approval circles (color them accordingly)
        for (candidate_label, (coordinates, _)) in self.__candidates:
            xs, ys = coordinates.get_data()

            # Plot the approval circle
            circle = plt.Circle(
                (xs[0], ys[0]),
                multiplier * approval_radius / 100,
                color=coordinates.get_color(),
                fill=False,
                zorder=15,
            )
            self.__approbation_circles.append(circle)
            self.__axes.add_patch(circle)

    def clear_approbation_circles(self):
        """
        Clears the approval circles around candidates on the graph.
        """
        # Remove the already plotted approval circles
        for approbation_circle in self.__approbation_circles:
            approbation_circle.remove()
        self.__approbation_circles.clear()
