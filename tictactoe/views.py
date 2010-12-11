from django.views.generic.simple import direct_to_template, redirect_to
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


from models import Board
from logic import evaluate_gamestate
from utils import COMPUTER, PLAYER
from exceptions import *

### BUGS ###
# (1) None of these boards enforce any sort of user authentication
# (2) As a consequence of (2), your game could get interrupted or deleted by another person
##################33333

# this could be in urls.py, but it may eventually get more complex
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

def board_update(request, board_id):
    messages = []
    d = {}
    if request.is_ajax():
        m = request.GET.get('m')
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

def board_clear(request, board_id):
    d = {}
    #if request.is_ajax():
    if True:
        try:
            b = Board.objects.get(pk=board_id)
            b.latest_l = "000000000"
            b.save()
            d['board'] = b
        except Board.DoesNotExist:
            pass
    return render_to_response('tictactoe/board_update.xml', d, context_instance=RequestContext(request), mimetype='text/xml')
