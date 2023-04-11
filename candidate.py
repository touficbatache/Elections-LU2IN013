import random
from dataclasses import dataclass

import matplotlib.colors as mcolors


@dataclass
class Candidate:
    """Data class for keeping track of a candidate."""

    __label: str
    __coordinates: tuple
    __color: str

    def __init__(self, label: str, coordinates: tuple, color: str):
        self.__label = label
        self.__coordinates = coordinates
        self.__color = color

    @classmethod
    def random_color(cls, label: str, coordinates: tuple):
        """
        Generates random color for candidate.
        :param label: the label of the candidate
        :param coordinates: the coordinates of the candidate
        :return: the new candidate
        """
        colors = mcolors.XKCD_COLORS
        if "xkcd:black" in colors:
            colors.pop("xkcd:black")
        if "xkcd:white" in colors:
            colors.pop("xkcd:white")
        return cls(label, coordinates, random.choice(list(colors.values())))

    def get_label(self) -> str:
        """
        :return: the candidate's label
        """
        return self.__label

    def set_label(self, label: str):
        """
        :param label: the candidate's new label
        """
        self.__label = label

    def coordinates(self) -> tuple:
        """
        :return: the candidate's coordinates
        """
        return self.__coordinates

    def get_color(self) -> str:
        """
        :return: the candidate's color
        """
        return self.__color

    def set_color(self, color: str):
        """
        :param color: the candidate's new color
        """
        self.__color = color
