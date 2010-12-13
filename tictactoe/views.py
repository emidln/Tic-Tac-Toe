from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404

from models import Board
from logic import evaluate_gamestate
from utils import COMPUTER, PLAYER
from exceptions import *

### BUGS ###
# (1) None of these boards enforce any sort of user authentication
# (2) As a consequence of (2), your game could get interrupted or deleted by another person
##################33333

# potential timing issue
# create a board then go to it. this could theoretically lead to two players
# trying to play the same game if one issued a request to tictactoe directly after tictactoe_index
# was called
def index(request):
    b = Board() 
    b.save()
    return HttpResponseRedirect(reverse('tictactoe', args=[b.id]))

# per board game access
def tictactoe(request, board_id):
    b = Board.objects.get_or_create(pk=board_id)[0]
    b.save()
    d = {'board': b}
    return direct_to_template(request, 'tictactoe/tictactoe.html', extra_context=d )

# ajax update
def board_update(request, board_id):
    if request.is_ajax():
        messages = []
        d = {}
        try:
            m = request.GET['m']
        except KeyError: 
            raise Http404()        
        try: 
            b = Board.objects.get(pk=board_id)
            b.free() # will raise GameDraw if no moves are left
            b.move(int(m),PLAYER)
            evaluate_gamestate(b) 
            d['board'] = b
        except Board.DoesNotExist:
            pass
        except GameWin, e:
            d['board'] = b
            messages.append(str(e))            
        except GameDraw, e:
            d['board'] = b
            messages.append(str(e))
        except IllegalMove, e:
            messages.append(str(e))
        except UndefinedMove, e:
            messages.append(str(e))
        except ValueError:
            messages.append('Value passed must be an integer.')
        if messages:
            d['messages'] = messages    
        return render_to_response('tictactoe/board_update.xml', d, context_instance=RequestContext(request), mimetype='text/xml')
    else:
        raise Http404()
