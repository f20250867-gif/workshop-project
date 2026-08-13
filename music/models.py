from django.contrib.auth.models import User
from django.db import models
# Create your models here.


class Artist(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    followers = models.ManyToManyField(User, related_name="following")
    # ^ links an Artist profile to a login, so they can publish songs/albums

    def __str__(self):
        return self.name


class Genre(models.TextChoices):
    POP = "POP", "Pop"
    ROCK = "ROCK", "Rock"
    HIP_HOP = "HIP_HOP", "Hip Hop"
    RAP = "RAP", "Rap"
    RNB = "RNB", "R&B"
    JAZZ = "JAZZ", "Jazz"
    BLUES = "BLUES", "Blues"
    COUNTRY = "COUNTRY", "Country"
    FOLK = "FOLK", "Folk"
    CLASSICAL = "CLASSICAL", "Classical"
    ELECTRONIC = "ELECTRONIC", "Electronic"
    HOUSE = "HOUSE", "House"
    TECHNO = "TECHNO", "Techno"
    TRANCE = "TRANCE", "Trance"
    DUBSTEP = "DUBSTEP", "Dubstep"
    DRUM_AND_BASS = "DRUM_AND_BASS", "Drum and Bass"
    REGGAE = "REGGAE", "Reggae"
    REGGAETON = "REGGAETON", "Reggaeton"
    SKA = "SKA", "Ska"
    PUNK = "PUNK", "Punk"
    METAL = "METAL", "Metal"
    HEAVY_METAL = "HEAVY_METAL", "Heavy Metal"
    DEATH_METAL = "DEATH_METAL", "Death Metal"
    METALCORE = "METALCORE", "Metalcore"
    ALTERNATIVE = "ALTERNATIVE", "Alternative"
    INDIE = "INDIE", "Indie"
    INDIE_ROCK = "INDIE_ROCK", "Indie Rock"
    INDIE_POP = "INDIE_POP", "Indie Pop"
    GRUNGE = "GRUNGE", "Grunge"
    SOUL = "SOUL", "Soul"
    FUNK = "FUNK", "Funk"
    DISCO = "DISCO", "Disco"
    GOSPEL = "GOSPEL", "Gospel"
    LATIN = "LATIN", "Latin"
    SALSA = "SALSA", "Salsa"
    BOSSA_NOVA = "BOSSA_NOVA", "Bossa Nova"
    FLAMENCO = "FLAMENCO", "Flamenco"
    WORLD = "WORLD", "World"
    AFROBEAT = "AFROBEAT", "Afrobeat"
    AMBIENT = "AMBIENT", "Ambient"
    LO_FI = "LO_FI", "Lo-Fi"
    SYNTHWAVE = "SYNTHWAVE", "Synthwave"
    K_POP = "K_POP", "K-Pop"
    J_POP = "J_POP", "J-Pop"
    BOLLYWOOD = "BOLLYWOOD", "Bollywood"
    CLASSICAL_INDIAN = "CLASSICAL_INDIAN", "Indian Classical"
    OPERA = "OPERA", "Opera"
    SOUNDTRACK = "SOUNDTRACK", "Soundtrack"
    INSTRUMENTAL = "INSTRUMENTAL", "Instrumental"
    ACOUSTIC = "ACOUSTIC", "Acoustic"
    SINGER_SONGWRITER = "SINGER_SONGWRITER", "Singer-Songwriter"
    EMO = "EMO", "Emo"
    EXPERIMENTAL = "EXPERIMENTAL", "Experimental"
    NEW_AGE = "NEW_AGE", "New Age"
    CHILDREN = "CHILDREN", "Children's Music"
    COMEDY = "COMEDY", "Comedy"
    CHRISTIAN = "CHRISTIAN", "Christian"
    HOLIDAY = "HOLIDAY", "Holiday"
    TRAP = "TRAP", "Trap"
    GRIME = "GRIME", "Grime"
    DANCEHALL = "DANCEHALL", "Dancehall"
    SWING = "SWING", "Swing"
    BLUEGRASS = "BLUEGRASS", "Bluegrass"


class Album(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    release_date = models.DateField(auto_now_add=True)
    genre = models.CharField(max_length=50, choices=Genre.choices)

    def __str__(self):
        return f"{self.title} by {self.artist}"


class Music(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    release_date = models.DateField(auto_now_add=True)
    genre = models.CharField(max_length=50, choices=Genre.choices)
    likes = models.ManyToManyField(User, related_name="liked_music")

    def __str__(self):
        return f"{self.title} by {self.artist}"


class Playlist(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="playlists")
    music = models.ManyToManyField(Music, related_name="playlists")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class RecentlyPlayed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    music = models.ForeignKey(Music, on_delete=models.CASCADE)
    played_at = models.DateTimeField(
        auto_now=True
    )  # was auto_now_add — now updates on every save

    class Meta:
        ordering = ["-played_at"]
        unique_together = (
            "user",
            "music",
        )  # replaying bumps the row instead of duplicating it
        indexes = [
            models.Index(
                fields=["user", "-played_at"]
            ),  # this table grows fast; speeds up your query
        ]

    def __str__(self):
        return f"{self.user} played {self.music}"

