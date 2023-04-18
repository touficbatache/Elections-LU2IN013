import unittest
from candidate import Candidate


class TestCandidate(unittest.TestCase):
    def setUp(self) -> None:
        self.label = "A"
        self.coordinates = (0.2, 0.2)
        self.candidate1 = Candidate.random_color(self.label, self.coordinates)
        self.candidate2 = Candidate("B", (0.4, 0.4), "xkcd:purple")

    def test_candidate_attributes(self):
        self.assertEqual(self.candidate1.get_label(), self.label)
        self.assertEqual(self.candidate1.coordinates(), self.coordinates)

        self.candidate1.set_color("xkcd:purple")
        self.candidate1.set_label("B")

        self.assertEqual(self.candidate1.get_color(), self.candidate2.get_color())
        self.assertEqual(self.candidate1.get_label(), self.candidate2.get_label())

    def tearDown(self):
        return
