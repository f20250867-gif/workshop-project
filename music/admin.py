from django.contrib import admin

from .models import Album, Artist, Music, Playlist, RecentlyPlayed

# Register your models here.

# Register your models here.
admin.site.register(Music)
admin.site.register(Album)
admin.site.register(Artist)
admin.site.register(Playlist)
@admin.register(RecentlyPlayed)
class RecentlyPlayedAdmin(admin.ModelAdmin):
    list_display = ("user", "music", "played_at")
