"""
Django views for the UniMusic project.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import models
from .models import Playlist, Song
from .forms import SongForm, PlaylistForm

def register(request):
    """
    Handles new user registration.
    On POST: Validates the form, creates a user, logs them in, and redirects to home.
    On GET: Displays an empty registration form.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'unimusic/register.html', {'form': form})

def log_in(request):
    """
    Handles user login.
    On POST: Authenticates credentials and starts a session.
    On GET: Displays the login form.
    """
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'unimusic/login.html', {'form': form})

def log_out(request):
    """Logs out the user and redirects to the login page."""
    logout(request)
    return redirect('login')

@login_required
def home(request):
    """
    Displays the user dashboard.
    Calculates statistics (total songs/playlists, favorite artist)
    and lists the user's playlists with pagination.
    """
    user = request.user
    total_playlists = Playlist.objects.filter(owner=user).count()
    total_songs = Song.objects.filter(added_by=user).count()

    favorite_artist = Song.objects.filter(added_by=user) \
        .values('artist') \
        .annotate(count=models.Count('artist')) \
        .order_by('-count').first()

    favorite_artist_name = favorite_artist['artist'] if favorite_artist else "No songs yet 💕"

    my_playlists = Playlist.objects.filter(owner=user).order_by('-created_at')
    paginator = Paginator(my_playlists, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'unimusic/home.html', {
        'page_obj': page_obj,
        'total_playlists': total_playlists,
        'total_songs': total_songs,
        'favorite_artist': favorite_artist_name,
    })

@login_required
def add_song(request):
    """Allows authenticated users to add a new song with a link."""
    if request.method == 'POST':
        form = SongForm(request.POST)
        if form.is_valid():
            song = form.save(commit=False)
            song.added_by = request.user
            song.save()
            return redirect('home')
    else:
        form = SongForm()
    return render(request, 'unimusic/add_song.html', {'form': form})

@login_required
def create_playlist(request):
    """Handles creation of a new playlist including many-to-many song selection."""
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.owner = request.user
            playlist.save()
            form.save_m2m()
            return redirect('home')
    else:
        form = PlaylistForm()
    return render(request, 'unimusic/create_playlist.html', {'form': form})

@login_required
def view_playlist(request, pk):
    """Displays playlist. Accessible to guests if public."""
    playlist = get_object_or_404(Playlist, pk=pk)

    if not playlist.is_public and playlist.owner != request.user:
        raise PermissionDenied("This playlist is private 🔒")

    return render(request, 'unimusic/view_playlist.html', {
        'playlist': playlist,
        'is_owner': request.user == playlist.owner
    })

@login_required
def edit_playlist(request, pk):
    """Updates an existing playlist's information and song list."""
    playlist = get_object_or_404(Playlist, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = PlaylistForm(request.POST, instance=playlist)
        if form.is_valid():
            form.save()
            return redirect('view_playlist', pk=pk)
    else:
        form = PlaylistForm(instance=playlist)
    return render(request, 'unimusic/edit_playlist.html', {'form': form, 'playlist': playlist})

@login_required
def delete_playlist(request, pk):
    """Deletes a specific playlist after verifying ownership."""
    playlist = get_object_or_404(Playlist, pk=pk, owner=request.user)
    playlist.delete()
    return redirect('home')

@login_required
def song_list(request):
    """Lists all songs added by the user with pagination (10 songs per page)."""
    songs = Song.objects.filter(added_by=request.user).order_by('-id')
    paginator = Paginator(songs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'unimusic/song_list.html', {'page_obj': page_obj})

@login_required
def delete_song(request, pk):
    """Removes a song from the user's library."""
    song = get_object_or_404(Song, pk=pk, added_by=request.user)
    song.delete()
    return redirect('song_list')

@login_required
def search(request):
    """
    Search engine for playlists and songs.
    Filters by title, artist, album, name, or description using the 'q' query parameter.
    """
    query = request.GET.get('q', '').strip()

    results_playlists = Playlist.objects.filter(owner=request.user)
    results_songs = Song.objects.filter(added_by=request.user)

    if query:
        # Search playlists by name, description, or content (song titles/artists)
        results_playlists = results_playlists.filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(songs__title__icontains=query) |
            models.Q(songs__artist__icontains=query)
        ).distinct()

        # Search songs by title, artist, or album
        results_songs = results_songs.filter(
            models.Q(title__icontains=query) |
            models.Q(artist__icontains=query) |
            models.Q(album__icontains=query)
        ).distinct()

    return render(request, 'unimusic/search.html', {
        'query': query,
        'playlists': results_playlists,
        'songs': results_songs,
    })
