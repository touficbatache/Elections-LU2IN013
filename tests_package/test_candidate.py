import unittest
from candidate import Candidate


class TestCandidate(unittest.TestCase):
    def setUp(self) -> None:
        self.label = "A"
        self.coordinates = (0.2, 0.2)
        self.candidate = Candidate.random_color(self.label, self.coordinates)

    def test_candidate_attributes(self):
        self.assertEqual(self.candidate.get_label(), self.label)
        self.assertEqual(self.candidate.coordinates(), self.coordinates)

        self.candidate.set_color("xkcd:purple")
        self.candidate.set_label("B")

        self.assertEqual(self.candidate.get_color(), "xkcd:purple")
        self.assertEqual(self.candidate.get_label(), "B")

    def tearDown(self):
        return
