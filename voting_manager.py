class VotingManager:
    """
    Managing class for the different voting systems.
    """

    # TODO: Add the voting you're working on below, as follows:
    #  def pluralite_simple(...):
    #    ...

    def __departage(self, candidates: list, reverse=False) -> str:
        """
        Returns the first element of the alphabetically sorted list of candidates.

        :param candidates: the list of candidate labels
        """
        return sorted(candidates, key=str.casefold, reverse=reverse)[0]

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

    def __count_scores(self, profils: dict) -> dict:
        """

        :param profils: dictionary of the scores of each voter
        :return: dictionary of the updated scores of each voter
        """
        scores = dict()

        for _, preferences in profils.items():
            label = preferences[0][0]
            if label not in scores:
                scores[label] = 1
            else:
                scores[label] += 1
        return scores

    def elimination_successive(self, profils: dict) -> tuple:
        """

        :param profils: dictionary of the scores of each voter
        :return: the winning candidate
        """
        scores = self.__count_scores(profils)
        majorite = len(profils) / 2

        while scores:
            scores = self.__count_scores(profils)
            losers = [k for k, v in scores.items() if v == sorted(scores.values(), reverse=False)[0]]

            for candidate, points in scores.items():
                if points > majorite:
                    return candidate, False

            letter = self.__departage(losers, True)
            scores.pop(letter)

            for _, profil in profils.items():
                for candidate, _ in profil:
                    if candidate == letter:
                        profil.remove((candidate, _))
                        break
