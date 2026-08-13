from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Music, RecentlyPlayed

@login_required
def like_song(request, song_id):
    song = get_object_or_404(Music, id=song_id)

    song.likes.add(request.user)

    return JsonResponse({
        "message": "Song liked successfully"
    })


@login_required
def unlike_song(request, song_id):
    song = get_object_or_404(Music, id=song_id)

    song.likes.remove(request.user)

    return JsonResponse({
        "message": "Song unliked successfully"
    })


@login_required
def check_like(request, song_id):
    song = get_object_or_404(Music, id=song_id)

    liked = song.likes.filter(id=request.user.id).exists()

    return JsonResponse({
        "liked": liked
    })


@login_required
def liked_songs(request):
    songs = request.user.liked_music.all()

    return JsonResponse({
        "liked_songs": [
            {
                "id": song.id,
                "title": song.title,
                "artist": str(song.artist),
            }
            for song in songs
        ]
    })


@login_required
def play_song(request, song_id):
    song = get_object_or_404(Music, id=song_id)

    recently_played, created = RecentlyPlayed.objects.get_or_create(
        user=request.user,
        music=song
    )

    if not created:
        recently_played.save()

    return JsonResponse({
        "message": "Song played successfully"
    })


@login_required
def recently_played(request):
    songs = RecentlyPlayed.objects.filter(user=request.user)

    return JsonResponse({
        "recently_played": [
            {
                "id": item.music.id,
                "title": item.music.title,
                "artist": str(item.music.artist),
                "played_at": item.played_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for item in songs
        ]
    }, json_dumps_params={"indent": 4})
