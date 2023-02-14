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
        Finds the winner in a dictonnary of candidates and scores.
        If the list contains one winner, it returns it. If not, it
        chooses one based on alphabetical order (asc).

        :param results: dictionnary of results (..., candidate_label : score, ...)
        :return: Couple of winner and boolean indicating if winner is raw-win or decided
        """
        winners = [k for k, v in results.items() if v == sorted(results.values(), reverse=True)[0]]
        return self.__departage(winners), len(winners) > 1, winners

    def veto(self, candidates: list, profils: dict) -> str:
        """
        Implementation of veto sorting method
        """
        
        v_scores = dict()
        for candidat in candidates :
            v_scores[candidat.label()] = 0
    
        current_cand_lab = ""
        for voter_label, one_profil in profils.items():
            for i in range(len(one_profil)-2):
                current_cand_lab, _ = one_profil[i]
                v_scores[current_cand_lab] += 1

        winners = {k:v for k,v in v_scores.items() if v == sorted(v_scores.values(), reverse=True)[0]}
    
        return self.__departage(list(winners))
