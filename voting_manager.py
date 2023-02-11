class VotingManager:
    """
    Managing class for the different voting systems.
    """

    # TODO: Add the voting you're working on below, as follows:
    #  def pluralite_simple(...):
    #    ...

    def __departage(self, candidate_labels: list) -> str:
        """
        Returns the first element of the alphabetically sorted list of candidates.

        :param candidate_labels: the list of candidate labels
        """
        return sorted(candidate_labels, key=str.casefold)[0]

    def __find_winner(self, results: dict) -> tuple[str, bool, list]:
        """
        Finds the winner in a dictionary of candidates and scores.
        If the list contains one winner, it returns it. If not, it
        chooses one based on alphabetical order (asc).

        :param results: dictionary of results (..., candidate_label : score, ...)
        :return: Couple of winner and boolean indicating if winner is raw-win or decided
        """
        winners = [
            candidate_label
            for candidate_label, score in results.items()
            if score == sorted(results.values(), reverse=True)[0]
        ]
        return self.__departage(winners), len(winners) > 1, winners
