import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.oauth2 as oauth2
import re

import requests
import inspect
import pprint
from difflib import SequenceMatcher
from constants import *


class Spotify_client():
    '''
    This class manages Spotify authorization and handles API requests
    '''
    
    def __init__(self):
        
        self.auth_manager = SpotifyClientCredentials(
            client_id = CLIENT_ID,
            client_secret = CLIENT_SECRET
        )
        self.token = self.auth_manager.get_access_token()
        self.spotify = spotipy.Spotify(auth=self.token, client_credentials_manager=self.auth_manager, requests_timeout=2)

    
    def search_for_album(self, album_name, artists):
        album_name = remove_punct(str(album_name).lower())
        search_artists = []
        for a in artists:
            search_artists.append(remove_punct(str(a).lower()))
        artists = search_artists
        
        query = 'album:' + album_name
        result = self.spotify.search(q=query, type='album')
        albums_list = result['albums']['items']
        
        top_match = None
        top_ratio = 0
        for album in albums_list:
            for a1 in artists:
                for a2 in album['artists']:
                    a2_name = remove_punct(a2['name'].lower())
                    match_ratio = SequenceMatcher(a=a1, b=a2_name).ratio()
                    if a1 == a2_name or a1 in a2_name or a2_name in a1:
                        #successful search
                        return 0, album
                    elif len(albums_list) == 1:
                        #successful search
                        return 0, album
                    elif match_ratio > top_ratio:
                        top_ratio = match_ratio
                        top_match = album
        
        if top_match is not None:
            names = [top_match['artists'][i]['name'] for i in range(len(top_match['artists']))]
            #successful search
            if top_ratio > 0.5:
                return 0, top_match
            #flagged search
            else:
                flag, second_check = self.second_check(album_name, artists, top_match)
                return flag, second_check
        else:
            #failed search
            return -2, None
    
    def second_check(self, album_name, artists, guess):
        '''
        album name and artists shoudl already be corrected (lowercase w/ no punctuation) when passed to 
        this method
        '''
        query = 'album:' + album_name + ' artist:' + artists[0]
        result = self.spotify.search(q=query, type='album')
        if result:
            for alb in result['albums']['items']:
                res_artists = [i['name'].lower() for i in alb['artists']]
                for a1 in res_artists:
                    for a2 in artists:
                        if album_name in alb['name'].lower() and a2 in a1:
                            return 0, alb
        return -1, guess
        
        
def remove_punct(s):
    return re.sub(r'[^\w\s]', ' ', s) 
    
        

    
         