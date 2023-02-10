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

    def __find_winner(self, results: dict) -> tuple[str, bool]:
        """
        Finds the winner in a dictonnary of candidates and scores.
        If the list contains one winner, it returns it. If not, it
        chooses one based on alphabetical order (asc).

        :param results: dictionnary of results (..., candidate_label : score, ...)
        :return: Couple of winner and boolean indicating if winner is raw-win or decided
        """
        max_score = 0
        winners = []
        for candidate_label, score in results.items():
            if score > max_score:
                max_score = score
                winners = [candidate_label]
            elif score == max_score:
                winners.append(candidate_label)
        if len(winners) == 1:
            return winners[0], False
        else:
            return self.__departage(winners), True
