from django.test import TestCase
from models import Board
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
    
        
