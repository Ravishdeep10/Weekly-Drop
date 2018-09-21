from django.utils import timezone
from django.views.generic.list import ListView

from .models import getSpotifyAlbums, spotifyAlbum, readyToUpdate

class AlbumView(ListView):

    model = spotifyAlbum

    def get_context_data(self, **kwargs):
        if readyToUpdate():
            getSpotifyAlbums()
        context_data = super(AlbumView, self).get_context_data(**kwargs)
        context_data['singles'] = spotifyAlbum.objects.filter(album_type='single')
        context_data['albums'] = spotifyAlbum.objects.filter(album_type='album')
        return context_data

