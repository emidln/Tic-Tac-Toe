""" Board model for tictactoe.

Treats Django model as a mutable list.

* per-item getters and setters should work and automatically translate ints
  to strings
* slicing works, in particular self[:] is used probably far more than it
  should be to get a list of ints
* str() is useful for console debugging (it breaks on rows)
* as_t is slightly nonstandard. It would have led to slightly more code
  duplication if I had written it to be like the standard django as_t and
  leave off the <table></table>. The only real side effect of doing this is
  that you can't customize the header info or add in extra data without some
  work.
* behind the scenes, Board keeps state in squares_l, which is size 9 CharField
* conversions are handled as needed where it makes sense
* some exceptions are passed transparently. This is purposeful since these
  exceptions represent game events like winning, losing, drawing or
  illegal/undefined actions that the user should know about

"""
from django.db import models
from django.utils.safestring import mark_safe
from .exceptions import IllegalMove, UndefinedMove, GameWin, GameDraw
from .utils import winning_rows, COMPUTER, PLAYER


# There's a pylint warning about Abstract class not referenced due to
# pylint's default configuration not understanding Python's Model
# metaclass system. It is safe to ignore.
class Board(models.Model):

    """
    TicTacToe board implemented using a CharField.

    Supports setting/getting positions as if the Board were a list.

    """

    squares_l = models.CharField(max_length=9, default='000000000')
    winner = models.IntegerField(default=0)
    drawn = models.BooleanField(default=False)

    def __len__(self):
        return 9

    def __getitem__(self, k):
        return int(self.squares_l[k])

    def __setitem__(self, k, v):
        l = list(self.squares_l)
        l[k] = v
        self.squares_l = ''.join([str(x) for x in l])
        self.save()

    def __delitem__(self, k):
        raise NotImplementedError()

    def __getslice__(self, i, j):
        return [int(x) for x in self.squares_l[i:j]]

    def __unicode__(self):
        return self.squares_l

    def __str__(self):
        """Return a preformatted output suitable for debugging."""
        return ''.join('%s\n' % (str(x), ) if ((i % 3) == 0) else str(x)
                       for i, x in enumerate(self[:], 1))

    def active(self):
        """Return True if active, False otherwise."""
        return ((self.winner == 0) and (not self.drawn))

    # this adds some extra code, in particular, an extra div and the containing
    # table that as_t doesn't normally add.
    #
    # td elements will have classes of either board_x, board_o, or spacer for
    # styling
    def as_t(self):
        """Return the game as a preformatted table."""

        s = '<div class="board"><table>'
        for x in str(self).strip().split('\n'):
            s += '<tr>'
            for y in x:
                if y == '1':
                    k = ('X', 'board_x')
                elif y == '2':
                    k = ('O', 'board_o')
                else:
                    k = (' ', 'spacer')
                td = '<td><span><div class="cell %s">%s</div></span></td>'
                s += td % (k[1], k[0])
            s += '</tr>'
        s += '</table></div>'
        return mark_safe(s)

    def free(self):
        """Return a list of free squares.

        Raises GameDraw if no squares are available.

        """
        f = [x for x in range(len(self)) if self[x] == 0]
        if not f:
            raise GameDraw()
        return f

    def taken(self):
        """Return a list of taken squares."""
        f = [x for x in range(len(self)) if self[x] != 0]
        return f

    def eval_winner(self):
        """Return the winner or None."""
        return self.eval_row(3)[0]

    # takes two ints, a player and a square.
    # the square should be 0-9 to get left to right starting from the top
    # right to left starting from the bottom (-9 to -1) is supported naturally
    # numbers outside of this range raise UndefinedMove
    # attempting to choose a number that is already taken raises IllegalMove
    # if the game has already finished
    def move(self, square, player):
        """Make a move for player given a square.

        Returns None or raises:
            GameWin if someone wins
            GameDraw if the board state is drawn
            IllegalMove if a move is re-attempted
            UndefinedMove if the move didn't make sense

        Squares are 0 indexed in a 9 element list

        """
        try:
            # raise GameDraw to stop moves on full board
            self.free()
            if not self[square]:
                # raise GameWin to stop moves on an already completed game
                self.eval_winner()
                self[square] = player
                return self.eval_winner()
            else:
                raise IllegalMove(square, player)
        except IndexError:
            raise UndefinedMove(square, player)
        # IllegalMoves, GameDraw, GameWin are propagated too

    def row(self, row):
        """Return an iterable of positions to the implementation."""
        return [self[x] for x in row]

    # pylint/mccabe believe this is too complicated. This is due to
    # it condensing two related functions (whether a winning move
    # can be made next) and whether a win has already occured.
    def eval_row(self, c, players=None):
        """Evaluate the board to determine if a winning row exists.

        Can evaluate for a winning move c=2.
        Can evaluate to see if a win actually occured c=3

        c is the number of squares to evaluate for:
            by passing 2, you find rows that can potentially win next move
            by passing 3, you can determine a game's winner, if any

        Raises a ValueError if you pass in (not (c in  (2, 3)))

        On success:
            Returns a list in the form [player, position that wins]
        On failure:
            Returns [None, None]

        """
        if c not in (2, 3):
            raise ValueError("eval_row only accepts 2 or 3")

        if players is None:
            players = (COMPUTER, PLAYER)

        # raise GameDraw if necessary
        self.free()
        for row in winning_rows:
            the_row = self.row(row)
            for player in players:
                if the_row.count(player) == c:
                    if c == 2:
                        if the_row.count(0):
                            return [player, row[the_row.index(0)]]
                    else:  # c == 3
                        raise GameWin(player)
        return [None, None]
