
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from .models import Artist, Music, Album, RecentlyPlayed, Playlist
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.template import context
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView


# Create your views here.
def home(request):
    music_list = Music.objects.all()
    if request.method == "GET":
        music_title = request.GET.get("music")
        if music_title!= None:
            music_list = Music.objects.filter(title__icontains=music_title)
    context = {
        'music_list': music_list 
    }
    return render(request, 'music/home.html', context)


class CreatePlaylistView(CreateView):
    model = Playlist
    fields = ['name', 'description', 'music']
    template_name = 'music/create_playlist.html'
    success_url = reverse_lazy('music-home') 

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
class UpdatePlaylistView(UpdateView):
    model = Playlist
    fields = ['name', 'description', 'music']
    template_name = 'music/update_playlist.html'
    success_url = reverse_lazy('music-home') 

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class DeletePlaylistView(DeleteView):
    model = Playlist
    success_url = '/'

class ArtistDetailView(DetailView):
    model = Artist
    template_name = 'music/artist_detail.html'
    context_object_name = 'artist'

@require_POST
def create_album(request):
    try :
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error" : "Invalid JSON"},
            status = 400
        )
    
    title = data.get("title")
    release_date = data.get("release_date")
    genre = data.get("genre")
    artist_id = data.get("artist_id")
    
    if not title or not release_date or not genre or not artist_id:
        return JsonResponse(
            {"error" : "title, release_date, genre and artist_id are required"},
            status = 400
        )
        
    try:
        artist = Artist.objects.get(id = artist_id)
    except Artist.DoesNotExist:
        return JsonResponse(
            {"error" : "Artist not found"},
            status = 404
        )
    
    album = Album.objects.create(
        title = title,
        artist = artist,
        release_date = release_date,
        genre = genre
    )
    
    return JsonResponse(
        {"message" : "Album created successfully",
         "album_id" : album.id},
        status = 201
    )

@require_http_methods(["DELETE"])
def delete_album(request, album_id):
    try:
        album = Album.objects.get(id=album_id)
    except Album.DoesNotExist:
        return JsonResponse(
            {"error": "Album not found"},
            status=404
        )
    album.delete()

    return JsonResponse(
        {"message": "Album deleted successfully"},
        status=200
    )

@require_POST
def create_song(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )

    title = data.get("title")
    album_id = data.get("album_id")
    artist_id = data.get("artist_id")
    release_date = data.get("release_date")
    genre = data.get("genre")

    if not title or not album_id or not artist_id or not release_date or not genre:
        return JsonResponse(
            {"error": "title, album_id, artist_id, release_date and genre are required"},
            status=400
        )

    try:
        artist = Artist.objects.get(id=artist_id)
    except Artist.DoesNotExist:
        return JsonResponse(
            {"error": "Artist not found"},
            status=404
        )

    try:
        album = Album.objects.get(id=album_id)
    except Album.DoesNotExist:
        return JsonResponse(
            {"error": "Album not found"},
            status=404
        )

    song = Music.objects.create(
        title=title,
        artist=artist,
        album=album,
        release_date=release_date,
        genre=genre
    )

    return JsonResponse(
        {
            "message": "Song created successfully",
            "song_id": song.id
        },
        status=201
    )
  
@require_http_methods(["DELETE"])
def delete_song(request, song_id):
    try:
        song = Music.objects.get(id=song_id)
    except Music.DoesNotExist:
        return JsonResponse(
            {"error": "Song not found"},
            status=404
        )
    song.delete()

    return JsonResponse(
        {"message": "Song deleted successfully"},
        status=200
    )

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

def follow_unfollow(request, id):
    if request.method != "POST":
        return redirect('music-home')

    artist = get_object_or_404(Artist, id=id)

    if request.user in artist.followers.all():
        artist.followers.remove(request.user)  
    else:
        artist.followers.add(request.user)

    return redirect('artist-detail', pk=artist.id)





