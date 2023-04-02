from typing import Callable

import matplotlib.colors as mcolors

from candidate import Candidate
from voter import Voter


class DataManager:
    """
   Class to manage the data.
   """

    # Store the voters
    __voters: list[Voter] = []

    # Voter added callback
    __on_voter_added: Callable[[Voter, int], None]

    # Voter edited callback
    __on_voter_edited: Callable[[Voter, int], None]

    # Voters cleared callback
    __on_voters_cleared: Callable[[], None]

    # Voter error callback
    __on_voter_error: Callable[[str], None]

    # Store the candidates
    __candidates: list[Candidate] = []

    # Candidate added callback
    __on_candidate_added: Callable[[Candidate, int], None]

    # Candidate edited callback
    __on_candidate_edited: Callable[[Candidate, int], None]

    # Candidates cleared callback
    __on_candidates_cleared: Callable[[], None]

    # Candidate error callback
    __on_candidate_error: Callable[[str], None]

    # Voter

    def add_voter(self, coordinates: tuple[float, float]) -> bool:
        """
        Adds a voter to the data.

        :param coordinates: voter's coordinates
        :return: whether the voter has been added or not
        """

        # Generate label
        label = str(len(self.__voters) + 1)

        # Avoid duplicates (unique labels!)
        added_labels = [added_voter.get_label() for added_voter in self.__voters]
        label_offset = 0
        while label in added_labels:
            label_offset += 1
            label = str(len(self.__voters) + 1 + label_offset)

        # Create a new voter
        voter = Voter(label=label, coordinates=coordinates)

        self.__voters.append(voter)
        if self.__on_voter_added is not None:
            self.__on_voter_added(voter, len(self.__voters) - 1)

        return True

    def get_voters(self) -> list[Voter]:
        """
        Returns the list of voters.

        :return: list of voters in data
        """
        return self.__voters

    def get_voter_at(self, index: int) -> Voter:
        """
        Returns the voter at the given index.

        :param index: index of the desired voter
        :return: voter at given index
        """

        return self.__voters[index]

    def edit_voter_at(self, index: int, label: str) -> bool:
        """
        Modifies the voter label at the given index.

        :param index: index of the desired voter
        :param label: voter's new label
        :return: if the voter was edited successfully or not
        """

        # Avoid duplicates (unique labels!)
        for added_index, added_voter in enumerate(self.__voters):
            if added_voter.get_label() == label and added_index != index:
                self.__on_voter_error("Un votant avec ce nom existe déjà.")
                return False

        self.__voters[index].set_label(label)
        if self.__on_voter_edited is not None:
            self.__on_voter_edited(self.__voters[index], index)

        return True

    def is_voters_empty(self) -> bool:
        """
        Returns whether the list of voters is empty or not.
        :return: bool(is list voters empty?)
        """

        return len(self.__voters) == 0

    def clear_voters(self):
        """
        Clears all voters.
        """

        self.__voters.clear()
        if self.__on_voters_cleared is not None:
            self.__on_voters_cleared()

    def set_voter_added_callback(self, callback: Callable[[Voter, int], None]):
        """
        Sets the (on voter added) callback, which is called when
        a voter is added to the data.

        :param callback: the callback function, takes a Voter and their index in the data
        """
        self.__on_voter_added = callback

    def set_voter_edited_callback(self, callback: Callable[[Voter, int], None]):
        """
        Sets the (on voter edited) callback, which is called when
        a voter is edited inside the data.

        :param callback: the callback function, takes a Voter and their index in the data
        """
        self.__on_voter_edited = callback

    def set_voters_cleared_callback(self, callback: Callable[[], None]):
        """
        Sets the (on voters cleared) callback, which is called when
        all voters are cleared from the data.

        :param callback: the callback function
        """
        self.__on_voters_cleared = callback

    def set_voter_error_callback(self, callback: Callable[[str], None]):
        """
        Sets the (on voter error) callback, which is called when
        an error occurs with a voter.

        :param callback: the callback function
        """
        self.__on_voter_error = callback

    # Candidate

    def __get_letter_count(self, index: int) -> int:
        """
        Returns the letter count for a label at a given index.
        """

        labels_before_index = 0
        letter_count = 0

        # Search how many powers of 26 can fit before reaching the
        # given index. We don't want to use log_26 because if we have
        # a two-lettered label, then we would have already filled the
        # one-lettered possibilities. So if we have a 676 (26^2) index,
        # then that means it already contains the 26 one-lettered labels,
        # so the label only becomes three-lettered if 676+26=702 is reached.
        while labels_before_index < index:
            letter_count += 1
            labels_before_index += 26 ** letter_count
        return letter_count

    def __purify(self, number: int) -> int:
        """
        Returns the corresponding number based on the number of letters.

        Example:

        0 -> A
        25 -> Z

        If the given number is 26, that should correspond to A, and it returns 0.

        It may look like this is working the same as modulo because it's quite
        similar. The modulo operator gives us the remainder of the division by a
        number, by removing multiples of that number. This gives us the remainder
        by removing powers of the number.

        Now if the number is 676 for instance, this will return 650 and not 0. Why?
        Because if we have a two-lettered label, then we would have already filled the
        one-lettered possibilities. So if we have a 676 (26^2) index, then that means
        it already contains the 26 one-lettered labels, so the label only becomes
        three-lettered if 676+26=702 is reached. So if we reached 676, then that means
        we need to deal with one more set of 26s before resetting.
        """

        i = 1
        while number >= 26 ** i:
            number -= 26 ** i
            i += 1
        return number

    def __get_label_for(self, index: int) -> str:
        """
        Generate an adequate label for the candidate at the given index.

        :param index: new candidate at index needing a label
        :return: generated label
        """
        new_candidate_index = index
        label_letter_count = self.__get_letter_count(new_candidate_index + 1)

        label = ""
        for i in reversed(range(1, label_letter_count + 1)):
            label += chr(ord('A') + (self.__purify(new_candidate_index) % (26 ** i) // (26 ** (i - 1))))

        return label

    def add_candidate(self, coordinates: tuple[float, float], label=None, color=None) -> bool:
        """
        Adds a candidate to the data.

        :param coordinates: candidate's coordinates
        :param label: candidate's label
        :param color: candidate's color
        :return: whether the candidate has been added or not
        """

        # Generate label
        if label is None:
            label = self.__get_label_for(len(self.__candidates))

        # Avoid duplicates (unique labels!)
        added_labels = [added_candidate.get_label() for added_candidate in self.__candidates]
        label_offset = 0
        while label in added_labels:
            label_offset += 1
            label = self.__get_label_for(len(self.__candidates) + label_offset)

        # Create a new candidate
        if color is None or color not in mcolors.XKCD_COLORS.values():
            candidate = Candidate.random_color(label=label, coordinates=coordinates)
        else:
            candidate = Candidate(label, coordinates, color)

        self.__candidates.append(candidate)
        if self.__on_candidate_added is not None:
            self.__on_candidate_added(candidate, len(self.__candidates) - 1)

        return True

    def get_candidates(self) -> list[Candidate]:
        """
        Returns the list of candidates.

        :return: list of candidates in data
        """
        return self.__candidates

    def get_candidate_at(self, index: int) -> Candidate:
        """
        Returns the candidate at the given index.

        :param index: index of the desired candidate
        :return: candidate at given index
        """

        return self.__candidates[index]

    def edit_candidate_at(self, index: int, label: str, color: str) -> bool:
        """
        Modifies the candidate label and color at the given index.

        :param index: index of the desired candidate
        :param label: candidate's new label
        :param color: candidate's new color
        :return: if the candidate was edited successfully or not
        """

        # Avoid duplicates (unique labels!)
        for added_index, added_candidate in enumerate(self.__candidates):
            if added_candidate.get_label() == label and added_index != index:
                self.__on_candidate_error("Un candidat avec ce nom existe déjà.")
                return False

        self.__candidates[index].set_label(label)
        self.__candidates[index].set_color(color)
        if self.__on_candidate_edited is not None:
            self.__on_candidate_edited(self.__candidates[index], index)

        return True

    def is_candidates_empty(self) -> bool:
        """
        Returns whether the list of candidates is empty or not.
        :return: bool(is list candidates empty?)
        """

        return len(self.__candidates) == 0

    def clear_candidates(self):
        """
        Clears all candidates.
        """

        self.__candidates.clear()
        if self.__on_candidates_cleared is not None:
            self.__on_candidates_cleared()

    def set_candidate_added_callback(self, callback: Callable[[Candidate, int], None]):
        """
        Sets the (on candidate added) callback, which is called when
        a candidate is added to the data.

        :param callback: the callback function, takes a Candidate and their index in the data
        """
        self.__on_candidate_added = callback

    def set_candidate_edited_callback(self, callback: Callable[[Candidate, int], None]):
        """
        Sets the (on candidate edited) callback, which is called when
        a candidate is edited inside the data.

        :param callback: the callback function, takes a Candidate and their index in the data
        """
        self.__on_candidate_edited = callback

    def set_candidates_cleared_callback(self, callback: Callable[[], None]):
        """
        Sets the (on candidates cleared) callback, which is called when
        all candidates are cleared from the data.

        :param callback: the callback function
        """
        self.__on_candidates_cleared = callback

    def set_candidate_error_callback(self, callback: Callable[[str], None]):
        """
        Sets the (on candidate error) callback, which is called when
        an error occurs with a candidate.

        :param callback: the callback function
        """
        self.__on_candidate_error = callback
