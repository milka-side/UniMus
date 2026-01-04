"""
Django urls for UniMus project.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.log_in, name='login'),
    path('logout/', views.log_out, name='logout'),
    path('', views.home, name='home'),
    path('add-song/', views.add_song, name='add_song'),
    path('create-playlist/', views.create_playlist, name='create_playlist'),
    path('playlist/<int:pk>/', views.view_playlist, name='view_playlist'),
    path('playlist/<int:pk>/edit/', views.edit_playlist, name='edit_playlist'),
    path('playlist/<int:pk>/delete/', views.delete_playlist, name='delete_playlist'),
    path('songs/', views.song_list, name='song_list'),
    path('song/<int:pk>/delete/', views.delete_song, name='delete_song'),
    path('search/', views.search, name='search'),
]
