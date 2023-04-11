import csv
import time
import os

from typing import Callable

from candidate import Candidate
from voter import Voter


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

    __separator = ','

    def __init__(self, separator=__separator):
        self.__separator = separator

    def create_error_message(self, line: int, line_format: bool) -> str:
        """
        Creates the message string to be displayed on error.
        If line_format is True, the format of the line is incorrect.
        If False, the coordinates given in that line are not in the correct interval.

        :param line: the number of the line that contains the error
        :param line_format: if True, the error is in the format, else in the coordinates
        :return: the message to be displayed on error
        """
        if line_format:
            return "Le format de la ligne " + str(line) + " est invalide."
        return "Les coordonnées à la ligne " + str(line) + " sont invalides."

    def import_objects_from_file(
            self,
            filename: str | None,
            on_error: Callable[[str, str], None],
            on_success: Callable[[list, list], None]
    ) -> int:
        """
        Imports the coordinates of candidates and/or voters from file and plots them on the graph.

        :param filename: name of the file to import from
        :param on_error: error callback
        :param on_success: success callback
        :return 0 if file is imported, -1 if any error is generated
        """
        error_title = "Erreur de lecture"

        candidates = []
        voters = []
        object = ""

        f = open(filename, "r")
        for i, line in enumerate(csv.reader(f), start=1):
            nb_inputs = len(line)
            if nb_inputs > 4:
                on_error(error_title, self.create_error_message(i, True))
                return -1
            if nb_inputs == 0:
                continue
            if nb_inputs == 1:
                if line[0] == "Votants" or line[0] == "Candidats":
                    object = line[0]
                else:
                    on_error(error_title, self.create_error_message(i, True))
                    return -1
            if nb_inputs >= 2:
                try:
                    x = float(line[0])
                    y = float(line[1])
                    if x < -1 or x > 1 or y < -1 or y > 1:
                        raise ValueError()
                except ValueError:
                    on_error(error_title, self.create_error_message(i, False))
                    return -1

                if nb_inputs == 3 or nb_inputs == 4:
                    if object == "Candidats":
                        label = line[2]
                        if label == "":
                            on_error(error_title, "Le nom du candidat ne peut pas être vide.")
                            return -1
                        try:
                            color = line[3]
                        except IndexError:
                            color = Candidate.random_color(label, (x, y)).get_color()
                    else:
                        on_error(error_title, self.create_error_message(i, True))
                        return -1
                else:
                    label = None
                    color = None

                if object == "Candidats":
                    candidates.append((x, y, label, color))
                elif object == "Votants":
                    voters.append((x, y))
                else:
                    on_error(error_title, self.create_error_message(i, True))
                    return -1
        f.close()
        on_success(voters, candidates)
        return 0

    def export_objects_to_file(
            self,
            candidates: list[Candidate],
            voters: list[Voter],
            on_error: Callable[[str, str], None],
            on_success: Callable[[str, str], None]
    ) -> int:
        """
        Creates a new file and writes the coordinates of the candidates and/or voters present on the graph in it.
        The file is created in the directory 'files'.

        :param candidates: the list of candidates
        :param voters: the list of voters
        :param on_error: error callback
        :param on_success: success callback
        :return 0 if file is exported, -1 if any error is generated
        """
        if candidates == [] and voters == []:
            on_error("Erreur de sauvegarde", "Il n'y a ni candidats ni votants sur le graphe.")
            return -1

        filename = "donnees-" + time.strftime("%d%m%Y-%H%M%S") + ".csv"
        if not os.path.isdir("./files/"):
            os.mkdir("./files/")
        file = open("./files/" + filename, "w")

        if candidates:
            file.write("Candidats\n")
            for candidate in candidates:
                x, y = candidate.coordinates()
                output = [str(x), str(y), candidate.get_label(), candidate.get_color()]
                file.write(self.__separator.join(output) + "\n")

        if voters:
            if candidates:
                file.write("\n")
            file.write("Votants\n")
            for voter in voters:
                x, y = voter.coordinates()
                output = [str(x), str(y)]
                file.write(self.__separator.join(output) + "\n")

        file.close()

        on_success("Sauvegarde réussie", "Le fichier " + filename + " a été créé dans le répertoire 'files'.")

        return 0
