from dataclasses import dataclass


@dataclass
class Candidate:
    """Data class for keeping track of a candidate."""

    __label: str
    __coordinates: tuple

    def __init__(self, label: str, coordinates: tuple):
        self.__label = label
        self.__coordinates = coordinates

    def label(self) -> str:
        """
        :return: the candidate's label
        """
        return self.__label

    def coordinates(self) -> tuple:
        """
        :return: the candidate's coordinates
        """
        return self.__coordinates
