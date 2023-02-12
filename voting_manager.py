class VotingManager:
    """
    Managing class for the different voting systems.
    """

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

    def approbation(self, profils: dict, approval_radius: int) -> tuple[str, bool, list] | None:
        """
        Approval voting system (système de vote par approbation).

        In this voting system, voters can show support for one or more candidates
        by voting "yes / no" for each one. Approval is given if the voter is
        within an approval circle whose radius is defined by the user.

        :param profils: Scores for each voter
        :param approval_radius: Radius of the approval circle
        :return: tuple(str(winner label), bool(multiple winners?), list(all winners' labels))
        """
        results = dict()
        for voter_label, profil in profils.items():
            for candidate_label, score in profil:
                if (score * 100) >= 100 - approval_radius:
                    if candidate_label not in results:
                        results[candidate_label] = 0
                    results[candidate_label] += 1

        if len(results) == 0:
            return None

        return self.__find_winner(results)
