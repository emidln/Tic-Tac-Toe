winning_rows = [
    range(0,3),
    range(3,6),
    range(6,9),
    [0,3,6],
    [1,4,7],
    [2,5,8],
    [0,4,8],
    [2,4,6],
]
CORNERS = [2,3,6,8]
SIDES = [1,3,5,7]
MIDDLE = [4]
COMPUTER = 1
PLAYER = 2

def choice_logic(b):
    strategies = [strat_win, strat_not_lose, strat_fork, strat_most_winning_rows]
    for s in strategies:
        if s(b):
            return True
    print "all else failed, pick one"
    b.move(b.free()[0],COMPUTER)
    return True

def strat_win(b):
    print "attempting to win"
    p = b.eval_row(2, p=[COMPUTER])
    if p[1] is not None:
        b.move(p[1], COMPUTER)
        return True
    print "could not win"
    return False

def strat_not_lose(b):
    print "attempting not to lose"
    p = b.eval_row(2, p=[PLAYER])
    if p[1] is not None:
        print p[1]
        b.move(p[1], COMPUTER)
        return True
    print "doesn't appear that we'll lose"
    return False

# evaluate forking as a strategy for a given player
# b - Board object
# player - optional tuple containing the number of the player to evaluate for; default: COMPUTER
def strat_fork(b, player=None):
    if player is None:
        player = (COMPUTER,)
    print "attempting fork"
    # constructs the current game from r with replacements
    # r - iterable of of free positions as ints
    # m - position to replace
    # b - Board object
    def modified_row(r,m,b):
        l = []
        for x in r:
            if x != m:
                l.append(b[x])
            else:
                l.append(player[0])
        return l

    d = {}
    for f in b.free():
        r = b.eval_row_multi(2,p=player,rf=lambda r: modified_row(r, f, b))
        print f, '=>', r
        d[f] = r
    for k,v in d.iteritems():
        if v is not None:
            if len(v) == 2:
                b.move(k,COMPUTER)
                return True
    print "no forks found"
    return False


def strat_most_winning_rows(b,player=None):
    if player is None:
        player = PLAYER
    print "attempting most winning rows"
    f = b.free()
    t = [x for x in range(len(b)) if b[x] == player]
    ts = set(t)
    l = [r for r in winning_rows if not ts.intersection(r)]
    if l:
        fd = {}
        for k in f:
            fd[k] = 0
        fset = set(f)
        for r in l:
            i = fset.intersection(r)
            for x in i:
                fd[x] += 1
        print fd
        r = max(fd.iterkeys(), key=lambda x: fd[x])
        #return (True, r)
        b.move(r, (COMPUTER if player == PLAYER else PLAYER))
        return True
    print "most rows didn't pan out"
    return False

