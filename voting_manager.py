from collections import defaultdict
from enum import Enum


class CondorcetMethod(Enum):
    COPELAND = 1
    SIMPSON = 2


class CondorcetTieBreakingRule(Enum):
    RANDOM = 1
    ORDRE_LEXICO = 2


class VotingManager:
    """
    Managing class for the different voting systems.
    """

    KEY_WINS = "wins"
    KEY_LOSSES = "losses"

    def __departage(self, candidate_labels: list, reverse: bool = False) -> str:
        """
        Returns the first or last element of the alphabetically sorted list of candidates.

        :param candidate_labels: the list of candidate labels
        """
        return sorted(candidate_labels, key=str.casefold, reverse=reverse)[0]

    def __find_winners(self, results: dict, reverse:bool = True) -> list[str]:
        """
        Finds the winners in a dictionary of candidates and scores.

        :param results: dictionary of results (..., candidate_label : score, ...)
        :param reverse: whether to select winners by max or min score
        :return: list(winners' labels)
        """
        return [
            candidate_label
            for candidate_label, score in results.items()
            if score == sorted(results.values(), reverse=reverse)[0]
        ]

    def __find_winner(self, results: dict) -> tuple[str, bool, list]:
        """
        Finds the winner in a dictionary of candidates and scores.
        If the list contains one winner, it returns it. If not, it
        chooses one based on alphabetical order (asc).

        :param results: dictionary of results (..., candidate_label : score, ...)
        :return: tuple(str(winner label), bool(multiple winners?), list(all winners' labels))
        """
        winners = self.__find_winners(results)
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

    def borda(self, profils: dict, maximum: int, step: int) -> tuple[str, bool, list]:
        """
        Returns the winner according to Borda voting method.

        In this system, the candidates are given a score based on the maximum score given by the user.
        The first candidate received the max points, the second -> max-step, the third -> max-2*step, ...
        If the number of candidates is higher than max, the remaining candidates [max; nb_candidates]
        will receive the score of 0.
        In case of equality, the function returns the first in alphabetical order.

        :param step: step between two scores (ex: if max=100 and step=5, score attribution: 100, 95, 90, ...)
        :param profils: dictionary of votes registered by the voters
        :param maximum: maximum score to attribute to the top candidate
        :return: tuple(str(winner label), bool(multiple winners?), list(all winners' labels))
        """
        points_association = dict()

        for profil in profils.values():
            for i, (candidate_label, _) in enumerate(profil):
                if candidate_label not in points_association:
                    points_association[candidate_label] = 0
                if (maximum - (i * step)) > 0:
                    points_association[candidate_label] += maximum - (i * step)

        return self.__find_winner(points_association)

    def veto(self, profils: dict) -> tuple[str, bool, list]:
        """
        Implementation of veto sorting method : 0 for the last candidate in each profil, 1 for the rest

        :param profils: dictionary of votes registered by the voters
        :return: tuple(str(winner label), bool(multiple winners?), list(all winners' labels))
        """

        veto_scores = dict()

        for profil in profils.values():
            if len(profil) == 1 :
                return profil[0][0], False, []

            for candidate_label, _ in profil[:-1]:
                if candidate_label not in veto_scores:
                    veto_scores[candidate_label] = 0
                veto_scores[candidate_label] += 1

        return self.__find_winner(veto_scores)

    def condorcet(
            self,
            profils: dict,
            method: CondorcetMethod,
            tie_breaking_rule: CondorcetTieBreakingRule
    ) -> tuple[str, bool, bool, list | None]:
        """
        Condorcet voting system.

        In this voting system, we start by generating pairs for each 2 candidates
        and organizing duels between them. In order to win, the candidate's score
        must be strictly greater than his opponent's. In the case of a tie,
        neither the candidate nor their opponent are added to any of the "wins" or
        "losses" tables: we simply do nothing.

        If a candidate wins all his duels (loses none), then he is the Condorcet winner.

        If not, we resort to using the method given as an argument to the method.

        If there are multiple winners, we use the tie-breaking rule given as argument.

        :param profils: Scores for each voter
        :param method: Method to use in case there is no Condorcet winner
        :param tie_breaking_rule: Tie-breaking rule to use in order to decide who wins
        :return: tuple(
                    str(winner label),
                    bool(used given method?),
                    bool(used tie-breaking rule?),
                    list(all winners' labels)
                )
        """
        # Candidate labels list
        candidate_labels = [candidate_label for candidate_label, _ in list(profils.values())[0]]

        # Give the winner directly if there's one candidate
        if len(candidate_labels) == 1:
            return candidate_labels[0], False, False, None

        # We organise duels and calculate scores
        duel_scores = list()
        for candidate1_label in candidate_labels:
            for candidate2_label in candidate_labels:
                # so that we have unique pairs (combination)
                if candidate2_label > candidate1_label:
                    current_duel = {candidate1_label: 0, candidate2_label: 0}
                    for profil in profils.values():
                        for candidate_label, _ in profil:
                            if candidate_label in current_duel:
                                current_duel[candidate_label] += 1
                                break
                    duel_scores.append(current_duel)

        # We try and see if there's a Condorcet winner
        duel_results = defaultdict(lambda: defaultdict(list))
        for duel_score in duel_scores:
            loser, winner = sorted(duel_score.keys(), key=lambda k: duel_score[k])

            if duel_score[winner] != duel_score[loser]:
                duel_results[winner][self.KEY_WINS].append(loser)
                duel_results[loser][self.KEY_LOSSES].append(winner)

        try:
            # Condorcet winner success
            winner = next(
                candidate_label
                for candidate_label, results in duel_results.items()
                if len(results[self.KEY_LOSSES]) == 0
            )
            return winner, False, False, None
        except StopIteration:
            # Condorcet winner fail: there's no Condorcet winner
            # We have to use method given as an argument
            winners = None
            match method:
                # Copeland method
                case CondorcetMethod.COPELAND:
                    winners = self.__condorcet_winners_copeland(duel_scores)
                # Simpson method
                case CondorcetMethod.SIMPSON:
                # TODO: Implement Simpson
                    winners = self.__condorcet_winners_simpson(duel_scores)



            # If we have only one winner, return them
            if len(winners) == 1:
                return winners[0], True, False, None
            # If not, use the tie-breaking rule given as an argument
            else:
                # TODO: remove this return when the match is implemented
                return winners[0], True, True, winners

                # match tie_breaking_rule:
                #     case CondorcetTieBreakingRule.ORDRE_LEXICO:
                #         # TODO: Implement alphabetical order tie-breaking
                #         return winners[0], True, winners
                #     case CondorcetTieBreakingRule.RANDOM:
                #         # TODO: Implement random tie-breaking
                #         return winners[0], True, winners

    def __condorcet_winners_copeland(self, duels: list[dict[str, int]]) -> list[str]:
        """
        Condorcet voting system.
        Copeland method.

        For each duel, give the winning candidate 1 point and
        in case of equality, give both 0.5 points.

        Winner is the candidate with most points.

        :param duels: list(..., { candidate1_label: score, candidate2_label: score }, ...)
        :return: list(winners)
        """
        scores = dict()
        for duel in duels:
            duel_items = list(duel.items())
            
            # Assign a score of 0.5 to each candidate in  case of equality
            if duel_items[0][1] == duel_items[1][1]:
                if duel_items[0][0] not in scores:
                    scores[duel_items[0][0]] = 0
                if duel_items[1][0] not in scores:
                    scores[duel_items[1][0]] = 0
                scores[duel_items[0][0]] += 0.5
                scores[duel_items[1][0]] += 0.5
            else:
                # Assign a score of 1 to the winner
                winner_index = 0 if duel_items[0][1] > duel_items[1][1] else 1
                if duel_items[winner_index][0] not in scores:
                    scores[duel_items[winner_index][0]] = 0
                scores[duel_items[winner_index][0]] += 1

        return self.__find_winners(scores)


    def __condorcet_winners_simpson(self, duels: list[dict[str, int]]) -> list[str]:
        """
        Condorcet voting system.
        Simpson method.

        The winner is the candidate whose highest defeat score in duels is the lowest among the other candidates.
        :param duels: list(..., { candidate1_label: score, candidate2_label: score }, ...)
        :return: list(winners)
        """
        # type : { cand1:[difference des DEFAITES de cand1], ... , candN:[difference des DEFAITES de candn] }
        defeatscores = defaultdict(list)

        for duel in duels:
            duel_items = list(duel.items()) #Creating list of couples in a single duel -> list(tuple): 
        
            #Initializing the score differences list
            if duel_items[0][1] < duel_items[1][1] :
                defeatscores[duel_items[0][0]].append(abs(duel_items[0][1] - duel_items[1][1] ))
            elif duel_items[0][1] > duel_items[1][1] :
                defeatscores[duel_items[1][0]].append(abs(duel_items[0][1] - duel_items[1][1] ))
            else :
                defeatscores[duel_items[1][0]].append(0)
                defeatscores[duel_items[0][0]].append(0)

        maxdefeat = dict()

        for label, listscore in defeatscores.items() :
            maxdefeat[label] = max(listscore)

        return self.__find_winners(maxdefeat, reverse=False)
        