import unittest
from voter import Voter


class TestVoter(unittest.TestCase):
    def setUp(self) -> None:
        self.label = "1"
        self.coordinates = (0.2, 0.2)
        self.voter1 = Voter(self.label, self.coordinates)
        self.voter2 = Voter("2", (0.4, 0.4))

    def test_voter_attributes(self):
        self.assertEqual(self.voter1.get_label(), self.label)
        self.assertEqual(self.voter1.coordinates(), self.coordinates)

        self.voter1.set_label("2")
        self.assertEqual(self.voter1.get_label(), self.voter2.get_label())
        self.assertNotEqual(self.voter1.coordinates(), self.voter2.coordinates())

    def tearDown(self):
        return
