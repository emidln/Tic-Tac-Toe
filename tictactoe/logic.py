from utils import COMPUTER, PLAYER

# move count in the game, takes a board
def move_count(b):
    return 9-b[:].count(0)

# I had a really complicated way to determining forks and such until I realized
# that the challenge was only to not lose, not to potentially win. As such, 
# I streamlined the perfect tic tac toe game theory down considerably
#
# This will attempt to force reciprocal blocking ASAP
#
# takes a Board objects and returns True if action was taken
# Exceptions are not caught because they're inforrmational to the user
# such as drawing, winning, illegal moves, undefined moves, etc
def evaluate_gamestate(b):
    mc = move_count(b)

    if mc== 0:
        b.move(4,COMPUTER)
        return True
    elif mc == 1:
        if 4 not in b.taken():
            # opponent didn't take center, so take it
            b.move(4,COMPUTER)
            return True
        else:
            # take the first corner
            b.move(0,COMPUTER)
            return True
    elif mc == 2:
        # take a corner in non-diagonal line with PLAYER to force blocks
        outers = [[0,1,2],[6,7,8],[0,3,6],[2,5,8]]
        p = b[:].index(PLAYER)
        for row in outers:
            if p in row:
                i = set([0,2,6,8]).intersection(row)
                if p not in i:
                    # they took the middle, corner doesn't matter
                    b.move(i.pop(),COMPUTER)
                    return True
                else:
                    # take a remaining corner
                    i.remove(p)
                    b.move(i.pop(), COMPUTER)  
                    return True
    elif mc == 3:
        if b[4] == PLAYER:
            # any move made requires a block leading to a draw
            return win_block_corner_first(b)    
        elif b[4] == COMPUTER:
            l = [x for x in b.taken() if b[x] == PLAYER]
            sl = set(l)
            if sl >= set((0,8)) or sl >= set((2,6)):
                # opp in opposite corners, play a side to force draws
                b.move(1,COMPUTER)
                return True
            sc = sl.intersection([1,3,5,7])
            if sc:
                # opponent in a side
                if len(sc) == 1:
                    # either block or choose a corner
                    return win_block_corner_first(b)
                if len(sc) == 2:
                    if sc >= set(1,5):
                        # take middle corner
                        b.move(2,COMPUTER)
                        return True
                    if sc >= set(3,7):
                        b.move(6, COMPUTER)
                        return True        
            else:
                # all other scenarios are block scenarios
                return win_block_corner_first(b)
    else:
        return win_block_corner_first(b)

def win(b):
    p = b.eval_row(2, p=[COMPUTER])
    if p[1] is not None:
        b.move(p[1], COMPUTER)
        return True
    return False

def block(b):
    p = b.eval_row(2, p=[PLAYER])
    if p[1] is not None:
        b.move(p[1], COMPUTER)
        return True
    return False

def corner(b):
    i = set([0,2,6,8]).intersection(b.free())
    if i:
        b.move(i.pop(), COMPUTER)
        return True
    return False

# this will always return True or hit an exception ending the block_corner_free chain
def first(b): 
    b.move(b.free().pop(), COMPUTER)
    return True


def win_block_corner_first(b):
    for x in (win,block,corner,first):
        r = x(b)
        if r:
            return r
