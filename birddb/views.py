from django.db.models import prefetch_related_objects
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Bird

from .birdpoll import BirdPoll
from .birdaccess import TooLongError
from .birdranker import SearchData
from .birdsearch import BirdSearcher
from .scrape.colornames import SIMPLIFIED_COLORS_NAMES


# THERE CAN BE ONLY ONE!
bs = BirdSearcher()


MAX_SIZE = 20


def bird_ranks(request):
    """ Page for every little birdy """
    try:
        lat = float(request.GET["lat"])
        lon = float(request.GET["lon"])
        color = request.GET["color"]
        size = float(request.GET["size"])
    except KeyError:
        return HttpResponseBadRequest("Error, missing data")
    except ValueError:
        return HttpResponseBadRequest("Error, invalid data")

    sd = SearchData(lat, lon, color, size)

    if not sd.valid():
        return HttpResponseBadRequest("Error, incomplete/incorrect data")

    try:
        bird_rankings = bs.search(sd)
        render_birds = []
        if bird_rankings:
            render_birds = [bird[0] for bird in bird_rankings[:MAX_SIZE]]
            prefetch_related_objects(render_birds, "webdata")
        return render(request, "birddb/bird_ranks.html", {"bird_ranks": render_birds, "COLOR_NAMES": SIMPLIFIED_COLORS_NAMES})
    except TooLongError:
        # Took too long, so show error page
        return redirect("birddb:bird_error")
    except Exception as e:
        # Unknown error
        raise e
        return HttpResponseBadRequest("Unknown error")


def bird_poll(request, bird_id):
    """ Add a color to the BirdPoll """
    try:
        color = request.POST["color"]
    except KeyError:
        return HttpResponseBadRequest("Invalid data")
    
    # Validation code in BirdPoll
    if not BirdPoll.vote(bird_id, color):
        return HttpResponseBadRequest("Failed to update poll data")
    return HttpResponse("Succeeded")


def bird_partial(request):
    """ Show all partial birds """
    return render(request, "birddb/bird_partial.html", {"bird_ranks": Bird.objects.filter(color__exact=None, birdpollcolor__isnull=True).prefetch_related("webdata")[:MAX_SIZE], 
                                                        "COLOR_NAMES": SIMPLIFIED_COLORS_NAMES})


def bird_error(request):
    """ Webpage error message """
    return render(request, "birddb/bird_error.html")