from dataclasses import dataclass


@dataclass
class Voter:
    """Data class for keeping track of a voter."""

    __label: str
    __coordinates: tuple
    __has_delegated_vote: bool
    __weight: int

    def __init__(self, label: str, coordinates: tuple):
        self.__label = label
        self.__coordinates = coordinates
        self.__has_delegated_vote = False
        self.__weight = 1

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

    def has_delegated_vote(self) -> bool:
        """
        :return: whether the voter has delegated their vote or not
        """
        return self.__has_delegated_vote

    def set_delegated_vote(self, has_delegated_vote: bool):
        """
        :param has_delegated_vote: whether the voter has delegated their vote or not
        """
        self.__has_delegated_vote = has_delegated_vote

    def get_weight(self) -> int:
        """
        :return: the voter's vote weight
        """
        return self.__weight

    def set_weight(self, weight: int):
        """
        :param weight: the voter's vote weight
        """
        self.__weight = weight
