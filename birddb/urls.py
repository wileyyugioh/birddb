from django.urls import path

from . import views

app_name = 'birddb'
urlpatterns = [
    # ex: /birddb/bird_ranks/
    path("bird_ranks/", views.bird_ranks, name="bird_ranks"),

    # ex /birdbb/bird_poll/BIRD_ID/
    path("bird_poll/<int:bird_id>/", views.bird_poll, name="bird_poll"),

    # ex /birddb/bird_partial/
    path("bird_partial/", views.bird_partial, name="bird_partial"),

    # ex/birddb/bird_error/
    path("bird_error/", views.bird_error, name="bird_error")
]
