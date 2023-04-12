import unittest
from voter import Voter


class TestVoter(unittest.TestCase):
    def setUp(self) -> None:
        self.label = "1"
        self.coordinates = (0.2, 0.2)
        self.voter = Voter(self.label, self.coordinates)

    def test_voter_attributes(self):
        self.assertEqual(self.voter.get_label(), self.label)
        self.assertEqual(self.voter.coordinates(), self.coordinates)

        self.voter.set_label("2")
        self.assertEqual(self.voter.get_label(), "2")
        self.assertNotEqual(self.voter.get_label(), "1")

    def tearDown(self):
        return
