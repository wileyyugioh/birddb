from django.db.models import F

from .models import Bird, BirdPollColor
from .scrape.colornames import COLOR_NAMES


class BirdPoll:
    """ Accessing our BirdPoll Model """
    @staticmethod
    def verify(bird_id, color):
        """ Verify the data """
        try:
            bird = Bird.objects.prefetch_related("birdpollcolor_set").get(pk=bird_id)
        except Bird.DoesNotExist:
            return False

        if color not in COLOR_NAMES:
            return False

        return bird

    @staticmethod
    def vote(bird_id, color):
        """ Add a vote for a color of a given bird """
        bird = BirdPoll.verify(bird_id, color)

        if not bird:
            return False

        try:
            bird_color = bird.birdpollcolor_set.get(color__iexact=color)
        except BirdPollColor.DoesNotExist:
            # Create a new entry
            bird_color = bird.birdpollcolor_set.create(color=color, votes=0)
        bird_color.votes = F("votes") + 1
        bird_color.save()

        return True