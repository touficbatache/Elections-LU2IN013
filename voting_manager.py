class VotingManager:
    """
    Managing class for the different voting systems.
    """

    # TODO: Add the voting you're working on below, as follows:
    #  def pluralite_simple(...):
    #    ...

    @staticmethod
    def departage(candidates: list):
        """
        Returns the first element of the alphabetically sorted list of candidates.

        :param candidates: the list of candidates
        """
        return (candidates.sort(key=str.lower))[0]
