from django.contrib import admin

from .models import Bird, BirdPollColor, Genus, InvalidBird

admin.site.register(Bird)
admin.site.register(Genus)
admin.site.register(BirdPollColor)
admin.site.register(InvalidBird)