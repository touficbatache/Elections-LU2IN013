class VotingManager:
    """
    Managing class for the different voting systems.
    """

    def __departage(self, candidate_labels: list, reverse: bool = False) -> str:
        """
        Returns the first or last element of the alphabetically sorted list of candidates.

        :param candidate_labels: the list of candidate labels
        """
        return sorted(candidate_labels, key=str.casefold, reverse=reverse)[0]

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
        Counts the scores of the candidates based on the preferences of the voters

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

    def elimination_successive(self, profils: dict) -> tuple[str, bool, list]:
        """
        Returns the winner according to Single transferable vote (STV) system.
        Eliminates the last candidate in alphabetical order in case of equality.

        :param profils: dictionary of the scores of each voter
        :return: the winning candidate
        """
        scores = self.__count_scores(profils)
        majority = len(profils) / 2

        while scores:
            scores = self.__count_scores(profils)

            for candidate, points in scores.items():
                if points > majority:
                    return candidate, False, []

            # Find the list of labels of all candidates who had the lowest score
            losers = [label for label, score in scores.items() if score == sorted(scores.values(), reverse=False)[0]]

            # Remove the candidate whose label is last in alphabetical order
            letter = self.__departage(losers, True)
            scores.pop(letter)

            for _, profil in profils.items():
                for candidate, _ in profil:
                    if candidate == letter:
                        profil.remove((candidate, _))
                        break

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

    def pluralite_simple(self, profils):
        """
        Returns the winner according to simple majority voting method.
        Returns the first in alphabetical order in case of equality.

        :param profils: dictionnary of votes registered by the voters
        :return Couple of winner and boolean indicating if winner is raw-win or decided
        """
        votes = list(profils.values())
        points_association = dict()

        for candidate in votes:
            if candidate[0][0] not in points_association:
                points_association[candidate[0][0]] = 0
            points_association[candidate[0][0]] += 1

        return self.__find_winner(points_association)

    def borda(self, profils: dict, maximum: int) -> tuple[str, bool, list]:
        """
        Returns the winner according to Borda voting method. Returns the first in alphabetical order in case of equality.

        :param profils: dictionary of votes registered by the voters
        :param maximum: maximum score to attribute to the top candidates
        :return: Couple of winner and boolean indicating if winner is raw-win or decided
        """
        votes = list(profils.values())
        points_association = dict()
        number_candidates = len(votes[0])

        for candidate_list in votes:
            for i in range(number_candidates):
                candidate_label = candidate_list[i][0]
                if candidate_label not in points_association:
                    points_association[candidate_label] = 0
                if (maximum - i) > 0:
                    points_association[candidate_label] += maximum - i

        return self.__find_winner(points_association)
