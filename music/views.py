
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from .models import Artist, Music, Album, RecentlyPlayed, Playlist
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template import context
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from .models import Artist, Music, RecentlyPlayed, Playlist
from .forms import SongUploadForm, AlbumUploadForm


# Create your views here.
def home(request):
    music_list = Music.objects.all()
    music_title = request.GET.get("music")
    album_title = request.GET.get("album")
    artist_query = request.GET.get("artist")

    if music_title:
        music_list = music_list.filter(title__icontains=music_title)
    if album_title:
        music_list = music_list.filter(album__title__icontains=album_title)

    artist_results = Artist.objects.filter(name__icontains=artist_query) if artist_query else None

    context = {
        'music_list': music_list,
        'music_query': music_title or '',
        'album_query': album_title or '',
        'artist_query': artist_query or '',
        'artist_results': artist_results,
    }
    if request.user.is_authenticated:
        context['my_playlists'] = request.user.playlists.all()

    return render(request, 'music/home.html', context)


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')


class CreatePlaylistView(LoginRequiredMixin, CreateView):
    model = Playlist
    fields = ['name', 'description', 'music']
    template_name = 'music/create_playlist.html'
    success_url = reverse_lazy('music-home')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class UpdatePlaylistView(LoginRequiredMixin, UpdateView):
    model = Playlist
    fields = ['name', 'description', 'music']
    template_name = 'music/update_playlist.html'
    success_url = reverse_lazy('music-home')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class DeletePlaylistView(LoginRequiredMixin, DeleteView):
    model = Playlist
    success_url = '/'

class PlaylistDetailView(LoginRequiredMixin, DetailView):
    model = Playlist
    template_name = 'music/playlist_detail.html'
    context_object_name = 'playlist'

    def get_queryset(self):
        return Playlist.objects.filter(owner=self.request.user)

class ArtistDetailView(DetailView):
    model = Artist
    template_name = 'music/artist_detail.html'
    context_object_name = 'artist'

class MusicDetailView(DetailView):
    model = Music
    template_name = 'music/music_detail.html'
    context_object_name = 'music'

@login_required
@require_POST
def create_album(request):
    try:
        artist = request.user.artist
    except Artist.DoesNotExist:
        return JsonResponse({"error": "Only linked artist accounts can create albums"}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    title = data.get("title")
    genre = data.get("genre")

    if not title or not genre:
        return JsonResponse({"error": "title and genre are required"}, status=400)

    album = Album.objects.create(title=title, artist=artist, genre=genre)

    return JsonResponse(
        {"message": "Album created successfully", "album_id": album.id},
        status=201
    )

def _get_artist_or_none(request):
    try:
        return request.user.artist
    except Artist.DoesNotExist:
        return None


@login_required
@require_http_methods(["DELETE"])
def delete_album(request, album_id):
    try:
        album = Album.objects.get(id=album_id)
    except Album.DoesNotExist:
        return JsonResponse({"error": "Album not found"}, status=404)

    if album.artist.user_id != request.user.id:
        return JsonResponse({"error": "You don't own this album"}, status=403)

    album.delete()
    return JsonResponse({"message": "Album deleted successfully"}, status=200)


@login_required
@require_POST
def create_song(request):
    try:
        artist = request.user.artist
    except Artist.DoesNotExist:
        return JsonResponse({"error": "Only linked artist accounts can create songs"}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    title = data.get("title")
    album_id = data.get("album_id")
    genre = data.get("genre")

    if not title or not album_id or not genre:
        return JsonResponse({"error": "title, album_id and genre are required"}, status=400)

    try:
        album = Album.objects.get(id=album_id, artist=artist)
    except Album.DoesNotExist:
        return JsonResponse({"error": "Album not found"}, status=404)

    song = Music.objects.create(title=title, artist=artist, album=album, genre=genre)

    return JsonResponse(
        {"message": "Song created successfully", "song_id": song.id},
        status=201
    )


@login_required
@require_http_methods(["DELETE"])
def delete_song(request, song_id):
    try:
        song = Music.objects.get(id=song_id)
    except Music.DoesNotExist:
        return JsonResponse({"error": "Song not found"}, status=404)

    if song.artist.user_id != request.user.id:
        return JsonResponse({"error": "You don't own this song"}, status=403)

    song.delete()
    return JsonResponse({"message": "Song deleted successfully"}, status=200)

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


from django.contrib import messages
from .forms import SongUploadForm


@login_required
def upload_song(request):
    artist = _get_artist_or_none(request)
    if artist is None:
        messages.error(request, "Only linked artist accounts can upload songs.")
        return redirect('music-home')

    if request.method == 'POST':
        form = SongUploadForm(request.POST, request.FILES, artist=artist)
        if form.is_valid():
            song = form.save(commit=False)
            song.artist = artist
            song.save()
            messages.success(request, f'"{song.title}" uploaded.')
            return redirect('publisher_dashboard')
    else:
        form = SongUploadForm(artist=artist)

    return render(request, 'music/upload_song.html', {'form': form})


@login_required
def create_album_view(request):
    artist = _get_artist_or_none(request)
    if artist is None:
        messages.error(request, "Only linked artist accounts can create albums.")
        return redirect('music-home')

    if request.method == 'POST':
        form = AlbumUploadForm(request.POST)
        if form.is_valid():
            album = form.save(commit=False)
            album.artist = artist
            album.save()
            messages.success(request, f'Album "{album.title}" created.')
            return redirect('publisher_dashboard')
    else:
        form = AlbumUploadForm()

    return render(request, 'music/create_album.html', {'form': form})


@login_required
def publisher_dashboard(request):
    artist = _get_artist_or_none(request)
    if artist is None:
        messages.error(request, "This page is for linked artist accounts only.")
        return redirect('music-home')

    context = {
        'artist': artist,
        'albums': artist.album_set.all(),
        'songs': artist.music_set.all(),
    }
    return render(request, 'music/publisher_dashboard.html', context)

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

@login_required
def follow_unfollow(request, id):
    if request.method != "POST":
        return redirect('music-home')

    artist = get_object_or_404(Artist, id=id)

    if request.user in artist.followers.all():
        artist.followers.remove(request.user)
    else:
        artist.followers.add(request.user)

    return redirect('artist-detail', pk=artist.id)
