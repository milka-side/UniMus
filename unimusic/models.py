from django.db import models
from django.contrib.auth.models import User

class Song(models.Model):
    """Represents an individual musical track."""
    title = models.CharField(max_length=255, verbose_name="Song Title")
    artist = models.CharField(max_length=255, verbose_name="Artist")
    album = models.CharField(max_length=255, blank=True, verbose_name="Album")
    year = models.IntegerField(blank=True, null=True, verbose_name="Year")
    link = models.URLField(max_length=500, blank=True, verbose_name="Link")
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='added_songs')

    def __str__(self):
        return f"{self.title} — {self.artist}"

class Playlist(models.Model):
    """Represents a collection of songs curated by a user."""
    name = models.CharField(max_length=255, verbose_name="Playlist Name")
    description = models.TextField(blank=True, verbose_name="Description")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    songs = models.ManyToManyField(Song, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True, verbose_name="Public Access")
    likes = models.ManyToManyField(User, related_name='liked_playlists', blank=True)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"{self.name}"
