from track import Track
from spotify_client import Spotify_client
from ipypb import track as pb
import pandas as pd

class Album():
    '''
    This class stores data about an album and all the songs in the album as well as summary statistics of said songs
    '''
    
    def __init__(self, raw_album, client):
        '''
        Initialization of an Album:
        1. Sets basic variables
        2. Initializes Songs in the album
        3. Gathers audio features from each song
        4. Creates summary statistics of track analyses and features
        '''
        #step 1
        self.name = raw_album['name']
        self.id = raw_album['id']
        self.score = raw_album['score']
        self.year = raw_album['release_date'][:4]
        self.track_count = raw_album['total_tracks']
        self.artists = [(a['name'],a['id']) for a in raw_album['artists']]
        self.client = client
        self.tracks = []
        
        #step 2
        self.get_tracks()
        self.get_duration()
        
        #step 3
        self.get_features()
        
        #step 4
        #self.summarize()
        
    def get_tracks(self):
        '''
        This method initializes all the Songs in the album and adds them to this class's song list
        '''
        raw_tracks = self.client.spotify.album_tracks(album_id=self.id)
        for raw_track in pb(raw_tracks['items'], label=self.name + " by " + self.artists[0][0]):
            self.tracks.append(Track(raw_track,self.client, self.id))
            
    def get_features(self):
        '''
        This method gathers the audio features of all tracks and adds the features to each Song class. This is done in this class to reduce the overall number of API calls.
        '''
        track_features = self.client.spotify.audio_features(tracks=[t.id for t in self.tracks ])
        for track, features in zip(self.tracks, track_features):
            track.set_features(features)
            

    def summarize(self):
        '''
        This method generates the whole Album's summary stats based on the Album's tracks' summary stats
        '''
        #Collect summary statistics of song features and analysis
        self.dataframe()
        summary = self.df.describe()
        summary.drop(labels=['count','min','max','25%','75%'], axis='index', inplace=True)
        summary = summary.values.flatten()
        
        #Collect basic song info
        basic = [self.id, self.name, self.score, self.artists[0][0], self.year, self.track_count, self.duration]
        basic.extend(summary)
        
        self.summary = basic
        
        
    def dataframe(self):
        '''
        This method returns a pandas DataFrame representation of this Album's songs and their respective data
        '''
        cols = ['name', 'id', '# artists', 'artist', 'danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'duration_ms', 'duration', 'end_of_fade_in', 'start_of_fade_out', 'loudness', 'tempo', 'tempo_confidence', 'time_signature', 'time_signature_confidence', 'key', 'key_confidence', 'mode', 'mode_confidence']
        data = [t.to_list() for t in self.tracks]
        self.df = pd.DataFrame(data, columns = cols)
        
    def get_duration(self):
        '''
        This method calculates the total duration of the album in seconds
        '''
        duration = 0
        for track in self.tracks:
            duration = duration + track.duration
        self.duration = duration
        
    def to_psql(self):
        values = (self.id, self.name, self.artists[0][1], self.score, self.year)
        return values;
    
    def artist_psql(self):
        return (self.artists[0][1], self.artists[0][0])
        