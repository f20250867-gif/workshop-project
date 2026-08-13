from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from .models import Artist, Music, Album
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

@csrf_exempt
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

@csrf_exempt   
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

@csrf_exempt   
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

@csrf_exempt   
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