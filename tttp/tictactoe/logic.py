""" Logic for the computer to play TicTacToe. """
from .utils import COMPUTER, PLAYER


def move_count(b):
    """ Return the move count in the game, taking a board object. """
    return 9 - b[:].count(0)


# pylint and mccabe complain this is a faily complicated piece of code, which
# it is. I don't believe it has too many branches, and while I could trivially
# rewrite it to use dictionary lookups and piecemeal functions, I believe that
# doing so loses clarity, not increases it. This is a discussion for the team
# I'm working on, and could be changed in the future.
def evaluate_gamestate(b):
    """ Evaluate the gamestate so the COMPUTER can move.

    Return values are ignored, but return is used to short-circuit the function.
    The return value will always be True if the function returns, but an
    Exception may be thrown for game state conditions.

    The logic here is to force reciprocal blocking ASAP.

    """

    mc = move_count(b)

    if mc == 0:
        b.move(4, COMPUTER)
        return True
    elif mc == 1:
        if 4 not in b.taken():
            # opponent didn't take center, so take it
            b.move(4, COMPUTER)
            return True
        else:
            # take the first corner
            b.move(0, COMPUTER)
            return True
    elif mc == 2:
        # take a corner in non-diagonal line with PLAYER to force blocks
        outers = [[0, 1, 2], [6, 7, 8], [0, 3, 6], [2, 5, 8]]
        p = b[:].index(PLAYER)
        for row in outers:
            if p in row:
                i = set([0, 2, 6, 8]).intersection(row)
                if p not in i:
                    # they took the middle, corner doesn't matter
                    b.move(i.pop(), COMPUTER)
                    return True
                else:
                    # take a remaining corner
                    i.remove(p)
                    b.move(i.pop(), COMPUTER)
                    return True
    elif mc == 3:
        if b[4] == PLAYER:
            # any move made requires a block leading to a draw
            # exception still taken care of by wbcf
            return win_block_corner_first(b)
        elif b[4] == COMPUTER:
            l = [x for x in b.taken() if b[x] == PLAYER]
            sl = set(l)
            if sl >= set((0, 8)) or sl >= set((2, 6)):
                # opp in opposite corners, play a side to force draws
                b.move(1, COMPUTER)
                return True
            sc = sl.intersection([1, 3, 5, 7])
            if sc:
                # opponent in a side
                if len(sc) == 1:
                    # either block or choose a corner
                    return win_block_corner_first(b)
                if len(sc) == 2:
                    forks = (
                        ((1, 5), 2),
                        ((3, 7), 6),
                        ((1, 3), 0),
                        ((5, 7), 8)
                    )
                    for fork in forks:
                        if sc >= set(fork[0]):
                            b.move(fork[1], COMPUTER)
                            return True
                    # opp is on opposite sides and gets to initiate blocking
                    # after our move
                    return win_block_corner_first(b)
            else:
                # all other scenarios are block scenarios
                return win_block_corner_first(b)
    else:
        return win_block_corner_first(b)


def win(b):
    """Attempt win, raising GameWin if it occurs, return False otherwise."""
    p = b.eval_row(2, players=[COMPUTER])
    if p[1] is not None:
        b.move(p[1], COMPUTER)
        return True
    return False


def block(b):
    """Attempt block, raising GameDraw if it occurs, return False otherwise."""
    p = b.eval_row(2, players=[PLAYER])
    if p[1] is not None:
        b.move(p[1], COMPUTER)
        return True
    return False


def corner(b):
    """Attempt corner, raising GameDraw if it occurs, return False otherwise."""
    i = set([0, 2, 6, 8]).intersection(b.free())
    if i:
        b.move(i.pop(), COMPUTER)
        return True
    return False


def first(b):
    """Return True or raise an except ending the block_corner_free chain."""
    b.move(b.free().pop(), COMPUTER)
    return True


def win_block_corner_first(b):
    """Thread through win, block, corner, first actions.

    Return True to short-circuit or raise an Exception.

    """
    for x in (win, block, corner, first):
        r = x(b)
        if r:
            return r
