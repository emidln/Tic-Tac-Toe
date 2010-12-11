
class TTTBaseException(Exception):
    def __str__(self):
        return str(unicode(self))

    def __repr__(self):
        return str(self)

class IllegalMove(TTTBaseException):
    def __init__(self, move, player):
        self.move = move
        self.player = player

    def __unicode__(self):
        return "Illegal Move at %d attempted by %s" % (self.move, self.player)
    
class UndefinedMove(TTTBaseException):
    def __init__(self, move, player):
        self.move = move
        self.player = player

    def __unicode__(self):
        return "Undefined Move at %d attempted by %s" % (self.move, self.player)

class GameDraw(TTTBaseException):
    def __unicode__(self):
        return "GAME OVER -- DRAW"

class GameWin(TTTBaseException):
    def __init__(self, player):
        self.player = player

    def __unicode__(self):
        return "Player %s won the game!" % self.player

