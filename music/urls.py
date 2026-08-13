from django.urls import path
from . import views

urlpatterns = [
    path("publisher/albums/", views.create_album),
    path("publisher/albums/<int:album_id>/", views.delete_album),
    path("publisher/songs/", views.create_song),
    path("publisher/songs/<int:song_id>/", views.delete_song)
]