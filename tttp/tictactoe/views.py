""" Views for tictactoe.

In an effort to maintain existing code, the
function direct_to_template from django.views.generic.simple was
essentially mocked using a custom TemplateView.

"""
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render

from .models import Board
from .logic import evaluate_gamestate
from .utils import PLAYER
from .exceptions import GameWin, GameDraw, IllegalMove, UndefinedMove


### BUGS ###
# (1) None of these boards enforce any sort of user authentication
# (2) As a consequence of (2), your game could get interrupted or deleted by
#     another person
##################

# potential timing issue
# create a board then go to it. this could theoretically lead to two players
# trying to play the same game if one issued a request to tictactoe directly
# after tictactoe_index was called


def index(request):
    """ Return a redirect to a newly created board. """
    b = Board()
    b.save()
    return HttpResponseRedirect(reverse('tictactoe', args=[b.id]))


def tictactoe(request, board_id):
    """ Return response with a particular board rendered. """
    b = Board.objects.get_or_create(pk=board_id)[0]
    b.save()
    d = {'board': b}
    return render(request,
                  template_name='tictactoe/tictactoe.html',
                  dictionary=d)


# mccabe claims that board_update is too complex due to the extensive
# exception handling in it. The exceptions are informative game events
# and need to be handled here.
def board_update(request, board_id):
    """ Return taconite response updating the board based on the play. """
    if request.is_ajax():
        messages = []
        d = {}
        try:
            m = request.GET['m']
        except KeyError:
            raise Http404()
        try:
            b = Board.objects.get(pk=board_id)
            b.free()  # will raise GameDraw if no moves are left
            b.move(int(m), PLAYER)
            evaluate_gamestate(b)
            d['board'] = b
        except Board.DoesNotExist:
            pass
        except GameWin as e:
            b.winner = e.player
            b.save()
            d['board'] = b
        except GameDraw as e:
            b.drawn = True
            b.save()
            d['board'] = b
        except (IllegalMove, UndefinedMove) as e:
            messages.append(str(e))
        except ValueError:
            messages.append('Value passed must be an integer.')
        d['messages'] = messages
        return render(request,
                      template_name='tictactoe/board_update.xml',
                      dictionary=d,
                      content_type='text/xml')
    else:
        raise Http404()
