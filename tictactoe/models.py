from django.db import models
from django.utils.safestring import mark_safe
from exceptions import IllegalMove, UndefinedMove, GameWin, GameDraw
from utils import *
# Create your models here.

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

    #def __repr__(self):
    #    return [int(x) for x in self.squares_l]
    #    return str(self)

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

    def as_t(self):
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
        f = [x for x in range(len(self)) if self[x] == 0]
        if not f:   
            raise GameDraw()
        return f

    def taken(self):
        f = [x for x in range(len(self)) if self[x] != 0] 
        if not f:
            raise GameDraw()
        return f

    def foo(self):
        return self[0]

    def eval_winner(self):
        return self.eval_row(3, rf=self.row)[0]
    
    def move(self, square, player):
        try:
            if not self[square]:
                self.eval_winner() # raise GameWin to stop moves on an already completed game
                self[square] = player
                return self.eval_winner()
            else:
                raise IllegalMove(square, player)
        except IndexError:
            raise UndefinedMove(square, player)
        # IllegalMoves are propagated automagically

    def row(self, row):
        return [self[x] for x in row]

    def eval_row(self, c, multi=False, p=None, rf=None):
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
        return winners
