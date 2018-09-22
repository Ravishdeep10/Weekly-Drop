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
    '''
    Basic Model for a Spotify Album
    '''
    artist = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    release = models.DateTimeField()
    url = models.CharField(max_length=200)
    uri = models.CharField(max_length=200)
    image_url = models.CharField(max_length=200)
    album_type = models.CharField(max_length=200)




### Functions relating to redditPost

def getRedditObjects():
    '''
    This function checks whether the database is ready to update with new
        reddit recommendations and then clears the prexisting data and fills
        it with data retrieved about trending albums from reddit

    :return: Queryset of redditPost objects just created
    '''
    if readyToUpdate():
        clearDB()
        topics_data = filterFreshOnly(getRedditPosts())

        for index, row in topics_data.iterrows():
            redditPost(title=row['title'], score=row['score'], post_id=row['id'], url=row['url'],
                       comms_numm=row['comms_num'], timestamp=row['timestamp']).save()

    return redditPost.objects.all()

def clearDB():
    '''
    This function clears the database of redditPost objects if any are there
    '''
    if redditPost.objects.count() == 0:
        return
    else:
        redditPost.objects.all().delete()

def filterFreshOnly(topics_data):
    '''
    :param topics_data (pd.Dataframe): The dataframe containg info about the hottest
        posts from the hiphopheads subreddit
    :return: A mask of topic_data which will only contain posts about new releases
    '''
    mask = [checkFresh(x) for x in topics_data.title]
    return topics_data[mask]

def checkFresh(title):
    '''
    The title of reddit posts that infer a new album is released has
        a certain tags in the post's title. This function checks if the
        post identifies a new release through the title
    :param title (string): title of the reddit post
    :return: (bool): check if the reddit post is about a new release
    '''
    return checkFreshSingle(title) or checkFreshEP(title) or checkFreshAlbum(title)

def checkFreshSingle(title):
    '''
    :param title (string): title of the reddit post
    :return(bool): check if the reddit post is about a new single release
    '''
    return title[:7] == "[FRESH]"

def checkFreshEP(title):
    '''
    :param title (string): title of the reddit post
    :return(bool): check if the reddit post is about a new EP release
    '''
    return title[:10] == "[FRESH EP]"

def checkFreshAlbum(title):
    '''
    :param title (string): title of the reddit post
    :return(bool): check if the reddit post is about a new Album release
    '''
    return title[:13] == "[FRESH ALBUM]"

def get_date(created):
    '''
    :param created (string): A string representing the date when reddit post was created
    :return (datetime): The corresponding datetime format for date
    '''
    return dt.datetime.fromtimestamp(created)

def fixDates(topics_data):
    '''
    This function gets the created column from topics_data and creates a timestamp
        column that provides the post's date created in a human readable format.
    :param topics_data (pd.Dataframe): The dataframe containg info about the hottest
        posts from the hiphopheads subreddit
    :return: A copy of topics data containg the new timestamp column
    '''
    timestamp = topics_data["created"].apply(get_date)
    topics_data = topics_data.assign(timestamp=timestamp)
    return topics_data



def utc_to_local(utc_dt):
    '''
    Converts a datetime object that in utc timezone to local timezone
    '''
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

def readyToUpdate():
    '''
    This function checks whether it is ready to update due to new releases.
        It checks the current redditPosts and checks the date the lates one was
        created at. Then a new datetime nexThursday is created which corresponds
        to the next coming Thursday after the redditPost was created. If the
        current time is later than nextThiursday that means the newest releases
        are out.
    '''
    if redditPost.objects.count() == 0:
        return True

    numPastPosts = redditPost.objects.count()

    latestPost = redditPost.objects.order_by('timestamp')[numPastPosts - 1]

    latestDateTime = utc_to_local(getattr(latestPost, 'timestamp'))

    nextThursday = getNextThursday(latestDateTime)

    currentDateTime = utc_to_local(timezone.now())

    return currentDateTime > nextThursday


def getNextThursday(latest_date):
    '''
    :param latest_date: The datetime corresponding to the date the latest
        redditPost was created on
    :return (datetime): The datetime object corresponding to the next
        Thursday afte latest_date
    '''

    #If we are on the Thursday after the last Update
    if latest_date.weekday() == 3:
        latest_date += dt.timedelta(days=1)

    while latest_date.weekday() != 3:
        latest_date += dt.timedelta(days=1)

    latest_date = latest_date.replace(hour=21, minute=15, second=0, microsecond=0)

    return latest_date



def getRedditPosts():
   '''
    This function uses a praw reddit wrapper in order to use the Reddit Api. The wrapper
        created checks the hiphopheads subreddit and gets the hittest 50 posts. Each reddit post's
        characteristics that are transferrable to redditPost are put in a dictionary. The dictionary
        then gets converted to a pandas Dataframe object
   :return (pd.DataFrame): A dataframe containg info about the reddit posts from r/hiphopheads
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


### Functions relating to spotifyAlbum


def getDateTime(str_time):
    '''
    :param str_time (string): A date represented in yyyy-mm-dd format
    :return (datetime): The corresponding datetime object for str_time
    '''
    return pd.to_datetime(str_time).date()


def getSpotifyAlbums():
    '''
    This function retrieves the newest Spotify releases based on what is
        trending on the hiphopheads subreddit. The redditPosts are retrieved
        and the current SpotifyAlbums are deleted from the database. Then for
        every redditPost object it is converted to a spotifyAlbum object.
    '''
    trending = getRedditObjects()
    spotifyAlbum.objects.all().delete()

    for album in trending:
        convertRedditSpotify(album)


def convertRedditSpotify(album):
    '''
    This function uses the Spotify Web Api through the spotipy python wrapper. A spotify
        client is initilized and we extract the artist and album names from the post's
        title. The client is then used to search for the artist and retrieves the latest
        release. It then checks if it is the same release the redditPost corresponds to
        and if so a corresponding spotifyAlbum is initialized in the database

    :param album (redditPost): The redditPost corresponding to an artist's new release
    :return:
    '''
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
        # The artist search was a failure
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


def checkCorrectAlbum(album, title, spotifyclient):
    '''
    This function is a basic way to check if an album from the redditPost
        object is actually on Spotify. Looking for a better process to
        implement this check.

    For now we take the lates album from the artist that was found in
        convertRedditSpotify() and the album title from the redditPost. They
        don;t have to the exact same titles to be reffering to the same album
        We just search for the album using the redditPost title and see if
        nothing pops up. We then check if the title retrieved from spotify
        was released on the certain weekday when they should be released.

    '''
    album_spotify = spotifyclient.search(q='album:' + title, type='album')['albums']

    if album_spotify['total'] == 0:
        return False

    return getDateTime(album['release_date']).weekday() == 4
