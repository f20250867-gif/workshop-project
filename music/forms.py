from django import forms
from .models import Music, Album

class AlbumUploadForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'genre']

class SongUploadForm(forms.ModelForm):
    class Meta:
        model = Music
        fields = ['title', 'album', 'genre', 'audio']

    def __init__(self, *args, artist=None, **kwargs):
        super().__init__(*args, **kwargs)
        if artist is not None:
            self.fields['album'].queryset = Album.objects.filter(artist=artist)
