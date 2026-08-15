from django.contrib.admin import views
from django.urls import path
from .views import home, CreatePlaylistView,  UpdatePlaylistView,DeletePlaylistView, like_song, unlike_song, check_like, liked_songs, play_song, recently_played, ArtistDetailView, follow_unfollow
from .views import (like_song,
                    unlike_song,
                    check_like,
                    liked_songs,
                    play_song,
                    recently_played,
                    create_album,
                    delete_album,
                    create_song,
                    delete_song)


urlpatterns = [
    path("", home, name="music-home"),
    path("like/<int:song_id>/", like_song, name="like_song"),
    path("unlike/<int:song_id>/", unlike_song, name="unlike_song"),
    path("like/<int:song_id>/check/", check_like, name="check_like"),
    path("liked-songs/", liked_songs, name="liked_songs"),
    path("play/<int:song_id>/", play_song, name="play_song"),
    path("recently-played/", recently_played, name="recently_played"),
    path('playlist/create/', CreatePlaylistView.as_view(), name='create_playlist'),
    path('playlist/<int:pk>/update/', UpdatePlaylistView.as_view(), name='update_playlist'),
    path('playlist/<int:pk>/delete/', DeletePlaylistView.as_view(), name='delete_playlist'),
    path('artist/<int:pk>/', ArtistDetailView.as_view(), name='artist-detail'),
    path('artist/<int:id>/follow/', follow_unfollow, name='follow_unfollow'),

    path("publisher/albums/", create_album, name="create_album"),
    path("publisher/albums/<int:album_id>/", delete_album, name="delete_album"),
    path("publisher/songs/", create_song, name="create_song"),
    path("publisher/songs/<int:song_id>/", delete_song, name="delete_song")
]
