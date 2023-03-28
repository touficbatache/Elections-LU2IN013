import hashlib
import random
import tkinter as tk
from tkinter import ttk
from collections import defaultdict
from enum import Enum
from data_manager import DataManager


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
    KEY_DRAWS = "draws"

    data_manager = DataManager()

    def __departage(self, candidate_labels: list, reverse: bool = False) -> str:
        """
        Returns the first or last element of the alphabetically sorted list of candidates.

        :param candidate_labels: the list of candidate labels
        :param reverse: reverse sorted() order used for elimination_successive
        :return the winner's label according to alphabetical sorting
        """
        return sorted(candidate_labels, key=str.casefold, reverse=reverse)[0]

    def __find_winners(self, results: dict, reverse: bool = True) -> list[str]:
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

    def __create_scrollbar(self, frame, nb_candidates):
        # Create a Frame container to put in it the results and make it scrollable in case of multiple round
        container = ttk.Frame(frame, width=480, height=300)
        canvas = tk.Canvas(container, width=420, height=300)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, width=360, height=300)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        container.pack()
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return scrollable_frame

    def __details_scores(self, frame, scores: dict, candidates: list, winner: tuple[str, bool, list]):
        """
        Displays score details for Veto, Borda, Approbation and Simple purality.

        :param frame: Frame to fill with labels with score details
        :param scores: dictionary of scores regarding each candidate
        :param candidates: list of all the candidates participating in the election
        :param winner: tuple(str(winner label), bool(multiple winners?), list(all winners' labels)) or None if no winner
        """
        nb_candidates = len(candidates)
        tk.Label(frame, text="Les scores des votes :", font=("Mistral", "15", "bold")).grid(row=0, columnspan=nb_candidates if nb_candidates < 12 else 12, column=0)

        i = 0
        row_upgrade = 0
        for candidate in candidates:
            candidate_label = candidate.get_label()
            if i % 12 == 0 :
                i = 0
                row_upgrade += 1
            if candidate_label in scores.keys():
                tk.Label(frame, text=candidate_label + " : " + str(scores[candidate_label])).grid(row=row_upgrade, column=i)
            else:
                tk.Label(frame, text=candidate_label + " : 0").grid(row=row_upgrade, column=i)
            i += 1

        row_upgrade += 1

        if winner is not None:
            if not winner[1]:
                tk.Label(frame, text="Le gagnant est : " + winner[0], font=("Mistral", "15", "bold")).grid(row=row_upgrade, columnspan=nb_candidates if nb_candidates < 12 else 12, column=0)
            else:
                tk.Label(frame, text="Le gagnant a été départagé :", font=("Mistral", "15", "bold")).grid(row=row_upgrade, columnspan=nb_candidates if nb_candidates < 12 else 12, column=0)
                tk.Label(frame, text=winner[0] + " a gagné parmi " + str(winner[2])).grid(row=row_upgrade + 1, columnspan=nb_candidates if nb_candidates < 12 else 12, column=0)
        else:
            tk.Label(frame, text="Aucun gagnant trouvé", font=("Mistral", "15", "bold")).grid(row=row_upgrade, columnspan=nb_candidates if nb_candidates < 12 else 12, column=0)
            tk.Label(frame, text="Avec les données fournis, aucun gagnant peut être déterminé.", wraplength=nb_candidates*30 if nb_candidates < 12 else 360).grid(row=row_upgrade + 1, columnspan=nb_candidates if nb_candidates < 12 else 12, column=0)

    def elimination_successive_details(self, frame):
        """
        Gives a definition of STV voting system.

        :param frame: Frame from which voting method details popup should generate
        """
        top_details_elim = tk.Toplevel(frame)
        top_details_elim.title("Elimination Successive - Définition")

        tk.Label(top_details_elim, text="Description du mode de vote :", font=("Mistral", "15", "bold")).grid(row=0, column=0)
        tk.Label(top_details_elim,
                 text="Le vote par Elimination succéssive est un vote itérative. S'il existe un "
                      "candidat classé premier (1er) par une majorité de votants alors il est élu "
                      "directement gagnat. Sinon, le candidat classé premier (1er) par le moins de votants "
                      "est  élimine de tous les votes. Les votes de ce candidat sont transférés au meilleur "
                      "candidat restant. Cette condition est répétée jusqu'à ce qu'il existe un candidat "
                      "classé premier (1er) par une majorité de votants",
                 wraplength=250).grid(row=1, column=0)

    def elimination_successive(self, profils: dict, frame=None) -> tuple[str, bool, list] | None:
        """
        Returns the winner according to Single transferable vote (STV) system.
        Eliminates the last candidate in alphabetical order in case of equality.

        :param profils: dictionary of the scores of each voter
        :param frame: Frame from which score details popup should generate
        :return: tuple(str(winner label), bool(multiple winners?), list(all winners' labels))
        """
        if frame:
            # Generate TopLevel popup for scores details
            top_step_elim = tk.Toplevel(frame)
            top_step_elim.title("Elimination succéssive - Résultat détaillé")

            # Get list of candidates
            candidates = self.data_manager.get_candidates()
            # Get number of candidates
            nb_candidates = len(candidates)
            # Tracker for the round number
            round_number = 1
            # Grid row manager for the frame labels grid position
            grid_row_manager = 0

            scrollable_frame = self.__create_scrollbar(top_step_elim, nb_candidates)

        scores = self.__count_scores(profils)
        majority = len(profils) / 2

        while scores:
            scores = self.__count_scores(profils)

            if frame:
                ttk.Label(scrollable_frame, text="Score du tour #" + str(round_number) + " :", font=("Mistral", "15", "bold")).grid(row=grid_row_manager, column=0, columnspan=nb_candidates if nb_candidates < 12 else 12)
                row_uprade = -1
                i = 0
                for candidate in candidates:
                    candidate_label = candidate.get_label()
                    if i % 12 == 0:
                        row_uprade += 1
                        i = 0
                    if candidate_label in scores.keys():
                        ttk.Label(scrollable_frame, text=candidate_label + " : " + str(scores[candidate_label])).grid(row=grid_row_manager + row_uprade + 1, column=i)
                    else:
                        ttk.Label(scrollable_frame, text=candidate_label + " : 0").grid(row=grid_row_manager + row_uprade + 1, column=i)
                    i += 1
                round_number += 1
                grid_row_manager += 2 + row_uprade

            for candidate, points in scores.items():
                if points > majority:
                    if frame is None:
                        return candidate, False, []
                    else:
                        ttk.Label(scrollable_frame, text="Gagnant par majorité (>" + str(majority) + ") : " + candidate, font=("Mistral", "13", "bold")).grid(row=grid_row_manager, column=0, columnspan=nb_candidates if nb_candidates < 12 else 12)
                        return

            # Find the list of labels of all candidates who had the lowest score
            losers = [
                label
                for label, score in scores.items()
                if score == sorted(scores.values(), reverse=False)[0]
            ]

            if frame:
                ttk.Label(scrollable_frame, text="Pas de gagnant par majorité dans ce tour.",
                        wraplength=250).grid(row=grid_row_manager, columnspan=nb_candidates if nb_candidates < 12 else 12, column=0)
                grid_row_manager += 1

            # Remove the candidate whose label is last in alphabetical order
            letter = self.__departage(losers, True)
            scores.pop(letter)
            if frame:
                ttk.Label(scrollable_frame, text="Candidat éliminé au tour #" + str(round_number - 1) + " : " + letter).grid(row=grid_row_manager, columnspan=nb_candidates if nb_candidates < 12 else 12, column=0)
                ttk.Label(scrollable_frame, text=" ").grid(row=grid_row_manager + 1, column=0, columnspan=nb_candidates if nb_candidates < 12 else 12)
                grid_row_manager += 2

            for _, profil in profils.items():
                for candidate, _ in profil:
                    if candidate == letter:
                        profil.remove((candidate, _))
                        break

    def approbation_datails(self, approval_radius: int, frame):
        """
        Gives a definition of Approbation voting system.

        :param approval_radius: Radius of the approval circle
        :param frame: Frame from which voting method details popup should generate
        """
        top_details_approbation = tk.Toplevel(frame)
        top_details_approbation.title("Approbation - Définition")

        tk.Label(top_details_approbation, text="Description du mode de vote :", font=("Mistral", "15", "bold")).grid(row=0, column=0)
        tk.Label(top_details_approbation,
                 text="Le vote par approbation est un vote similaire à une situation de Oui ou Non. Les candidats présents "
                      "dans la zone d'approbation du voteur (dans ce cas : " + str(approval_radius) + "% de la distance maximale) "
                      "recoivent un (1) point de la part du voteur. Les candidats en dehors de cette zone recoivent par conséquent "
                      "un score de zéro (0). Les scores des différents voteurs sont ensuite ajoutés pour déterminer le vainqueur. "
                      "Le candidat ayant le score le plus élevé gagne les éléctions. Si tout les candidats se trouvent hors des zones "
                      "d'approbation, aucun candidat gagne. En cas d'égalité, le gagnant est départagé par ordre lexicographique "
                      "croissant (A -> Z).",
                 wraplength=250).grid(row=1, column=0)

    def approbation(self, profils: dict, approval_radius: int, frame=None) -> tuple[str, bool, list] | None:
        """
        Approval voting system (système de vote par approbation).

        In this voting system, voters can show support for one or more candidates
        by voting "yes / no" for each one. Approval is given if the voter is
        within an approval circle whose radius is defined by the user.

        :param profils: Scores for each voter
        :param approval_radius: Radius of the approval circle
        :param frame: Frame from which score details popup should generate
        :return: tuple(str(winner label), bool(multiple winners?), list(all winners' labels))
        """
        if frame:
            top_step_approbation = tk.Toplevel(frame)
            top_step_approbation.title("Approbation - Résultat détaillé")
            candidates = self.data_manager.get_candidates()

        results = dict()

        for voter_label, profil in profils.items():
            for candidate_label, score in profil:
                if (score * 100) >= 100 - approval_radius:
                    if candidate_label not in results:
                        results[candidate_label] = 0
                    results[candidate_label] += 1

        if frame is None:
            if len(results) == 0:
                return None
            return self.__find_winner(results)
        else:
            if len(results) == 0:
                self.__details_scores(top_step_approbation, results, candidates, None)
            else:
                self.__details_scores(top_step_approbation, results, candidates, self.__find_winner(results))

    def pluralite_simple_details(self, frame):
        """
        Gives a definition of simple plurality voting system.

        :param frame: Frame from which voting method details popup should generate
        """
        top_details_pluralite = tk.Toplevel(frame)
        top_details_pluralite.title("Pluralité Simple - Définition")

        tk.Label(top_details_pluralite, text="Description du mode de vote :", font=("Mistral", "15", "bold")).grid(row=0, column=0)
        tk.Label(top_details_pluralite,
                 text="Le vote par pluralité simple est un vote qui prend en compte le premier vote de chaque voteur. "
                      "Le candidat le mieux classé gagne un (1) point dans chaque liste de vote et les scores sont ajoutés. "
                      "Le candidat ayant le score le plus élevé gagne les éléctions. En cas d'égalité, le gagnant est départagé "
                      "par ordre lexicographique croissant (A -> Z).",
                 wraplength=250).grid(row=1, column=0)

    def pluralite_simple(self, profils: dict, frame=None) -> tuple[str, bool, list] | None:
        """
        Returns the winner according to simple majority voting method.
        Returns the first in alphabetical order in case of equality.

        :param profils: dictionary of votes registered by the voters
        :param frame: Frame from which score details popup should generate
        :return tuple(str(winner label), bool(multiple winners?), list(all winners' labels))
        """
        if frame:
            top_step_pluralite = tk.Toplevel(frame)
            top_step_pluralite.title("Pluralité Simple - Résultat détaillé")
            candidates = self.data_manager.get_candidates()

        points_association = dict()

        for candidate in profils.values():
            candidate_label, _ = candidate[0]
            if candidate_label not in points_association:
                points_association[candidate_label] = 0
            points_association[candidate_label] += 1

        if frame is None:
            return self.__find_winner(points_association)
        else:
            self.__details_scores(top_step_pluralite, points_association, candidates, self.__find_winner(points_association))

    def borda_details(self, maximum: int, step: int, frame):
        """
        Gives a definition of Borda voting system.

        :param step: step between two scores (ex: if max=100 and step=5, score attribution: 100, 95, 90, ...)
        :param maximum: maximum score to attribute to the top candidate
        :param frame: Frame from which vote method details details popup should generate
        """
        top_details_borda = tk.Toplevel(frame)
        top_details_borda.title("Borda - Définition")

        tk.Label(top_details_borda, text="Description du mode de vote :", font=("Mistral", "15", "bold")).grid(row=0, column=0)
        tk.Label(top_details_borda,
                 text="Le vote avec la méthode de Borda est un vote qui attribu à chaque candidat d'un profil de vote un score. "
                      "Le candidat le mieux classé gagne un nombre maximum de point(s) (dans ce cas : " + str(maximum) + "). "
                      "Le candidat suivant recoit un score inférieur au premier en supprimant " + str(step) + " point(s) du score du précédent. "
                      "Les scores sont calculés simultanément. Si le nombre de candidat est supérieur au nombre de scores a attribué "
                      "les candidats restant obtiennent le score de zéro (0). Après addition de tous les profils, le candidat ayant le score "
                      "le plus élevé gagne les éléctions. En cas d'égalité, le gagnant est départagé par ordre lexicographique croissant (A -> Z).",
                 wraplength=250).grid(row=1, column=0)

    def borda(self, profils: dict, maximum: int, step: int, frame=None) -> tuple[str, bool, list] | None:
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
        :param frame: Frame from which score details popup should generate
        :return: tuple(str(winner label), bool(multiple winners?), list(all winners' labels))
        """
        if frame:
            top_step_borda = tk.Toplevel(frame)
            top_step_borda.title("Borda - Résultat détaillé")
            candidates = self.data_manager.get_candidates()

        points_association = dict()

        for profil in profils.values():
            for i, (candidate_label, _) in enumerate(profil):
                if candidate_label not in points_association:
                    points_association[candidate_label] = 0
                if (maximum - (i * step)) > 0:
                    points_association[candidate_label] += maximum - (i * step)

        if frame is None:
            return self.__find_winner(points_association)
        else:
            self.__details_scores(top_step_borda, points_association, candidates, self.__find_winner(points_association))

    def veto_details(self, frame):
        """
        Gives a definition of Veto voting system.

        :param frame: Frame from which vote method details popup should generate
        """
        top_details_veto = tk.Toplevel(frame)
        top_details_veto.title("Veto - Déscription")

        tk.Label(top_details_veto, text="Description du mode de vote :", font=("Mistral", "15", "bold")).grid(row=0, column=0)
        tk.Label(top_details_veto,
                 text="Le vote avec la méthode de Veto est un vote qui attribu à chaque candidat d'un profil de vote le score de "
                      "un (1) point. Par contre le candidat le moins bien classé obtient le score de zéro (0). Les scores des "
                      "différents profils sont ajoutés pour pouvoir déterminer qui est le gagnant. Après addition de tous les profils, "
                      "le candidat ayant le score le plus élevé gagne les éléctions. En cas d'égalité, le gagnant est départagé "
                      "par ordre lexicographique croissant (A -> Z).",
                 wraplength=250).grid(row=1, column=0)

    def veto(self, profils: dict, frame=None) -> tuple[str, bool, list] | None:
        """
        Implementation of veto sorting method : 0 for the last candidate in each profil, 1 for the rest

        :param profils: dictionary of votes registered by the voters
        :param frame: Frame from which score details popup should generate
        :return: tuple(str(winner label), bool(multiple winners?), list(all winners' labels))
        """
        if frame:
            top_step_veto = tk.Toplevel(frame)
            top_step_veto.title("Veto - Résultat détaillé")
            candidates = self.data_manager.get_candidates()

        veto_scores = dict()

        for profil in profils.values():
            if len(profil) == 1:
                return profil[0][0], False, []

            for candidate_label, _ in profil[:-1]:
                if candidate_label not in veto_scores:
                    veto_scores[candidate_label] = 0
                veto_scores[candidate_label] += 1

        if frame is None:
            return self.__find_winner(veto_scores)
        else:
            self.__details_scores(top_step_veto, veto_scores, candidates, self.__find_winner(veto_scores))

    def condorcet_details(self,  method: CondorcetMethod, tie_breaking_rule: CondorcetTieBreakingRule, frame):
        """
        Gives a definition of condorcet voting system.

        :param method: Method to use in case there is no Condorcet winner
        :param tie_breaking_rule: Tie-breaking rule to use in order to decide who wins
        :param frame: Frame from which vote method details popup should generate
        """
        top_details_condorcet = tk.Toplevel(frame)
        top_details_condorcet.title("Condorcet - Définition")

        tk.Label(top_details_condorcet, text="Description du mode de vote :", font=("Mistral", "15", "bold")).grid(row=0, column=0)
        tk.Label(top_details_condorcet,
                 text="Le vote par Condorcet consiste à simuler l'ensemble des duels possibles parmi les "
                      "différents candidats: pour chaque paire de candidats, on détermine le nombre d'électeurs "
                      "ayant voté pour l'un ou l'autre en vérifiant, sur chaque bulletin de vote, comment l'un "
                      "était classé par rapport à l'autre. Ainsi pour chaque duel, il y a un candidat vainqueur. "
                      "S'il y a un unique candidat qui remporte tous ses duels : il s'agit du vainqueur de Condorcet.",
                 wraplength=250).grid(row=1, column=0)
        match method, tie_breaking_rule:
            case CondorcetMethod.COPELAND, CondorcetTieBreakingRule.RANDOM:
                tk.Label(top_details_condorcet,
                         text="Si aucun candidat ne remporte tous ses duels, on peut avoir recours à deux méthodes. Dans "
                              "ce cas, on utilise la méthode de Copeland qui cherche le candidat qui a gagné le plus de "
                              "confrontations. Ce candidat serait donc le vainqueur. Par contre, s'il existe des conflits, "
                              "le candidat vainqueur est choisi au hasard parmi les différents candidats vérifiant la méthode "
                              "de Copeland, suivant des probabilités particulières optimales.",
                         wraplength=250).grid(row=2, column=0)
            case CondorcetMethod.COPELAND, CondorcetTieBreakingRule.ORDRE_LEXICO:
                tk.Label(top_details_condorcet,
                         text="Si aucun candidat ne remporte tous ses duels, on peut avoir recours à deux méthodes. Dans "
                              "ce cas, on utilise la méthode de Copeland qui cherche le candidat qui a gagné le plus de "
                              "confrontations. Ce candidat serait donc le vainqueur. Par contre, s'il existe des conflits, "
                              "le candidat vainqueur est choisi par ordre lexicographique parmi les différents candidats "
                              "vérifiant la méthode de Copeland.",
                         wraplength=250).grid(row=2, column=0)
            case CondorcetMethod.SIMPSON, CondorcetTieBreakingRule.RANDOM:
                tk.Label(top_details_condorcet,
                         text="Si aucun candidat ne remporte tous ses duels, on peut avoir recours à deux méthodes. Dans "
                              "ce cas, on utilise la méthode de de Simpson (minimax) qui choisit le candidat dont la défaite "
                              "max en duel est la plus faible. Ce candidat serait donc le vainqueur. Par contre, s'il existe "
                              "des conflits, le candidat vainqueur est choisi au hasard parmi les différents candidats vérifiant "
                              "la méthode de Simpson, suivant des probabilités particulières optimales.",
                         wraplength=250).grid(row=2, column=0)
            case CondorcetMethod.SIMPSON, CondorcetTieBreakingRule.ORDRE_LEXICO:
                tk.Label(top_details_condorcet,
                         text="Si aucun candidat ne remporte tous ses duels, on peut avoir recours à deux méthodes. Dans "
                              "ce cas, on utilise la méthode de de Simpson (minimax) qui choisit le candidat dont la défaite "
                              "max en duel est la plus faible. Ce candidat serait donc le vainqueur. Par contre, s'il existe "
                              "des conflits, le candidat vainqueur est choisi par ordre lexicographique parmi les différents "
                              "candidats vérifiant la méthode de Simpson.",
                         wraplength=250).grid(row=2, column=0)

    def condorcet(self, profils: dict, method: CondorcetMethod, tie_breaking_rule: CondorcetTieBreakingRule, frame=None) -> tuple[str, bool, bool, list | None] | None:
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
        :param frame: Frame from which score details popup should generate
        :return: tuple(
                    str(winner label),
                    bool(used given method?),
                    bool(used tie-breaking rule?),
                    list(all winners' labels)
                )
        """
        if frame:
            top_step_condorcet = tk.Toplevel(frame)
            top_step_condorcet.title("Condorcet - Résultat détaillé")
            candidates = self.data_manager.get_candidates()
            nb_candidates = len(candidates)

            scrollable_frame = self.__create_scrollbar(top_step_condorcet, nb_candidates)

        # Candidate labels list
        candidate_labels = [candidate_label for candidate_label, _ in list(profils.values())[0]]

        # Give the winner directly if there's one candidate
        if len(candidate_labels) == 1:
            if frame is None:
                return candidate_labels[0], False, False, None
            else:
                ttk.Label(scrollable_frame, text="Il n'y a qu'un unique candidat.").grid(row=0, column=0)
                ttk.Label(scrollable_frame, text="Le gagnant est : " + candidate_labels[0], font=("Mistral", "15", "bold")).grid(row=1, column=0)
                return

        if frame:
            ttk.Label(scrollable_frame, text="Les duels", font=("Mistral", "15", "bold")).grid(row=0, column=0)
            row_manager = 1

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
                    if frame:
                        ttk.Label(scrollable_frame, text="Duel entre " + candidate1_label + " et " + candidate2_label +
                                                         " : " + candidate1_label + " (" + str(current_duel[candidate1_label]) +
                                                         ") " + candidate2_label + " (" + str(current_duel[candidate2_label]) +
                                                         ") ").grid(row=row_manager, column=0)
                        row_manager += 1
                    duel_scores.append(current_duel)

        if frame:
            ttk.Label(scrollable_frame, text=" ").grid(row=row_manager, column=0)
            row_manager += 1

        # We try and see if there's a Condorcet winner
        duel_results = defaultdict(lambda: defaultdict(list))
        for duel_score in duel_scores:
            loser, winner = sorted(duel_score.keys(), key=lambda k: duel_score[k])

            if duel_score[winner] != duel_score[loser]:
                duel_results[winner][self.KEY_WINS].append(loser)
                duel_results[loser][self.KEY_LOSSES].append(winner)
            else:
                duel_results[winner][self.KEY_DRAWS].append(loser)
                duel_results[loser][self.KEY_DRAWS].append(winner)
        if frame:
            ttk.Label(scrollable_frame, text="Les résultats des duels", font=("Mistral", "15", "bold")).grid(row=row_manager, column=0)
            row_manager += 1

            for candidate_label, results in sorted(duel_results.items()):
                ttk.Label(scrollable_frame, text=candidate_label + " gagne " + str(len(results[self.KEY_WINS])) +
                                                 " fois et perd " + str(len(results[self.KEY_LOSSES])) +
                                                 " fois").grid(row=row_manager, column=0)
                row_manager += 1

            ttk.Label(scrollable_frame, text=" ").grid(row=row_manager, column=0)
            row_manager += 1
        try:
            # Condorcet winner success
            winner = next(
                candidate_label
                for candidate_label, results in duel_results.items()
                if len(results[self.KEY_LOSSES]) == 0 and len(results[self.KEY_DRAWS]) == 0
            )
            if frame is None:
                return winner, False, False, None
            else:
                ttk.Label(scrollable_frame, text="Le gagnant de condorcet est : ", font=("Mistral", "15", "bold")).grid(row=row_manager, column=0)
                ttk.Label(scrollable_frame, text=winner, font=("Mistral", "15", "bold")).grid(row=row_manager + 1, column=0)
                return
        except StopIteration:
            # Condorcet winner fail: there's no Condorcet winner
            # We have to use method given as an argument
            if frame:
                ttk.Label(scrollable_frame, text="Pas de gagnant de condorcet", font=("Mistral", "15", "bold")).grid(row=row_manager, column=0)
                ttk.Label(scrollable_frame, text="On utilise la méthode de " + str.lower(method.name)).grid(row=row_manager + 1, column=0)
                row_manager += 2

                ttk.Label(scrollable_frame, text=" ").grid(row=row_manager, column=0)
                row_manager += 1

            winners = None
            match method:
                # Copeland method
                case CondorcetMethod.COPELAND:
                    winners = self.__condorcet_winners_copeland(duel_scores)
                # Simpson method
                case CondorcetMethod.SIMPSON:
                    winners = self.__condorcet_winners_simpson(duel_scores)

            # If we have only one winner, return them
            if len(winners) == 1:
                if frame is None:
                    return winners[0], True, False, None
                else:
                    ttk.Label(scrollable_frame, text="Le gagnant est : ", font=("Mistral", "15", "bold")).grid(row=row_manager, column=0)
                    ttk.Label(scrollable_frame, text=winners[0], font=("Mistral", "15", "bold")).grid(row=row_manager + 1, column=0)
                    return

            # If not, use the tie-breaking rule given as an argument
            else:
                if frame:
                    ttk.Label(scrollable_frame, text="Plusieurs gagnants : " + str(winners), font=("Mistral", "15", "bold"), wraplength=300).grid(row=row_manager, column=0)
                    ttk.Label(scrollable_frame, text="On a recours a la méthode de " + str.lower(tie_breaking_rule.name) + " pour départager entre les différents candidats gagnants", wraplength=300).grid(row=row_manager + 1, column=0)
                    row_manager += 2

                    ttk.Label(scrollable_frame, text=" ").grid(row=row_manager, column=0)
                    row_manager += 1
                match tie_breaking_rule:
                    case CondorcetTieBreakingRule.ORDRE_LEXICO:
                        if frame is None:
                            return self.__departage(winners), True, True, winners
                        else:
                            ttk.Label(scrollable_frame, text="Le gagnant est : ", font=("Mistral", "15", "bold")).grid(row=row_manager, column=0)
                            ttk.Label(scrollable_frame, text=self.__departage(winners), font=("Mistral", "15", "bold")).grid(row=row_manager + 1, column=0)
                            return
                    case CondorcetTieBreakingRule.RANDOM:
                        if frame is None:
                            # return random.choice(winners), True, True, winners
                            return self.__random_choose_winner(winners, duel_results), True, True, winners
                        else:
                            ttk.Label(scrollable_frame, text="Le gagnant est : ", font=("Mistral", "15", "bold")).grid(row=row_manager, column=0)
                            # ttk.Label(scrollable_frame, text=random.choice(winners), font=("Mistral", "15", "bold")).grid(row=row_manager + 1, column=0)
                            # ttk.Label(scrollable_frame, text="Ce résultat peut ne pas s'accorder avec celui donner ultérieurement en cas de départage RANDOM", wraplength=300).grid(row=row_manager + 2, column=0)
                            ttk.Label(scrollable_frame, text=self.__random_choose_winner(winners, duel_results), font=("Mistral", "15", "bold")).grid(row=row_manager + 1, column=0)
                            return

    def __random_choose_winner(self, liste: list, duel_results: dict):
        win_lose_list = ""
        for candidate_label, results in sorted(duel_results.items()):
            if candidate_label in liste:
                win_lose_list += candidate_label + str(len(results[self.KEY_WINS])) + str(len(results[self.KEY_LOSSES]))
        hashed_text = hashlib.sha256(win_lose_list.encode()).hexdigest()
        ord_of_hash = 0
        for caracter in hashed_text:
            ord_of_hash += ord(caracter)
        return liste[ord_of_hash % len(liste)]

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
            # Creating list of couples in a single duel -> list(tuple):
            duel_items = list(duel.items())
            # Initializing the score differences list
            if duel_items[0][1] < duel_items[1][1]:
                defeatscores[duel_items[0][0]].append(abs(duel_items[0][1] - duel_items[1][1]))
            elif duel_items[0][1] > duel_items[1][1]:
                defeatscores[duel_items[1][0]].append(abs(duel_items[0][1] - duel_items[1][1]))
            else:
                defeatscores[duel_items[1][0]].append(0)
                defeatscores[duel_items[0][0]].append(0)

        maxdefeat = dict()

        for label, listscore in defeatscores.items():
            maxdefeat[label] = max(listscore)

        return self.__find_winners(maxdefeat, reverse=False)
