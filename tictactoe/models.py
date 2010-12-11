from django.db import models
from django.utils.safestring import mark_safe
from exceptions import IllegalMove, UndefinedMove, GameWin, GameDraw
from utils import *

# * per-item getters and setters should work and automatically translate ints to strings
# * slicing works, in particular self[:] is used probably far more than it should be to 
#   get a list of ints
# * str() is useful for console debugging (it breaks on rows)
# * as_t is slightly nonstandard. It would have led to slightly more code duplication if I had 
#   written it to be like the standard django as_t and leave off the <table></table>. The only
#   real side effect of doing this is that you can't customize the header info or add in extra
#   data without some work. 
# * behind the scenes, Board keeps state in squares_l, which is size 9 CharField
# * conversions are handled as needed where it makes sense
# * some exceptions are passed transparently. This is purposeful since these exceptions represent 
#   game events like winning, losing or illegal/undefined actions that the user should know about
class Board(models.Model):
    squares_l = models.CharField(max_length=9,default='000000000')

    def __len__(self):
        return 9

    def __getitem__(self,k):
        return int(self.squares_l[k])

    def __setitem__(self,k,v):
        l = list(self.squares_l)
        l[k] = v
        self.squares_l = ''.join([str(x) for x in l])
        self.save()

    def __getslice__(self, i, j):
        return [int(x) for x in self.squares_l[i:j]]     

    def __unicode__(self):
        return self.squares_l

    # returns a preformatted output suitable for debugging
    def __str__(self):
        i = 1
        s = ''
        for x in self[:]:
            if (i%3) == 0:
                s = ''.join([s, str(x), '\n'])
                i += 1
            else:
                s += str(x)
                i += 1
        return s

    # this adds some extra code, in particular, an extra div and the containing table 
    # that as_t doesn't normally add.
    #
    # td elements will have classes of either board_x, board_o, or spacer for styling
    def as_t(self):
        '''return the game as a preformatted table'''
        i = 1
        s = '<div class="board"><table>'
        for x in str(self).strip().split('\n'):
            s += '<tr>'
            for y in x:
                if y == '1':
                    k = ('X','board_x') 
                elif y == '2': 
                    k = ('O','board_o')
                else:
                    k = (' ','spacer')
                s += '<td><span><div class="cell %s">%s</div></span></td>' % (k[1],k[0])
            s += '</tr>'
        s += '</table></div>'    
        return mark_safe(s)

    def free(self):
        '''returns a list of free squares. raises GameDraw if no squares are available'''
        f = [x for x in range(len(self)) if self[x] == 0]
        if not f:   
            raise GameDraw()
        return f

    def taken(self):
        '''returns a list of taken squares.'''
        f = [x for x in range(len(self)) if self[x] != 0] 
        return f

    def eval_winner(self):
        '''returns the winner or None'''
        return self.eval_row(3, rf=self.row)[0]
    
    # takes two ints, a player and a square. 
    # the square should be 0-9 to get left to right starting from the top 
    # right to left starting from the bottom (-9 to -1) is supported naturally
    # numbers outside of this range raise UndefinedMove
    # attempting to choose a number that is already taken raises IllegalMove
    # if the game has already finished 
    def move(self, square, player):
        '''makes a move for player given a square. squares are 0 indexed in a 9 element list'''
        try:
            self.free() # raise GameDraw to stop moves on full board
            if not self[square]:
                self.eval_winner() # raise GameWin to stop moves on an already completed game
                self[square] = player
                return self.eval_winner()
            else:
                raise IllegalMove(square, player)
        except IndexError:
            raise UndefinedMove(square, player)
        # IllegalMoves, GameDraw, GameWin are propagated too

    def row(self, row):
        '''resolve an iterable of positions to the contents of the internal storage'''
        return [self[x] for x in row]

    # c is the number of squares to evaluate for
    #   by selecting 2, you find rows that can potentially win next move
    #   by selecting 3, you can determine a game's winner, if any
    # p is an iterable of players
    # rf is a function taking an iterable that resolves positions to values
    #
    # raises an exception if c isn't correct
    # raises GameWin if a winner is determined
    # on success:
    #     returns a list in the form [player, position that wins]
    # on failure:
    #     returns [None,None]
    def eval_row(self, c, p=None, rf=None):
        '''evaluate the board to determine if a winning row can be found for varying values of winning'''
        if c not in (2,3):
            raise Exception("eval_row only accepts 2 or 3") 
        if p is None:
            p = (1,2)
        if rf is None:
            rf = self.row
        for r in winning_rows:
            tr = rf(r)
            for x in p:
                if tr.count(x) == c:
                    if c == 2:
                        if tr.count(0):
                            return [x, r[tr.index(0)]]
                    else: # c == 3
                        raise GameWin(x)
        return [None, None]
