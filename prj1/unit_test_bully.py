import unittest as unit
import bully_election 

class Testing(unit.TestCase):
    def test_Message(self):
        uut = bully_election.Message(42,bully_election.Type.OK)
        self.assertEqual(uut.sender, 42)
        self.assertEqual(uut.type,bully_election.Type.OK)

if __name__ == '__main__':
    unit.main()

