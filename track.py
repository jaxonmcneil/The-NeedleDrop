
class Track:
    '''
    This class stores basic data about a track as well it's audio analysis and and audio features pulled from the Spotify API
    '''
    
    def __init__(self, raw_track, client, album_id):
        '''
        Initialization of a Track:
        1. Sets basic variables
        2. Pulls audio analysis from Spotify API
        '''
        #step 1
        self.name = raw_track['name']
        self.id = raw_track['id']
        self.album_id = album_id
        self.artists = [(a['name'],a['id']) for a in raw_track['artists']]
        self.client = client
        
        #step 2
        self.get_audio_analysis()
        
    def set_features(self,features):
        '''
        This method sets song features pulled from Spotify API
        
        #below line is the columns to remove in order to summarize albums 
        remove = ['type', 'id', 'uri', 'track_href', 'analysis_url', 'key', 'tempo', 'time_signature', 'loudness', 'mode']
        '''
        remove = ['type', 'id', 'uri', 'track_href', 'analysis_url']
        for r in remove:
            del features[r]
        self.features = features
        
    def get_audio_analysis(self):
        '''
        This method pulls relevant song analysis data from the Spotify API
        Note: API call is wrapped in a while True loop because this API call randomly times out
        '''
        while True:
            try:
                analysis = self.client.spotify.audio_analysis(track_id=self.id)['track']
                break
            except Exception as e:
                pass
                continue
        remove = ['codestring', 'echoprintstring', 'echoprint_version', 'synchstring', 'synch_version', 'rhythmstring', 'rhythm_version', 'num_samples', 'sample_md5', 'offset_seconds', 'window_seconds', 'analysis_sample_rate', 'analysis_channels', 'code_version']
        for r in remove:
            del analysis[r]
        self.analysis = analysis
        self.duration = analysis['duration']
        
    def to_list(self):
        '''
        This method returns a list representation of the class's data
        '''
        basic_info = [self.name, self.id, len(self.artists), self.artists[0][0]]
        feature_list = []
        for key in self.features:
            feature_list.append(self.features[key])
    
        analysis_list = []
        for key in self.analysis:
            analysis_list.append(self.analysis[key])
                
        my_list = []
        my_list.extend(basic_info)
        my_list.extend(feature_list)
        my_list.extend(analysis_list)

        return my_list
    
    def to_psql(self):
        values = [self.id, self.album_id, self.name]
        for key in self.features:
            values.append(self.features[key])
        return values