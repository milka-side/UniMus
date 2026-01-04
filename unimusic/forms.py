"""
Django forms for UniMus project.
"""

from django import forms
from .models import Song, Playlist

class SongForm(forms.ModelForm):
    """
    A form for creating and updating Song instances.
    """
    class Meta:
        """Special class Meta"""
        model = Song
        fields = ['title', 'artist', 'album', 'year', 'link']
        widgets = {
            'link': forms.URLInput(),
        }

class PlaylistForm(forms.ModelForm):
    """
    A form for creating and updating Playlist instances.
    """
    songs = forms.ModelMultipleChoiceField(
        queryset=Song.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select Songs"
    )

    class Meta:
        """Special class Meta"""
        model = Playlist
        fields = ['name', 'description', 'is_public', 'songs']
        labels = {
            'name': 'Playlist Name',
            'description': 'Description',
            'is_public': 'Make this playlist public',
        }
