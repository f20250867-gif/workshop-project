from django.contrib.admin import views
from django.urls import path
from music.views import CreateplaylistView
from .views import like_song, unlike_song, check_like, liked_songs, play_song, recently_played

urlpatterns = [
    path("like/<int:song_id>/", like_song, name="like_song"),
    path("unlike/<int:song_id>/", unlike_song, name="unlike_song"),
    path("like/<int:song_id>/check/", check_like, name="check_like"),
    path("liked-songs/", liked_songs, name="liked_songs"),
    path("play/<int:song_id>/", play_song, name="play_song"),
    path("recently-played/", recently_played, name="recently_played"),
    path('playlist/create/', CreateplaylistView.as_view(), name='create_playlist'),
]

