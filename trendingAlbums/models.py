# Create your models here.
import praw
import spotipy
import datetime as dt
import pandas as pd

from spotipy.oauth2 import SpotifyClientCredentials

from django.db import models
from django.utils import timezone

from config.settings.base import get_secret




class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides selfupdating
    ``created`` and ``modified`` fields.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Model for a reddit post
class redditPost(TimeStampedModel):
    """
    Basic Model for a Reddit Post
    """
    title = models.CharField(max_length=200)
    score = models.IntegerField()
    post_id = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    comms_numm = models.IntegerField()
    timestamp = models.DateTimeField()

class spotifyAlbum(TimeStampedModel):
    artist = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    release = models.DateTimeField()
    url = models.CharField(max_length=200)
    uri = models.CharField(max_length=200)
    image_url = models.CharField(max_length=200)
    album_type = models.CharField(max_length=200)

    def get_url(self):
        return self.url




### Functions relating to redditPost

def getRedditObjects():
    if readyToUpdate():
        clearDB()
        topics_data = filterFreshOnly(getRedditPosts())

        for index, row in topics_data.iterrows():
            redditPost(title=row['title'], score=row['score'], post_id=row['id'], url=row['url'],
                       comms_numm=row['comms_num'], timestamp=row['timestamp']).save()

    return redditPost.objects.all()

def clearDB():
    if redditPost.objects.count() == 0:
        return
    else:
        redditPost.objects.all().delete()

def filterFreshOnly(topics_data):
    mask = [checkFresh(x) for x in topics_data.title]
    return topics_data[mask]

def checkFresh(title):
    return checkFreshSingle(title) or checkFreshEP(title) or checkFreshAlbum(title)

def checkFreshSingle(title):
    return title[:7] == "[FRESH]"

def checkFreshEP(title):
    return title[:10] == "[FRESH EP]"

def checkFreshAlbum(title):
    return title[:13] == "[FRESH ALBUM]"


def getRedditPosts():
   '''
   Get the hot posts on the hiphopheads subreddit
   '''

   reddit = praw.Reddit(client_id=get_secret("REDDIT_CLIENT_ID"), client_secret= get_secret("REDDIT_SECRET_KEY"),
                             redirect_uri=get_secret("REDIRECT_URI"), user_agent=get_secret("REDDIT_USER_AGENT"))

   subreddit = reddit.subreddit('hiphopheads')

   topics_dict = {"title": [], "score": [], "id": [], "url": [], "comms_num": [], "created": []}

   hot_subreddit = subreddit.hot(limit=50)

   for submission in hot_subreddit:
       topics_dict["title"].append(submission.title)
       topics_dict["score"].append(submission.score)
       topics_dict["id"].append(submission.id)
       topics_dict["url"].append(submission.url)
       topics_dict["comms_num"].append(submission.num_comments)
       topics_dict["created"].append(submission.created)


   return fixDates(pd.DataFrame(topics_dict))


def get_date(created):
    return dt.datetime.fromtimestamp(created)

def fixDates(topics_data):
    _timestamp = topics_data["created"].apply(get_date)
    topics_data = topics_data.assign(timestamp=_timestamp)
    return topics_data


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

def readyToUpdate():
    if redditPost.objects.count() == 0:
        return True

    numPastPosts = redditPost.objects.count()

    latestPost = redditPost.objects.order_by('timestamp')[numPastPosts - 1]

    latestDateTime = utc_to_local(getattr(latestPost, 'timestamp'))

    nextThursday = getNextThursday(latestDateTime)

    currentDateTime = utc_to_local(timezone.now())

    return currentDateTime > nextThursday


def getNextThursday(latest_date):

    #If we are on the Thursday after the last Update
    if latest_date.weekday() == 3:
        latest_date += dt.timedelta(days=1)

    while latest_date.weekday() != 3:
        latest_date += dt.timedelta(days=1)

    latest_date = latest_date.replace(hour=21, minute=15, second=0, microsecond=0)

    return latest_date



def getDateTime(str_time):
    return pd.to_datetime(str_time).date()

def checkCorrectAlbum(album, title, spotifyclient):
    album_spotify = spotifyclient.search(q='album:' + title, type='album')['albums']

    if album_spotify['total'] == 0:
        return False

    #print("Latest Album Search: ", album_spotify['items'][0])
    #album_id_1 = album_spotify['items'][0]['artists'][0]['id']

    #album_id_2 = album['artists'][0]['id']

    return getDateTime(album['release_date']).weekday() == 4


def getSpotifyAlbums():
    trending = getRedditObjects()
    spotifyAlbum.objects.all().delete()

    for album in trending:
        convertRedditSpotify(album)


def convertRedditSpotify(album):

    client_credentials_manager = SpotifyClientCredentials(client_id=get_secret("SPOTIFY_CLIENT_ID"),
                                                          client_secret=get_secret("SPOTIFY_CLIENT_SECRET"))
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    name = getattr(album, 'title')

    if checkFreshSingle(name):
        seperate = name[8:].split(' - ')
        type = 'single'

    elif checkFreshEP(name):
        seperate = name[11:].split(' - ')
        type= 'single'
    elif checkFreshAlbum(name):
        seperate = name[14:].split(' - ')
        type = 'album'

    if len(seperate) != 2:
        return
    [artist, title] = seperate

    artist_spotify = spotify.search(q='artist:' + artist, type='artist')['artists']

    if artist_spotify['total'] == 0:
        return

    id = artist_spotify['items'][0]['id']

    artist_albums = spotify.artist_albums(id, album_type=type)['items']

    #Check if the artist has any albums at all
    if artist_albums == []:
        return

    latest_album = artist_albums[0]

    if checkCorrectAlbum(latest_album, title.strip(), spotify):
        url = "https://open.spotify.com/embed/album/" + latest_album['uri'].split(':')[-1]
        spotifyAlbum(artist=artist, name=latest_album['name'], release=getDateTime(latest_album['release_date']),
                     url=url, uri=latest_album['uri'],
                     image_url=latest_album['images'][1]['url'], album_type=latest_album['album_type']).save()

