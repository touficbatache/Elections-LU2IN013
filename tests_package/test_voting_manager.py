import unittest

import voting_manager
from voting_manager import VotingManager


class TestVotingManager(unittest.TestCase):
    def setUp(self) -> None:
        self.voting_manager = VotingManager()
        self.candidates = ["A", "B", "C", "D", "E"]
        self.voters = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.voting_profils = {
            "1": ([("D", 0.70), ("A", 0.68), ("E", 0.60), ("C", 0.59), ("B", 0.57)], 1),
            "2": ([("D", 0.65), ("A", 0.53), ("E", 0.48), ("C", 0.45), ("B", 0.43)], 1),
            "3": ([("D", 0.79), ("C", 0.46), ("A", 0.44), ("B", 0.42), ("E", 0.34)], 1),
            "4": ([("C", 0.98), ("B", 0.96), ("A", 0.73), ("D", 0.61), ("E", 0.56)], 1),
            "5": ([("A", 0.85), ("C", 0.74), ("B", 0.73), ("E", 0.72), ("D", 0.64)], 1),
            "6": ([("E", 0.93), ("A", 0.78), ("B", 0.53), ("C", 0.50), ("D", 0.36)], 1),
            "7": ([("D", 0.75), ("C", 0.41), ("B", 0.36), ("A", 0.26), ("E", 0.12)], 1),
            "8": ([("A", 0.89), ("E", 0.77), ("B", 0.72), ("C", 0.71), ("D", 0.59)], 1),
            "9": ([("D", 0.89), ("C", 0.53), ("B", 0.48), ("A", 0.44), ("E", 0.32)], 1),
            "10": ([("D", 0.85), ("C", 0.51), ("B", 0.47), ("A", 0.46), ("E", 0.35)], 1)
        }

        self.voting_profils_condorcet = {
            "1": ([("A", 0.70), ("B", 0.68), ("C", 0.60)], 1),
            "2": ([("B", 0.65), ("C", 0.53), ("A", 0.48)], 1),
            "3": ([("C", 0.79), ("A", 0.46), ("B", 0.44)], 1)
        }

    def test_pluralite_simple(self):
        self.assertEqual(
            self.voting_manager.pluralite_simple(self.voting_profils)[0], "D"
        )
        self.assertEqual(
            self.voting_manager.pluralite_simple(self.voting_profils)[1], False
        )
        self.assertEqual(
            self.voting_manager.pluralite_simple(self.voting_profils)[2], ["D"]
        )

    def test_veto(self):
        self.assertEqual(self.voting_manager.veto(self.voting_profils)[0], "A")
        self.assertEqual(self.voting_manager.veto(self.voting_profils)[1], True)
        self.assertEqual(self.voting_manager.veto(self.voting_profils)[2], ["A", "C"])

    def test_borda(self):
        self.assertEqual(
            self.voting_manager.borda(self.voting_profils, len(self.candidates), 1),
            ('D', False, ['D']),
        )

    def test_approbation(self):
        self.assertEqual(
            self.voting_manager.approbation(
                self.voting_profils, 10
            ),
            ('B', True, ['C', 'B', 'E']),
        )

        self.assertEqual(
            self.voting_manager.approbation(
                self.voting_profils, 25
            ),
            ('D', False, ['D']),
        )

        self.assertEqual(
            self.voting_manager.approbation(
                self.voting_profils, 90
            ),
            ('A', True, ['D', 'A', 'E', 'C', 'B']),
        )

    def test_elimination_successive(self):
        self.assertEqual(
            self.voting_manager.elimination_successive(self.voting_profils), ('D', False, [])
        )

    def test_condorcet(self):
        self.assertEqual(
            self.voting_manager.condorcet(
                self.voting_profils,
                voting_manager.CondorcetMethod.COPELAND,
                voting_manager.CondorcetTieBreakingRule.RANDOM,
            ),
            ('D', False, False, None),
        )

        self.assertEqual(
            self.voting_manager.condorcet(
                self.voting_profils_condorcet,
                voting_manager.CondorcetMethod.COPELAND,
                voting_manager.CondorcetTieBreakingRule.RANDOM,
            ),
            ('C', True, True, ['A', 'C', 'B']),
        )

        self.assertEqual(
            self.voting_manager.condorcet(
                self.voting_profils_condorcet,
                voting_manager.CondorcetMethod.COPELAND,
                voting_manager.CondorcetTieBreakingRule.ORDRE_LEXICO,
            ),
            ('A', True, True, ['A', 'C', 'B']),
        )

        self.assertEqual(
            self.voting_manager.condorcet(
                self.voting_profils_condorcet,
                voting_manager.CondorcetMethod.SIMPSON,
                voting_manager.CondorcetTieBreakingRule.RANDOM,
            ),
            ('A', True, True, ['B', 'A', 'C']),
        )

        self.assertEqual(
            self.voting_manager.condorcet(
                self.voting_profils_condorcet,
                voting_manager.CondorcetMethod.SIMPSON,
                voting_manager.CondorcetTieBreakingRule.ORDRE_LEXICO,
            ),
            ('A', True, True, ['B', 'A', 'C']),
        )


def tearDown(self):
    return
