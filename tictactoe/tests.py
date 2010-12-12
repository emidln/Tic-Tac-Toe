from django.test import TestCase
from models import Board
from exceptions import GameWin, GameDraw, IllegalMove, UndefinedMove

class BoardTests(TestCase):

    def move_normal(self):
        b = Board()
        self.assertRaises(GameWin, b.move, 4, 1)
        self.assertRaises(GameWin, b.move, 0, 2)
 
    def move_win(self):
        b = Board()
        b.square_l = '110000000'
        b.save()
        self.assertRaises(GameWin, b.move, 2, 1)
        
    def move_draw(self):
        b = Board() 
        b.square_l = '121212220'
        b.save()
        self.assertRaises(GameDraw, b.move, 8, 1)

    def move_illegal(self):
        b = Board()
        b[0] = 1 
        b.save()
        self.assertRaises(IllegalMove, b.move, 0, 1)
    
    def move_undefined(self):
        b = Board()
        self.assertRaises(UndefinedMove, b.move, 9, 1)
        self.assertRaises(UndefinedMove, b.move, -10, 1)
    
        
