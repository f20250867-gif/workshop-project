from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Artist(models.Model):
    name = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    # ^ links an Artist profile to a login, so they can publish songs/albums

    def __str__(self):
        return self.name

class Album(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    release_date = models.DateField()
    genre = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.title} by {self.artist}"

class Music(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    release_date = models.DateField()
    genre = models.CharField(max_length=50)
    like_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} by {self.artist}"

class Playlist(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')  
    music = models.ManyToManyField(Music, related_name='playlists')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    music = models.ForeignKey(Music, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'music')  # one like per user per song

    def __str__(self):
        return f"{self.user} likes {self.music}"

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'artist')

    def __str__(self):
        return f"{self.user} follows {self.artist}"

class RecentlyPlayed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    music = models.ForeignKey(Music, on_delete=models.CASCADE)
    played_at = models.DateTimeField(auto_now=True)  # was auto_now_add — now updates on every save

    class Meta:
        ordering = ['-played_at']
        unique_together = ('user', 'music')  # replaying bumps the row instead of duplicating it
        indexes = [
            models.Index(fields=['user', '-played_at']),  # this table grows fast; speeds up your query
        ]

    def __str__(self):
        return f"{self.user} played {self.music}"