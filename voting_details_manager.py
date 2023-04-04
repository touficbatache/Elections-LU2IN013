import tkinter as tk
from tkinter import ttk, Toplevel
from data_manager import DataManager
from keyboard_manager import KeyboardManager

top_step = None
top_step_condorcet = None
top_step_elimination = None

top_details = None


class VotingDetails:
    # Data list for Condorcet
    condorcet_details = []

    # Data list for STV
    elimination_successive_details = []

    # Data list for Veto, Borda, Approbation, and Simple plurality.
    remaining_methods_details = []

    # List of candidates from data manager
    __data_manager = DataManager()
    __candidates = __data_manager.get_candidates()

    # Create a Keyboard Manager
    keyboard_manager = KeyboardManager()

    def set_condorcet_details(self, value: list):
        """
        Sets the value of condorcet_details.

        :param value: The value to affect
        """
        self.condorcet_details = value

    def set_elimination_successive_details(self, value: list):
        """
        Sets the value of elimination_successive_details.

        :param value: The value to affect
        """
        self.elimination_successive_details = value

    def set_remaining_methods_details(self, value: list):
        """
        Sets the value of remaining_methods_details.
        This functions initializes the data list for the Veto, Borda, Approbation,
        and Simple plurality voting methods.

        :param value: The value to affect
        """
        self.remaining_methods_details = value

    def __create_scrollbar(self, frame: Toplevel):
        """
        Creates a scrollbar frame to store the details in.

        :param frame: The frame in which scrollbar should be created
        :return: the scrollable frame created
        """
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

    def show_elimination_successive_information(self, frame: Toplevel):
        """
        Gives a definition of STV voting system.

        :param frame: The frame used to show the details of the voting method
        """
        global top_details
        if top_details:
            top_details.destroy()

        top_details = tk.Toplevel(frame)
        top_details.title("Elimination Successive - Définition")

        tk.Label(top_details, text="Description du mode de vote :", font=("Mistral", "15", "bold")).grid(row=0,
                                                                                                         column=0)
        tk.Label(top_details,
                 text="Le vote par Elimination succéssive est un vote itératif. S'il existe un "
                      "candidat classé premier par une majorité de votants alors il est élu "
                      "directement gagnant. Sinon, le candidat classé premier par le moins de votants "
                      "est  éliminé de tous les votes. Les votes de ce candidat sont transférés au meilleur "
                      "candidat restant. Cette condition est répétée jusqu'à ce qu'un candidat est classé "
                      "premier par une majorité de votants.",
                 wraplength=250).grid(row=1, column=0)

        self.keyboard_manager.esc_bind(top_details)

    def show_approbation_information(self, approval_radius: int, frame: Toplevel):
        """
        Gives a definition of Approbation voting system.

        :param approval_radius: Radius of the approval circle
        :param frame: The frame used to show the details of the voting method
        """
        global top_details
        if top_details:
            top_details.destroy()

        top_details = tk.Toplevel(frame)
        top_details.title("Approbation - Définition")

        tk.Label(top_details, text="Description du mode de vote :", font=("Mistral", "15", "bold")).grid(row=0,
                                                                                                         column=0)
        tk.Label(top_details,
                 text="Le vote par approbation est un vote similaire à une situation de Oui ou Non. Les candidats présents "
                      "dans la zone d'approbation du votant (dans ce cas : " + str(
                     approval_radius) + "% de la distance maximale) "
                                        "reçoivent un (1) point de la part du votant. Les candidats en dehors de cette zone reçoivent par conséquent "
                                        "un score de zéro. Les scores des différents votants sont ensuite ajoutés pour déterminer le vainqueur. "
                                        "Le candidat ayant le score le plus élevé gagne les éléctions. En cas d'égalité, le gagnant est départagé "
                                        "par ordre lexicographique croissant (A -> Z). Si tous les candidats se trouvent hors des zones "
                                        "d'approbation, aucun candidat gagne.",
                 wraplength=250).grid(row=1, column=0)

        self.keyboard_manager.esc_bind(top_details)

    def show_pluralite_simple_information(self, frame: Toplevel):
        """
        Gives a definition of simple plurality voting system.

        :param frame: The frame used to show the details of the voting method
        """
        global top_details
        if top_details:
            top_details.destroy()

        top_details = tk.Toplevel(frame)
        top_details.title("Pluralité Simple - Définition")

        tk.Label(top_details, text="Description du mode de vote :", font=("Mistral", "15", "bold")).grid(row=0,
                                                                                                         column=0)
        tk.Label(top_details,
                 text="Le vote par pluralité simple est un vote qui prend en compte le premier vote de chaque votant. "
                      "Le candidat le mieux classé gagne un (1) point dans chaque profil de vote et son scores est la somme de tous ses points gagnés. "
                      "Le candidat ayant le score le plus élevé gagne les éléctions. En cas d'égalité, le gagnant est départagé "
                      "par ordre lexicographique croissant (A -> Z).",
                 wraplength=250).grid(row=1, column=0)

        self.keyboard_manager.esc_bind(top_details)

    def show_borda_information(self, maximum: int, step: int, frame: Toplevel):
        """
        Gives a definition of Borda voting system.

        :param step: Step between two scores (ex: if max=100 and step=5, score attribution: 100, 95, 90, ...)
        :param maximum: maximum score to attribute to the top candidate
        :param frame: Frame from which vote method details details popup should generate
        :param maximum: Maximum score to attribute to the top candidate
        :param frame: The frame used to show the details of the voting method
        """
        global top_details
        if top_details:
            top_details.destroy()

        top_details = tk.Toplevel(frame)
        top_details.title("Borda - Définition")

        tk.Label(top_details, text="Description du mode de vote :", font=("Mistral", "15", "bold")).grid(row=0,
                                                                                                         column=0)
        tk.Label(top_details,
                 text="La méthode de Borda est un vote qui attribut à chaque candidat un score dans chaque profil de vote. "
                      "Le candidat le mieux classé gagne un nombre maximum de points (dans ce cas : " + str(
                     maximum) + "). "
                                "Le candidat suivant reçoit un score inférieur au premier en supprimant " + str(
                     step) + " point(s) du score du précédent. "
                             "Les scores sont calculés simultanément. Si le nombre de candidats est supérieur au nombre de scores à attribuer, "
                             "les candidats restants obtiennent le score de zéro (0). Suite à l'ajout des différents scores, le candidat ayant le score "
                             "le plus élevé gagne les éléctions. En cas d'égalité, le gagnant est départagé par ordre lexicographique croissant (A -> Z).",
                 wraplength=250).grid(row=1, column=0)

        self.keyboard_manager.esc_bind(top_details)

    def show_veto_information(self, frame: Toplevel):
        """
        Gives a definition of Veto voting system.

        :param frame: The frame used to show the details of the voting method
        """
        global top_details
        if top_details:
            top_details.destroy()

        top_details = tk.Toplevel(frame)
        top_details.title("Veto - Définition")

        tk.Label(top_details, text="Description du mode de vote :", font=("Mistral", "15", "bold")).grid(row=0,
                                                                                                         column=0)
        tk.Label(top_details,
                 text="La méthode de Veto est un vote qui attribut à chaque candidat dans un profil de vote un "
                      "(1) point. Par contre, le candidat le plus mal classé obtient le score de zéro (0). Les scores des "
                      "différents profils sont ajoutés pour pouvoir déterminer qui est le gagnant. Le candidat ayant le score le plus "
                      "élevé gagne les éléctions. En cas d'égalité, le gagnant est départagé par ordre lexicographique croissant (A -> Z).",
                 wraplength=250).grid(row=1, column=0)

        self.keyboard_manager.esc_bind(top_details)

    def show_condorcet_information(self, method, tie_breaking_rule, frame: Toplevel):
        """
        Gives a definition of condorcet voting system.

        :param method: Method to use in case there is no Condorcet winner
        :param tie_breaking_rule: Tie-breaking rule to use to decide who wins
        :param frame: The frame used to show the details of the voting method
        """
        global top_details
        if top_details:
            top_details.destroy()

        top_details = tk.Toplevel(frame)
        top_details.title("Condorcet - Définition")

        tk.Label(top_details, text="Description du mode de vote :", font=("Mistral", "15", "bold")).grid(row=0,
                                                                                                         column=0)
        tk.Label(top_details,
                 text="Le vote par Condorcet revient à simuler l'ensemble des duels possibles parmi les "
                      "différents candidats: pour chaque paire de candidats, on détermine le nombre de votants "
                      "ayant voté pour l'un ou l'autre en vérifiant, sur chaque profil de vote, comment l'un a "
                      "été classé par rapport à l'autre. Ainsi pour chaque duel, il y a un candidat vainqueur. "
                      "S'il y a un unique candidat qui remporte tous ses duels : il s'agit du vainqueur de Condorcet.",
                 wraplength=250).grid(row=1, column=0)
        method_str = method.__str__()
        tie_breaking_rule_str = tie_breaking_rule.__str__()
        match method_str, tie_breaking_rule_str:
            case "CondorcetMethod.COPELAND", "CondorcetTieBreakingRule.RANDOM":
                tk.Label(top_details,
                         text="Si aucun candidat ne remporte tous ses duels, on peut avoir recours à différentes méthodes. Dans "
                              "ce cas, on utilise la méthode de Copeland qui cherche le candidat qui a gagné le plus de "
                              "confrontations. Ce candidat serait donc le vainqueur. Par contre, s'il existe "
                              "des conflits, le candidat vainqueur est choisi au hasard parmi les différents candidats vérifiant "
                              "la méthode de Simpson, suivant des probabilités particulières optimales.",
                         wraplength=250).grid(row=2, column=0)
            case "CondorcetMethod.COPELAND", "CondorcetTieBreakingRule.ORDRE_LEXICO":
                tk.Label(top_details,
                         text="Si aucun candidat ne remporte tous ses duels, on peut avoir recours à différentes méthodes. Dans "
                              "ce cas, on utilise la méthode de Copeland qui cherche le candidat qui a gagné le plus de "
                              "confrontations. Ce candidat serait donc le vainqueur. Par contre, s'il existe des conflits, "
                              "le candidat vainqueur est choisi par ordre lexicographique parmi les différents candidats "
                              "vérifiant la méthode de Copeland.",
                         wraplength=250).grid(row=2, column=0)
            case "CondorcetMethod.SIMPSON", "CondorcetTieBreakingRule.RANDOM":
                tk.Label(top_details,
                         text="Si aucun candidat ne remporte tous ses duels, on peut avoir recours à différentes méthodes. Dans "
                              "ce cas, on utilise la méthode de de Simpson (minimax) qui choisit le candidat dont la défaite "
                              "max en duel est la plus faible. Ce candidat serait donc le vainqueur. Par contre, s'il existe "
                              "des conflits, le candidat vainqueur est choisi au hasard parmi les différents candidats vérifiant "
                              "la méthode de Simpson, suivant des probabilités particulières optimales.",
                         wraplength=250).grid(row=2, column=0)
            case "CondorcetMethod.SIMPSON", "CondorcetTieBreakingRule.ORDRE_LEXICO":
                tk.Label(top_details,
                         text="Si aucun candidat ne remporte tous ses duels, on peut avoir recours à différentes méthodes. Dans "
                              "ce cas, on utilise la méthode de de Simpson (minimax) qui choisit le candidat dont la défaite "
                              "max en duel est la plus faible. Ce candidat serait donc le vainqueur. Par contre, s'il existe "
                              "des conflits, le candidat vainqueur est choisi par ordre lexicographique parmi les différents "
                              "candidats vérifiant la méthode de Simpson.",
                         wraplength=250).grid(row=2, column=0)

        self.keyboard_manager.esc_bind(top_details)

    def show_remaining_methods_details(self, frame: Toplevel):
        """
        Displays score details for Veto, Borda, Approbation and Simple plurality.

        :param frame: Frame to build popup on
        """
        global top_step
        if top_step:
            top_step.destroy()

        # Generate TopLevel popup for scores details
        top_step = tk.Toplevel(frame)
        top_step.title("Résultat détaillé")

        nb_candidates = len(self.__candidates)

        tk.Label(top_step, text="Les scores des votes :", font=("Mistral", "15", "bold")).grid(row=0,
                                                                                               columnspan=nb_candidates if nb_candidates < 12 else 12,
                                                                                               column=0)

        added_candidates = []

        row_upgrade = 1
        for candidate_label in self.remaining_methods_details[1].keys():
            tk.Label(top_step,
                     text=candidate_label + " : " + str(self.remaining_methods_details[1][candidate_label])).grid(
                row=row_upgrade, column=0)
            added_candidates.append(candidate_label)
            row_upgrade += 1

        for candidate in self.__candidates:
            candidate_label = candidate.get_label()
            if candidate_label not in added_candidates:
                tk.Label(top_step, text=candidate_label + " : 0").grid(row=row_upgrade, column=0)
            row_upgrade += 1


        row_upgrade += 1

        if self.remaining_methods_details[0] is not None:
            if not self.remaining_methods_details[0][1]:
                tk.Label(top_step, text="Le gagnant est : " + self.remaining_methods_details[0][0],
                         font=("Mistral", "15", "bold")).grid(row=row_upgrade,
                                                              columnspan=nb_candidates if nb_candidates < 12 else 12,
                                                              column=0)
            else:
                tk.Label(top_step, text="Le gagnant a été départagé :", font=("Mistral", "15", "bold")).grid(
                    row=row_upgrade, columnspan=nb_candidates if nb_candidates < 12 else 12, column=0)
                tk.Label(top_step, text=self.remaining_methods_details[0][0] + " a gagné parmi " + str(
                    self.remaining_methods_details[0][2])).grid(row=row_upgrade + 1,
                                                                columnspan=nb_candidates if nb_candidates < 12 else 12,
                                                                column=0)
        else:
            tk.Label(top_step, text="Aucun gagnant trouvé", font=("Mistral", "15", "bold")).grid(row=row_upgrade,
                                                                                                 columnspan=nb_candidates if nb_candidates < 12 else 12,
                                                                                                 column=0)
            tk.Label(top_step, text="Avec les données fournis, aucun gagnant peut être déterminé.",
                     wraplength=nb_candidates * 30 if nb_candidates < 12 else 360).grid(row=row_upgrade + 1,
                                                                                        columnspan=nb_candidates if nb_candidates < 12 else 12,
                                                                                        column=0)

        self.keyboard_manager.esc_bind(top_step)

    def show_condorcet_steps(self, frame: Toplevel):
        """
        Displays score details for Condorcet.

        :param frame: Frame to build popup on
        """
        global top_step_condorcet
        if top_step_condorcet:
            top_step_condorcet.destroy()

        top_step_condorcet = tk.Toplevel(frame)
        top_step_condorcet.title("Condorcet - Résultat détaillé")

        self.keyboard_manager.esc_bind(top_step_condorcet)

        nb_candidates = len(self.condorcet_details[5])

        scrollable_frame = self.__create_scrollbar(top_step_condorcet)

        if nb_candidates == 1:
            ttk.Label(scrollable_frame, text="Il n'y a qu'un unique candidat.").grid(row=0, column=0)
            ttk.Label(scrollable_frame, text="Le gagnant est : " + self.condorcet_details[5][0],
                      font=("Mistral", "15", "bold")).grid(row=1, column=0)
            return
        else:
            ttk.Label(scrollable_frame, text="Les duels", font=("Mistral", "15", "bold")).grid(row=0, column=0)
            row_manager = 1
            for duel in self.condorcet_details[1]:
                candidates = list(duel.keys())
                ttk.Label(scrollable_frame, text="Duel entre " + candidates[0] + " et " + candidates[1] +
                                                 " : " + candidates[0] + " (" + str(duel[candidates[0]]) +
                                                 ") " + candidates[1] + " (" + str(duel[candidates[1]]) +
                                                 ") ").grid(row=row_manager, column=0)
                row_manager += 1
            ttk.Label(scrollable_frame, text=" ").grid(row=row_manager, column=0)
            row_manager += 1

            ttk.Label(scrollable_frame, text="Les résultats des duels", font=("Mistral", "15", "bold")).grid(
                row=row_manager, column=0)
            row_manager += 1
            for candidate_label, results in sorted(self.condorcet_details[2].items()):
                ttk.Label(scrollable_frame, text=candidate_label + " gain : " + str(len(results["wins"])) +
                                                 ", perte : " + str(len(results["losses"])) +
                                                 " et nul : " + str(len(results["draws"]))
                          ).grid(row=row_manager, column=0)
                row_manager += 1
            ttk.Label(scrollable_frame, text=" ").grid(row=row_manager, column=0)
            row_manager += 1

            if not self.condorcet_details[0] and not self.condorcet_details[0]:
                ttk.Label(scrollable_frame, text="Le gagnant de condorcet est : ", font=("Mistral", "15", "bold")).grid(
                    row=row_manager, column=0)
                ttk.Label(scrollable_frame, text=self.condorcet_details[0][0], font=("Mistral", "15", "bold")).grid(
                    row=row_manager + 1, column=0)
            else:
                ttk.Label(scrollable_frame, text="Pas de gagnant de condorcet", font=("Mistral", "15", "bold")).grid(
                    row=row_manager, column=0)
                ttk.Label(scrollable_frame,
                          text="On utilise la méthode de " + str.lower(self.condorcet_details[3].name)).grid(
                    row=row_manager + 1, column=0)
                row_manager += 2

                ttk.Label(scrollable_frame, text=" ").grid(row=row_manager, column=0)
                row_manager += 1

                if self.condorcet_details[0][3] is None:
                    ttk.Label(scrollable_frame, text="Le gagnant est : ", font=("Mistral", "15", "bold")).grid(
                        row=row_manager, column=0)
                    ttk.Label(scrollable_frame, text=self.condorcet_details[0][0], font=("Mistral", "15", "bold")).grid(
                        row=row_manager + 1, column=0)
                else:
                    self.condorcet_details[6].append(self.condorcet_details[0][0])
                    ttk.Label(scrollable_frame, text="Plusieurs gagnants : " + str(sorted(self.condorcet_details[6])),
                              font=("Mistral", "15", "bold"), wraplength=300).grid(row=row_manager, column=0)
                    ttk.Label(scrollable_frame, text="On a recours a la méthode de " + str.lower(
                        self.condorcet_details[4].name) + " pour départager entre les différents candidats gagnants",
                              wraplength=300).grid(row=row_manager + 1, column=0)
                    row_manager += 2
                    ttk.Label(scrollable_frame, text=" ").grid(row=row_manager, column=0)
                    row_manager += 1

                    ttk.Label(scrollable_frame, text="Le gagnant est : ", font=("Mistral", "15", "bold")).grid(
                        row=row_manager, column=0)
                    ttk.Label(scrollable_frame, text=self.condorcet_details[0][0], font=("Mistral", "15", "bold")).grid(
                        row=row_manager + 1, column=0)
            return

    def show_elimination_successive_steps(self, frame: Toplevel):
        """
        Displays score details for STV.

        :param frame: Frame to build popup on
        """
        global top_step_elimination
        if top_step_elimination:
            top_step_elimination.destroy()

        # Generate TopLevel popup for scores details
        top_step_elimination = tk.Toplevel(frame)
        top_step_elimination.title("Elimination succéssive - Résultat détaillé")
        # Get number of candidates
        nb_candidates = len(self.__candidates)
        # Grid row manager for the frame labels grid position
        grid_row_manager = 0

        scrollable_frame = self.__create_scrollbar(top_step_elimination)

        self.keyboard_manager.esc_bind(top_step_elimination)

        row_uprade = -1
        for round_number, scores_letter in self.elimination_successive_details[0].items():
            scores = scores_letter[0]
            letter = scores_letter[1]
            ttk.Label(scrollable_frame, text="Score du tour #" + str(round_number) + " :",
                      font=("Mistral", "15", "bold")).grid(row=grid_row_manager, column=0,
                                                           columnspan=nb_candidates if nb_candidates < 12 else 12)

            i = 0
            for candidate in self.__candidates:
                candidate_label = candidate.get_label()
                if i % 12 == 0:
                    row_uprade += 1
                    i = 0
                if candidate_label in scores.keys():
                    ttk.Label(scrollable_frame, text=candidate_label + " : " + str(scores[candidate_label])).grid(
                        row=grid_row_manager + row_uprade + 1, column=i)
                else:
                    ttk.Label(scrollable_frame, text=candidate_label + " : 0").grid(
                        row=grid_row_manager + row_uprade + 1, column=i)
                i += 1
            grid_row_manager += 2 + row_uprade

            if letter != "":
                ttk.Label(scrollable_frame, text="Pas de gagnant par majorité dans ce tour.",
                          wraplength=250).grid(row=grid_row_manager,
                                               columnspan=nb_candidates if nb_candidates < 12 else 12, column=0)
                grid_row_manager += 1

                ttk.Label(scrollable_frame,
                          text="Candidat éliminé au tour #" + str(round_number) + " : " + letter).grid(
                    row=grid_row_manager, columnspan=nb_candidates if nb_candidates < 12 else 12, column=0)
                ttk.Label(scrollable_frame, text=" ").grid(row=grid_row_manager + 1, column=0,
                                                           columnspan=nb_candidates if nb_candidates < 12 else 12)
                grid_row_manager += 2

        ttk.Label(scrollable_frame,
                  text="Gagnant par majorité (>" + str(self.elimination_successive_details[1]) + ") : " +
                       self.elimination_successive_details[2][0], font=("Mistral", "13", "bold")).grid(
            row=grid_row_manager, column=0, columnspan=nb_candidates if nb_candidates < 12 else 12)
