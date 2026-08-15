from django.contrib.admin import views
from django.urls import path

from .views import (like_song,
                    unlike_song,
                    check_like,
                    liked_songs,
                    play_song,
                    recently_played,
                    create_album,
                    delete_album,
                    create_song,
                    delete_song,CreateplaylistView)



urlpatterns = [
    path("like/<int:song_id>/", like_song, name="like_song"),
    path("unlike/<int:song_id>/", unlike_song, name="unlike_song"),
    path("like/<int:song_id>/check/", check_like, name="check_like"),
    path("liked-songs/", liked_songs, name="liked_songs"),
    path("play/<int:song_id>/", play_song, name="play_song"),
    path("recently-played/", recently_played, name="recently_played"),
    path('playlist/create/', CreateplaylistView.as_view(), name='create_playlist'),
    path("publisher/albums/", create_album, name="create_album"),
    path("publisher/albums/<int:album_id>/", delete_album, name="delete_album"),
    path("publisher/songs/", create_song, name="create_song"),
    path("publisher/songs/<int:song_id>/", delete_song, name="delete_song")
]



