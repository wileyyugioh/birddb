from django.urls import path

from . import views

app_name = "front"
urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("legal/", views.legal, name="legal"),
]
