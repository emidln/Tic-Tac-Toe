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

CORNERS = [0,2,6,8]
SIDES = [1,3,5,7]
MIDDLE = [4]

EMPTY = 0
COMPUTER = 1
PLAYER = 2

def list_equal(l):
    return len(set(l)) <= 1

def is_empty(square):
    return bool(square)

def rotate3x3(l):
    '''return a rotated 3x3 matrix represented as a 1d list by pi/2'''
    tl = [6,3,0,7,4,1,8,5,2]
    i = 0
    nl = [0]*9
    while i < len(s):
        nl[tl[i]] = l[i]
        i += 1
    return nl 

def choice_logic(b):
    strategies = [strat_win, strat_not_lose, strat_fork, strat_most_winning_rows]
    for s in strategies:
        if s(b):
            return True
    b.move(b.free()[0],COMPUTER)
    return True

def strat_win(b):
    p = b.eval_row(2, p=[COMPUTER])
    if p[1] is not None:
        b.move(p[1], COMPUTER)
        return True
    return False

def strat_not_lose(b):
    p = b.eval_row(2, p=[PLAYER])
    if p[1] is not None:
        print p[1]
        b.move(p[1], COMPUTER)
        return True
    return False


def modified_row(r,m,b):
    l = []
    for x in r:
        if x != m:
            l.append(b.squares[x])
        else:
            l.append(m)
    return l

def strat_fork(b, player=None):
    if player is None:
        player = (COMPUTER,)
    d = {} 
    for f in b.free():
        d[f] = b.eval_row_multi(2,p=player,rf=lambda r: modified_row(r, f, b))
    for k,v in d.iteritems():
        if len(v) == 2:
            b.move(k,COMPUTER)
            return True
    return False 

def strat_defend_fork(b):
    # same as strategy to make the strongest choice
    pass

# find the squares that are not taken by the opponent and determine 
# which of those has the most chance to win for you
def strat_most_winning_rows(b,player=None):
    if player is None:
        player = PLAYER
    f = b.free()
    t = [x for x in range(len(b.squares)) if b.squares[x] == player]
    ts = set(t)
    l = [r for r in winning_rows if not ts.intersection(r)]
    if l:
        fd = {}
        for k in f:
            fd[k] = 0 
        fset = set(f)
        for r in l:
            i = fset.intersection(r)
            #print r, i, i.difference([x for x in range(len(b.squares)) if b.squares[x] == (COMPUTER if player == PLAYER else PLAYER)])
            for x in i:
                fd[x] += 1
        print fd
        r = max(fd.iterkeys(), key=lambda x: fd[x])
        #return (True, r)
        b.move(r, (COMPUTER if player == PLAYER else PLAYER)) 
        return True
    return False
 
def strat_sides(b):
    f = b.free()
    i = set(f).intersection(SIDES)
    if i:
        b.move(i.pop(), COMPUTER)
        return True
    return False

def strat_middle(b):
    if MIDDLE in b.free():
        b.move(i.pop(), COMPUTER)
        return True
    return False

def strat_opposite(b):
    f = b.free()
    fc = set(f).intersection(CORNERS)
    if fc:
        opc = set([x for x in b.squares if x == PLAYER]).intersection(CORNERS)
        for x in opc:
            for j,k in ((0,8),(2,6),(6,2),(8,0)):
                if x == j and k in fc:
                    b.move(k, COMPUTER)
                    return True
    return False
                       
def strat_corners(b):
    f = b.free()
    i = set(f).intersection(CORNERS)
    if i:
        b.move(i.pop(), COMPUTER)
        return True
    return False
    
    
class BaseClass(Exception):
    def __str__(self):
        return str(unicode(self))

    def __repr__(self):
        return str(self)

class IllegalMove(BaseClass):
    def __init__(self, move, player):
        self.move = move
        self.player = player

    def __unicode__(self):
        return "Illegal Move at %d attempted by %s" % (self.move, self.player)

class UndefinedMove(BaseClass):
    def __init__(self, move, player):
        self.move = move
        self.player = player

    def __unicode__(self):
        return "Undefined Move at %d attempted by %s" % (self.move, self.player)

class GameDraw(BaseClass):
    def __unicode__(self):
        return "GAME OVER -- DRAW"

#    def __str__(self):
#        return str(unicode(self))

#    def __repr__(self):
#        return str(self)

class GameWin(BaseClass):
    def __init__(self, player):
        self.player = player

    def __unicode__(self):
        return "Player %s won the game!" % self.player

#    def __repr__(self):
#        return str(unicode(self))

#    def __str__(self):
#        return str(unicode(self))

# This Board does not enforce the number of players. That is handled elsewhere.
class Board(object):
    def __init__(self):
        self.squares = [0 for x in xrange(0,9)]
       
    def move(self, square, player):
        '''Attempts a move on behalf of a player. On successful completion, returns None to indicate the game should continue and returns the winner
           if there is one. On an illegal move (square already taken), an IllegalMove is raised. On an undefined move (outside of the board), an
           UndefinedMove is raised. Both exceptions contain the move in question and the player attempting.'''
        try:
            if not self.squares[square]:
                self.squares[square] = player
                return self.eval_winner()
            else:
                raise IllegalMove(square, player)
        except IndexError:
            raise UndefinedMove(square, player)
        #IllegalMoves are propagated

    def row(self, row):
        return [self.squares[x] for x in row]

    def free(self):
        f = [x for x in range(len(self.squares)) if self.squares[x] == 0]
        if not f:
            raise GameDraw()
        return f           
 
    # c is a number of identical squares to check for
    # p is an iterable of players to check squares for
    def eval_row(self, c, p=None, rf=None):
        '''returns the player matched if a player has count, else None'''
        if c not in (2,3):
            raise Exception()
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
                    #print r, tr
                    #return [x, r[tr.index(0)] if c == 2 else None]
        return [None, None]    

    def eval_row_multi(self, c, p=None, rf=None):
        if p is None:       
            p = (1,2)
        if rf is None:
            rf = self.row
        winners = []
        for r in winning_rows:
            tr = rf(r)
            for x in p:
                if tr.count(x) == c and (tr.count(0) == 1 if c == 2 else True):
                    winners.append([x, r[tr.index(0)] if c == 2 else None])
        if not winners:
            return [None]
        else:
            return winners
       
    def __str__(self):
        i = 1 
        s = ""
        for x in self.squares:
            if (i%3) == 0:
                s = ''.join([s, str(x), '\n'])
                i += 1
            else:
                s += str(x) 
                i += 1
        return s 

    def __repr__(self):
        return str(self)

    def eval_winner(self):
        '''Returns None if no winner, otherwise the winner'''
        return self.eval_row(3, rf=self.row)[0]

if __name__ == '__main__':
    b = Board()
    while True:
        try:
            print b
            print "COMPUTER is 1. PLAYER is 2"
            r = raw_input("What is your Move? ")
            b.move(int(r), PLAYER)
            choice_logic(b)
        except GameDraw, e:
            print b
            print e
            break
        except GameWin, e:
            print b
            print e
            break
        except IllegalMove, e:
            print e
            continue
        except UndefinedMove, e:
            print e
            continue

            

