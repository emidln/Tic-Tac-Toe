""" Test cases for the TicTacToe board and logic engine. """
from django.test import TestCase
from django.test.client import Client
from .models import Board
from .logic import evaluate_gamestate as eg
from .logic import win, block, corner, first, win_block_corner_first
from .utils import COMPUTER, PLAYER
from .exceptions import GameWin, GameDraw, IllegalMove, UndefinedMove

# pep257 claims there must be docstrings for all public definitions.
# I have not provided them for my TestCase methods.

class BoardTests(TestCase):

    """ Board model test cases. """

    def test_move_normal(self):
        b = Board()
        self.assertEqual(b.move(4, 1), None)
        self.assertEqual(b.move(0, 2), None)

    def test_move_win(self):
        b = Board()
        b.squares_l = '110000000'
        b.save()
        self.assertEqual(b[:], [1, 1, 0, 0, 0, 0, 0, 0, 0])
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

    """ Logic engine test cases. """

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
        for x, y in [(0, 4), (1, 4), (4, 0)]:
            self.reset()
            self.b[x] = PLAYER
            self.assertEqual(eg(self.b), True)
            self.assertEqual(self.b[y], COMPUTER)

    def test_move_2(self):
        self.reset()
        corners = [0, 2, 6, 8]
        for x, y in ((4, 0), (4, 1)):
            self.reset()
            self.b[x] = COMPUTER
            self.assertEqual(eg(self.b), True)
            self.assertEqual(bool([x for x in range(len(self.b)) if self.b[x] == COMPUTER if x != 4 if x in corners]), True)

    def test_move_3_opp_center(self):
        def t(f):
            self.reset()
            r = range(9)
            r.pop(4)
            y = r[:]
            for x in r:
                for z in y:
                    if x != z:
                        self.b.squares_l = '000020000'
                        self.b[x] = 1
                        self.b[z] = 2
                        self.assertEqual(eg(self.b), True)
        t(win_block_corner_first)
        t(eg)

    def test_move_3_me_corners_opp(self):
        # opp in opposite corners
        self.reset()
        self.b.squares_l = '200010002'
        self.assertEqual(eg(self.b), True)
        self.assertEqual(self.b[1], COMPUTER)

    def test_move_3_me_corners_not_opp(self):
        # opp in corners not opposite
        self.reset()
        self.b.squares_l = '202010000'
        self.assertEqual(eg(self.b), True)
        self.assertEqual(self.b[1], COMPUTER)

    def test_move_3_me_one_side(self):
        # opp in one side forcing block
        self.reset()
        self.b.squares_l = '220010000'
        self.assertEqual(eg(self.b), True)
        self.assertEqual(self.b[2], COMPUTER)

        # opp doesn't force block
        self.reset()
        self.b.squares_l = '200012000'
        self.assertEqual(eg(self.b), True)
        self.assertEqual(bool([x for x in self.b.taken()
                               if self.b[x] == COMPUTER
                               if x != 4
                               if x in [0, 2, 6, 8]]), True)

    def test_move_3_me_two_sides(self):
        # opp in both sides
        self.reset()
        self.b.squares_l = '020012000'
        self.assertEqual(eg(self.b), True)
        self.assertEqual(self.b[2], COMPUTER)

    def test_move_3_me_two_sides_opp(self):
        # opp in two sides, opposite
        self.reset()
        self.b.squares_l = '020010020'
        self.assertEqual(eg(self.b), True)
        self.assertEqual(bool([x for x in self.b.taken()
                               if self.b[x] == COMPUTER
                               if x != 4
                               if x in [0, 2, 6, 8]]), True)

    def test_win(self):
        def t(f):
            self.reset()
            self.b.squares_l = '100012200'
            self.assertRaises(GameWin, f, self.b)
            self.assertEqual(self.b[8], COMPUTER)
        t(win)
        t(eg)

    def test_block(self):
        def t(f):
            self.reset()
            self.b.squares_l = '200021100'
            self.assertEqual(f(self.b), True)
            self.assertEqual(self.b[8], COMPUTER)
        t(block)
        t(eg)

    def test_win_before_defend(self):
        self.reset()
        self.b.squares_l = '220110000'
        self.assertRaises(GameWin, eg, self.b)
        self.assertEqual(self.b[5], COMPUTER)

    def test_corner(self):
        def t(f):
            self.reset()
            self.b.squares_l = '100020002'
            self.assertEqual(f(self.b), True)
            self.assertEqual(len([x for x in self.b.taken()
                                  if self.b[x] == COMPUTER
                                  if x in [0, 2, 6, 8]]), 2)
        t(corner)
        t(eg)

    def test_first(self):
        def t(f):
            self.reset()
            self.b.squares_l = '212010122'
            t = self.b.taken()
            self.assertEqual(f(self.b), True)
            self.assertEqual(set(self.b.taken()).difference(t).pop() in [3, 5], True)
        t(first)
        t(eg)


# the tests for the web page themselves are incomplete
# we need to see that the xml file generated has the appropriate fields, but we don't
# further, we need to verify that the messages shown in the appropriate fields are in
# fact correct the only things tested here are response codes. Manual validation has
# shown that the code is correct, but that isn't always likely to be good enough.
class WebTests(TestCase):

    """ Web Client test cases. """

    def setUp(self):
        self.client = Client()

    def test_page_redirect(self):
        self.assertEqual(self.client.get('/tictactoe/').status_code, 302)

    def test_page_50(self):
        self.assertEqual(self.client.get('/tictactoe/50/').status_code, 200)

    def test_ajax_as_normal(self):
        self.assertEqual(self.client.get('/tictactoe/50/update/', {'m': 4}).status_code, 404)

    def test_ajax_as_ajax(self):
        self.assertEqual(self.client.get('/tictactoe/50/update/', {'m': 4}, HTTP_X_REQUESTED_WITH='XMLHttpRequest').status_code, 200)

    def test_ajax_as_ajax_no_m(self):
        self.assertEqual(self.client.get('/tictactoe/50/update/', HTTP_X_REQUESTED_WITH='XMLHttpRequest').status_code, 404)
