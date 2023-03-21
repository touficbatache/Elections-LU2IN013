from dataclasses import dataclass


@dataclass
class Voter:
    """Data class for keeping track of a voter."""

    __label: str
    __coordinates: tuple

    def __init__(self, label: str, coordinates: tuple):
        self.__label = label
        self.__coordinates = coordinates

    def get_label(self) -> str:
        """
        :return: the voter's label
        """
        return self.__label

    def set_label(self, label: str):
        """
        :param label: the voter's new label
        """
        self.__label = label

    def coordinates(self) -> tuple[float, float]:
        """
        :return: the voter's coordinates
        """
        return self.__coordinates
