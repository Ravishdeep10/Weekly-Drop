from django.contrib import admin
from .models import redditPost, spotifyAlbum

# Register your models here.
admin.site.register(redditPost)
admin.site.register(spotifyAlbum)

