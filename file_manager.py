import os.path
import time

import tkinter as tk


class FileManager:
    """
    Class to manage files.

    This class handles the import and export of text files containing the
    coordinates of candidates and/or voters.

    All input and export files must be placed in a directory called 'files'.


    In case of import, the file should follow a certain format shown
    to the user once the import button is pressed. If the file does
    not exist, or if one of its lines does not have a valid format,
    an error is shown and the import fails. If the file has a valid
    format in the totality of its lines, the import is successful
    and the points are shown on the graph.

    In case of export, if there are no points on the graph, a message
    indicating so is shown. If the graph is populated with candidates
    and/or voters, a new file is created with a name following this
    convention : 'donnees-"%d%m%Y-%H%M%S.txt". This assures that no 2
    files have the same name. The file contains the coordinates of the
    points classified under 'Candidats' or 'Votants'. Its format is
    valid.
    """

    def __init__(self, tk_root, graph_manager, add_candidate_on_graph, add_voter_on_graph):
        self.__root = tk_root
        self.__graph_manager = graph_manager
        self.__add_candidate_on_graph = add_candidate_on_graph
        self.__add_voter_on_graph = add_voter_on_graph

    def import_from_file(self):
        """
        Shows popup explaining the format of the file to import.
        Handles user input.
        Calls import_objects_from_file() and gives it the name of a file as input.
        """
        top_main = tk.Toplevel(self.__root)
        top_main.title("Lecture d'un fichier")
        top_main.geometry("600x420")

        label_title = tk.Label(top_main, text="Donner le nom du fichier avec l'extension .txt :")
        label_title.pack()

        file = tk.StringVar()
        entry = tk.Entry(top_main, width=20, textvariable=file)
        entry.pack()

        file_format = tk.Text(top_main, wrap=tk.WORD, bg='#ececec')
        file_format.insert(
            tk.INSERT,
            "Le fichier doit avoir le format suivant:\n\n"
            "Candidats\n"
            "-0.589,0.75\n"
            "0.32,0.740\n"
            "-0.483,-0.3904\n"
            "0.2350,-0.34\n"
            "Votants\n"
            "-0.198,0.32\n"
            "0.3548,0.311\n"
            "-0.04879,-0.432\n"
            "0.87826,-0.49\n\n"
    
            "La premiere ligne est soit \"Candidats\" soit \"Votants\".\n"
            "Chaque ligne qui suit contient les coordonnées d'un candidat/votant séparés d'une virgule.\n"
            "Ce format peut être répété dans le fichier autant de fois que possible, avec ou sans des lignes vides après passage d'un objet à un autre.\n\n"
            "Remarque: Les coordonnées sont comprises entre [-1,1]."
        )
        file_format.config(state=tk.DISABLED, height=20)
        file_format.pack()

        label_hint = tk.Label(
            top_main,
            text="Laisser vide pour valeur de défaut (default.txt)"
        )
        label_hint.pack()

        button = tk.Button(
            top_main,
            text="Importer le fichier",
            command=lambda: [self.import_objects_from_file(file), top_main.destroy()]
        )
        button.pack()

    def import_objects_from_file(self, file) -> int:
        """
        Imports the coordinates of candidates and/or voters from file and plots them on the graph.
        If no file is given, the default one is used.

        :param file: name of the file to import from
        """
        if file.get() != "":
            file_name = str(file.get())
        else:
            file_name = "default.txt"

        path = "./files/" + file_name
        if not os.path.exists(path):
            tk.messagebox.showwarning(title='Erreur de lecture', message="Le fichier donné n'existe pas.")
        else:
            list_candidates = []
            list_voters = []

            f = open(path, "r")
            object = f.readline().strip('\n')
            i = 1
            for line in f:
                i += 1
                try:
                    x, y = map(float, line.strip('\n').split(","))
                    if x < -1 or x > 1 or y < -1 or y > 1:
                        tk.messagebox.showwarning(title='Erreur de lecture',
                                                  message="Les coordonnées à la ligne " + str(i) + " sont invalides.")
                        return -1

                    if object == "Candidats":
                        list_candidates.append((x, y))
                    elif object == "Votants":
                        list_voters.append((x, y))
                    else:
                        tk.messagebox.showwarning(title='Erreur de lecture',
                                                  message="Le format de la ligne " + str(i - 1) + " est invalide.")
                        return -1
                except ValueError:
                    object = line.strip('\n')
                    if object != "Candidats" and object != "Votants" and object != "":
                        tk.messagebox.showwarning(title='Erreur de lecture',
                                                  message="Le format de la ligne " + str(i) + " est invalide.")
                        return -1

            f.close()

            for candidate in list_candidates:
                self.__add_candidate_on_graph(candidate)
            for voter in list_voters:
                self.__add_voter_on_graph(voter)

            self.__graph_manager.build()
            return 0

    def export_objects_to_file(self, candidates: list, voters: list) -> int:
        """
        Creates a new file and writes the coordinates of the candidates and/or voters present on the graph in it.
        The file is created in the directory 'files'.
        """
        if candidates == [] and voters == []:
            tk.messagebox.showwarning(title='Erreur de sauvegarde',
                                      message="Il n'y a ni candidats ni votants sur le graphe.")
            return -1
        file_name = "donnees-" + time.strftime("%d%m%Y-%H%M%S") + ".txt"
        file = open("./files/" + file_name, "w")
        if candidates:
            file.write("Candidats\n")
            for candidate in candidates:
                x, y = candidate.coordinates()
                file.write(str(x) + "," + str(y) + "\n")

        if voters:
            if candidates:
                file.write("\n")
            file.write("Votants\n")
            for voter in voters:
                x, y = voter.coordinates()
                file.write(str(x) + "," + str(y) + "\n")

        tk.messagebox.showinfo(title="Sauvegarde réussie",
                               message="Le fichier " + file_name + " a été créé dans le répertoire 'files'.")
        file.close()
        return 0
