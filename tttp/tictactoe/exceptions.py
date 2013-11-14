""" Application-specific exceptions for TicTacToe.

IllegalMove, UndefinedMove, GameDraw, and GameWin are passed to the view
layer to signal events that have occurred deep within the logic engine.

"""
from .utils import COMPUTER


class TTTBaseException(Exception):

    """ Base exception for TicTacToe app. """

    def __str__(self):
        return str(unicode(self))

    def __repr__(self):
        return str(self)


class IllegalMove(TTTBaseException):

    """ IllegalMove was attempted. """

    def __init__(self, move, player):
        super(IllegalMove, self).__init__()
        self.move = move
        self.player = player

    def __unicode__(self):
        return "Illegal Move at %d attempted by %s" % (self.move, self.player)


class UndefinedMove(TTTBaseException):

    """ UndefinedMove was attempted. """

    def __init__(self, move, player):
        super(UndefinedMove, self).__init__()
        self.move = move
        self.player = player

    def __unicode__(self):
        return "Undefined Move at %d attempted by %s" % (self.move, self.player)


class GameDraw(TTTBaseException):

    """ A GameDraw has occurred. """

    def __unicode__(self):
        return "GAME OVER -- DRAW"


class GameWin(TTTBaseException):

    """ A GameWin has occurred. """

    def __init__(self, player):
        super(GameWin, self).__init__()
        self.player = player

    def __unicode__(self):
        if self.player == COMPUTER:
            return "You have lost the Game!"
        else:
            return "You have won the Game!"
