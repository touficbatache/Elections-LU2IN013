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


    def veto(self, candidates,profils):
        """
        Implementation of veto sorting method
        """
        # profils = {...<voter label>: <profil>...}
        # profil = list(...tuple(<candidate label>, <distance between candidate and voter>)...)

        # dict ({ str("candidate_label") : tuple(point, annotation) })
        # __candidates = dict()
        # print(profils)

        v_scores = dict()
        for candidat in candidates :
            v_scores[candidat.label()] = 0
    
        current_cand_lab = ""
        for voter_label, one_profil in profils.items():
            for i in range(len(one_profil)-2):
                current_cand_lab, _ = one_profil[i]
                v_scores[current_cand_lab] += 1
        
        #print(v_scores)
        winners = {k:v for k,v in v_scores.items() if v == sorted(v_scores.values(), reverse=True)[0]}
        
        #print(self.__departage(list(winners)))
        return self.__departage(list(winners))
    
    

    def __find_winner(self, results: dict) -> tuple[str, bool, list]:
        """
        Finds the winner in a dictionary of candidates and scores.
        If the list contains one winner, it returns it. If not, it
        chooses one based on alphabetical order (asc).

        :param results: dictionary of results (..., candidate_label : score, ...)
        :return: tuple(str(winner label), bool(multiple winners?), list(all winners' labels))
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
        :return: tuple(str(winner label), bool(multiple winners?), list(all winners' labels))
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

    def pluralite_simple(self, profils: dict) -> tuple[str, bool, list]:
        """
        Returns the winner according to simple majority voting method.
        Returns the first in alphabetical order in case of equality.

        :param profils: dictionary of votes registered by the voters
        :return tuple(str(winner label), bool(multiple winners?), list(all winners' labels))
        """
        points_association = dict()

        for candidate in profils.values():
            candidate_label, _ = candidate[0]
            if candidate_label not in points_association:
                points_association[candidate_label] = 0
            points_association[candidate_label] += 1

        return self.__find_winner(points_association)

    def borda(self, profils: dict, maximum: int) -> tuple[str, bool, list]:
        """
        Returns the winner according to Borda voting method.

        In this system, the candidates are given a score based on the maximum score given by the user.
        The first candidate received the max points, the second -> max-1, the third -> max-2, ...
        If the number of candidates is higher than max, the remaining candidates [max; nb_candidates]
        will receive the score of 0.
        In case of equality, the function returns the first in alphabetical order.

        :param profils: dictionary of votes registered by the voters
        :param maximum: maximum score to attribute to the top candidate
        :return: tuple(str(winner label), bool(multiple winners?), list(all winners' labels))
        """
        points_association = dict()

        for profil in profils.values():
            for i, (candidate_label, _) in enumerate(profil):
                if candidate_label not in points_association:
                    points_association[candidate_label] = 0
                if (maximum - i) > 0:
                    points_association[candidate_label] += maximum - i

        return self.__find_winner(points_association)
