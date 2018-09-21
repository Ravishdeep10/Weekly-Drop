from django.urls import path
from .views import AlbumView


urlpatterns = [
    path("", AlbumView.as_view(template_name="pages/home.html"), name="home"),
]
