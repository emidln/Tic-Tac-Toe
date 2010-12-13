from django.test import TestCase
from models import Board
from logic import evaluate_gamestate as eg
from logic import win, block, corner, first, win_block_corner_first
from utils import COMPUTER, PLAYER
from exceptions import GameWin, GameDraw, IllegalMove, UndefinedMove

class BoardTests(TestCase):

    def test_move_normal(self):
        b = Board()
        self.assertEqual(b.move(4, 1), None)
        self.assertEqual(b.move(0, 2), None)
 
    def test_move_win(self):
        b = Board()
        b.squares_l = '110000000'
        b.save()
        self.assertEqual(b[:],[1,1,0,0,0,0,0,0,0]) 
        self.assertRaises(GameWin, b.move, 2, 1)
        
    def test_move_draw(self):
        b = Board() 
        b.squares_l = '121221110'
        b.save()
        self.assertRaises(GameDraw, b.move, 8, 2)

    def test_move_illegal(self):
        b = Board()
        b[0] = 1 
        b.save()
        self.assertRaises(IllegalMove, b.move, 0, 1)
    
    def test_move_undefined(self):
        b = Board()
        b.save()
        self.assertRaises(UndefinedMove, b.move, 9, 1)
        self.assertRaises(UndefinedMove, b.move, -10, 1)
    
class LogicTests(TestCase):

    def setUp(self):
        self.b = Board()
        self.b.save()
    
    def reset(self):
        self.b.squares_l = '000000000'
        self.b.save()

    # tests computer on the play (offense)
    def test_move_0(self): 
        self.reset()
        self.assertEqual(eg(self.b), True)  
        self.assertEqual(self.b[4], COMPUTER)

    # tests player on the play (defense)
    def test_move_1(self):
        for x,y in [(0,4),(1,4),(4,0)]:
            self.reset()
            self.b[x] = PLAYER
            self.assertEqual(eg(self.b),True)
            self.assertEqual(self.b[y], COMPUTER)    

    def test_move_2(self):
        self.reset()
        corners = [0,2,6,8]
        sides = [1,3,5,7]
        for x,y in ((4,0),(4,1)):
            self.reset()
            self.b[x] = COMPUTER
            self.assertEqual(eg(self.b), True)
            self.assertEqual(bool([x for x in range(len(self.b)) if self.b[x] == COMPUTER if x != 4 if x in corners]), True)

    def test_move_3(self):
        pass

    def test_win(self):
        self.reset()
        self.b.squares_l = '100012200'
        self.assertRaises(GameWin, win, self.b)
        self.assertEqual(self.b[8], COMPUTER)
        self.reset()
        self.b.squares_l = '100012200'
        self.assertRaises(GameWin, eg, self.b)
        self.assertEqual(self.b[8], COMPUTER)
        
    def test_defend(self):
        pass

    def test_win_before_defend(self):
        pass

    def test_corner(self):
        pass

    def test_any(self):
        pass       
