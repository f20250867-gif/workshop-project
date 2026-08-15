import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from music.models import Album, Artist, Genre, Music, Playlist, RecentlyPlayed

FIRST_NAMES = [
    "Aiden", "Maya", "Liam", "Zoe", "Noah", "Ava", "Ethan", "Mia", "Lucas",
    "Ivy", "Owen", "Ruby", "Leo", "Nora", "Kai", "Luna", "Eli", "Stella",
    "Jax", "Willow", "Finn", "Hazel", "Milo", "Iris", "Rhys", "Sage",
    "Theo", "Wren", "Cole", "Juno",
]
LAST_NAMES = [
    "Carter", "Nguyen", "Patel", "Reyes", "Kim", "Brooks", "Fischer",
    "Morales", "Novak", "Adeyemi", "Larsson", "Okafor", "Rossi", "Haddad",
    "Petrov", "Suzuki", "Dubois", "Santos", "Klein", "Whitfield",
]
ARTIST_WORDS_A = [
    "Neon", "Velvet", "Crimson", "Electric", "Silver", "Ghost", "Golden",
    "Midnight", "Iron", "Paper", "Static", "Amber", "Broken", "Wild",
    "Hollow", "Glass", "Copper", "Distant", "Lunar", "Feral",
]
ARTIST_WORDS_B = [
    "Wolves", "Echo", "Riot", "Horizon", "Parade", "Static", "Collective",
    "Machine", "Garden", "Tide", "Circuit", "Bloom", "District", "Bones",
    "Radio", "Vessel", "Compass", "Ember", "Signal", "Orbit",
]
ALBUM_WORDS = [
    "Departures", "Afterglow", "Low Tide", "Paper Crowns", "Static Bloom",
    "Second Skin", "Faded Maps", "Night Drive", "Glass Houses", "Wildfire",
    "Slow Burn", "Open Roads", "Empty Rooms", "Loose Ends", "Northbound",
    "Sunset Static", "Quiet Riot", "Wired", "Homesick", "Aftertaste",
]
SONG_WORDS = [
    "Runaway", "Gravity", "Static", "Daylight", "Echoes", "Free Fall",
    "Paper Planes", "Wildflower", "Neon Lights", "Fade Out", "Hold On",
    "Undertow", "Skyline", "Afterparty", "Slow Dance", "Concrete",
    "Firelight", "Backroads", "Heavy Heart", "Blue Hour", "Reckless",
    "Stay Awake", "Borrowed Time", "Windows Down", "Constellations",
    "Tidal Wave", "Antidote", "Ghost Town", "Wide Awake", "Halfway Home",
]
PLAYLIST_NAMES = [
    "Late Night Drive", "Rainy Day Mix", "Workout Energy", "Chill Study",
    "Road Trip", "Sunday Morning", "Focus Flow", "Throwback Vibes",
    "Party Starters", "Heartbreak Hotel", "Golden Hour", "Deep Focus",
]

GENRES = [g[0] for g in Genre.choices]


class Command(BaseCommand):
    help = "Seed the database with a large batch of fake users, artists, albums, songs, playlists, and activity."

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=40, help="Number of regular users to create (default: 40)")
        parser.add_argument("--artists", type=int, default=20, help="Number of artist profiles to create (default: 20)")
        parser.add_argument("--password", type=str, default="password123", help="Password set on every seeded user (default: password123)")
        parser.add_argument("--flush", action="store_true", help="Delete previously seeded data (usernames/artists starting with 'seed_') before seeding")
        parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible output")

    def handle(self, *args, **options):
        if options["seed"] is not None:
            random.seed(options["seed"])

        num_users = options["users"]
        num_artists = min(options["artists"], num_users)
        password = options["password"]

        if options["flush"]:
            self.stdout.write("Flushing previously seeded data...")
            User.objects.filter(username__startswith="seed_").delete()
            self.stdout.write(self.style.WARNING("Deleted seed_ users (cascades to their artists/albums/songs/playlists)."))

        with transaction.atomic():
            users = self._create_users(num_users, password)
            artists = self._create_artists(users, num_artists)
            albums = self._create_albums(artists)
            songs = self._create_songs(artists, albums)
            self._create_follows(users, artists)
            self._create_likes(users, songs)
            playlists = self._create_playlists(users, songs)
            plays = self._create_recently_played(users, songs)

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(users)} users, {len(artists)} artists, {len(albums)} albums, "
            f"{len(songs)} songs, {len(playlists)} playlists, {plays} recently-played rows."
        ))
        self.stdout.write(f"All seeded users share the password: {password}")

    def _unique_username(self, used):
        while True:
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            username = f"seed_{first}{last}{random.randint(1, 999)}".lower()
            if username not in used:
                used.add(username)
                return username, first, last

    def _create_users(self, count, password):
        self.stdout.write(f"Creating {count} users...")
        used = set(User.objects.values_list("username", flat=True))
        users = []
        for _ in range(count):
            username, first, last = self._unique_username(used)
            user = User.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password=password,
                first_name=first,
                last_name=last,
            )
            users.append(user)
        return users

    def _create_artists(self, users, count):
        self.stdout.write(f"Creating {count} artists...")
        candidates = random.sample(users, count)
        used_names = set(Artist.objects.values_list("name", flat=True))
        artists = []
        for user in candidates:
            while True:
                name = f"{random.choice(ARTIST_WORDS_A)} {random.choice(ARTIST_WORDS_B)}"
                if name not in used_names:
                    used_names.add(name)
                    break
            artist = Artist.objects.create(name=name, user=user)
            artists.append(artist)
        return artists

    def _create_albums(self, artists):
        self.stdout.write("Creating albums...")
        albums = []
        for artist in artists:
            for _ in range(random.randint(1, 4)):
                title = f"{random.choice(ALBUM_WORDS)} {random.choice(ALBUM_WORDS)}" if random.random() < 0.2 else random.choice(ALBUM_WORDS)
                album = Album.objects.create(
                    title=title,
                    artist=artist,
                    genre=random.choice(GENRES),
                )
                albums.append(album)
        return albums

    def _create_songs(self, artists, albums):
        self.stdout.write("Creating songs...")
        songs = []
        for album in albums:
            for _ in range(random.randint(3, 9)):
                title = random.choice(SONG_WORDS)
                song = Music.objects.create(
                    title=title,
                    artist=album.artist,
                    album=album,
                    genre=random.choice(GENRES),
                )
                songs.append(song)
        return songs

    def _create_follows(self, users, artists):
        self.stdout.write("Creating follower relationships...")
        for artist in artists:
            follower_pool = [u for u in users if u != artist.user]
            followers = random.sample(follower_pool, k=min(len(follower_pool), random.randint(0, 15)))
            artist.followers.add(*followers)

    def _create_likes(self, users, songs):
        self.stdout.write("Creating song likes...")
        for song in songs:
            likers = random.sample(users, k=min(len(users), random.randint(0, 10)))
            song.likes.add(*likers)

    def _create_playlists(self, users, songs):
        self.stdout.write("Creating playlists...")
        playlists = []
        for user in users:
            if random.random() < 0.6:
                continue
            for _ in range(random.randint(1, 2)):
                playlist = Playlist.objects.create(
                    name=random.choice(PLAYLIST_NAMES),
                    description=random.choice([
                        "", "", "made for late nights.", "songs on repeat lately.",
                        "curated by yours truly.", "a work in progress.",
                    ]),
                    owner=user,
                )
                track_pool = random.sample(songs, k=min(len(songs), random.randint(3, 15)))
                playlist.music.add(*track_pool)
                playlists.append(playlist)
        return playlists

    def _create_recently_played(self, users, songs):
        self.stdout.write("Creating recently-played history...")
        count = 0
        for user in users:
            plays = random.sample(songs, k=min(len(songs), random.randint(0, 20)))
            for song in plays:
                RecentlyPlayed.objects.get_or_create(user=user, music=song)
                count += 1
        return count
