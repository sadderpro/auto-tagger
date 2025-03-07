
"""

TODO: Instead of creating a function to check the status of the access token, add logic to update the access token when it's expired
TODO: modify get_access_token so it handles a request made with no connection to internet

TODO: Create logic to update access using a timestamp instead of a stupid test request

"""

import requests
import json
import os
from collections import defaultdict
from time import time
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO


#*----------------------------- STATIC AND GLOBAL VARIABLES -----------------------------

load_dotenv()

SPOTIFY_ROOT_URL = 'https://api.spotify.com/v1/'
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

access_token, token_type, token_timestamp = None, None, None



#*---------------------------- CLASS AND METHOD DECLARATION ------------------------------


class Track:
  def __init__(self, artists, title, number, disc, lyrics='unavailable'):
    self.artists = artists
    self.title = title
    self.number = number
    self.disc = disc
    self.lyrics = lyrics

# I'll work on this later, I promise
#TODO: Add an attribute that contains the number of discs for the album.
class Album:
  

  def __init__(self, identifier):
    self.ID = identifier
    self.tracklist = defaultdict(list)
    print(f'Created new album instance with ID {self.ID}')
    self.request_album()
  





  # TODO: First, let's make sure the album data is retrieved correctly

  # This function requests the album data from Spotify's API and stores it in the album instance by calling the helper method set_album_info

  # This function is not intended to be called directly, but rather, it should be called by the __init
  # method of the Album class
  def request_album(self):
    # 1. data required for the request
    global access_token, token_type
    album_link = f'https://api.spotify.com/v1/albums/{self.ID}'
    artist_link = f'{SPOTIFY_ROOT_URL}artists/'

    get_access_token()

    header = {
      'Authorization': f'{token_type} {access_token}', # AUTHORIZATION: Olivia Pierce
    }
    # 2. Making the requests
    album_response = requests.get(album_link, headers=header)

    # 3. Handling the request, first make sure the status code is OK
    if album_response.status_code == 200:
      artist_response = requests.get(f'{artist_link}{album_response.json()['artists'][0]['id']}', headers=header)
      if artist_response.status_code == 200:
        self.set_genre(artist_response)
      self.set_album_info(album_response)
    elif album_response.status_code == 401:
      print("[WARNING]: Session expired or invalid access token. Generating a new access token, try again")
      get_access_token()
    else:
      #? Not sure whether to code logic to retry a request within the function or outside. This statement will
      #? remain like this for the time being.
      print(f"[ERROR]: Failed to retrieve album data. Status code {album_response.status_code}. Retry maybe?")

# Helper method to load the tracks to the album instance
  def set_album_info(self, album_response):
    
    album_response = album_response.json()

    # Set album info that is shared by every track (title, year, cover image, etc)
    self.albumartists = [artist["name"] for artist in album_response["artists"]]
    self.title = album_response["name"]
    self.year = album_response["release_date"][:4]
    self.total_tracks = album_response["total_tracks"]
    
    # Saving album cover image as raw data
    cover_link = album_response['images'][0]['url']
    cover_link_response = requests.get(cover_link)
    # If an image was obtained, we convert its format to make sure music-tag can accept it as jpeg data
    if cover_link_response.status_code == 200:
      image = Image.open(BytesIO(cover_link_response.content))
      jpeg_buffer = BytesIO()
      image.convert("RGB").save(jpeg_buffer, format='JPEG')
      # then we pass the corrected bytes to the album's property:
      self.cover_art = jpeg_buffer.getvalue()
    else:
      self.cover_art = None
    # phew, that one part was a bit tough, at least for me lol

    # Start adding the tracklist as track objects with track specific metadata (track artists, track title, track number and disc number)
    for track_item in album_response["tracks"]["items"]:
      artists = [artist["name"] for artist in track_item["artists"]]
      # Append new item to tracklist list (duh)
      track = Track(artists, track_item["name"], track_item["track_number"], track_item["disc_number"])
      self.tracklist[track_item["disc_number"]].append(track)
    print(f"Album info successfully attached to album class with id {self.ID}")

# helper method to retrieve genre. Since genres are no longer attached to album response, it's necessary to make a new request to spotify API
  def set_genre(self, artist_response):
    if artist_response is None:
      return
    artist_response = artist_response.json()
    self.genres = '; '.join(artist_response['genres'])

# Pretty self explainatory I think
  def print_album_info(self):
    artists = ", ".join(self.albumartists)
    album_info = f"""Album information retrieved:

    Title: {self.title}
    Artists: {artists}
    Year of release: {self.year}
    genre(s): {self.genres}

Tracklist:

  """
    print(album_info)
    for disc, tracks in self.tracklist.items():
      print(f"\nDisc {disc}:\n")
      for track in tracks:
        artists = ", ".join(track.artists)
        print(f"{track.number}. {track.title}, Artist(s): {artists}")



#*--------------------------- MODULE/STATIC FUNCTIONS --------------------------


# This seems to work properly :) but it still need to optimize the way it requests token... later

# Loads an access token from a json file, if it exists, otherwise, it requests a new one
# TODO: update logic to check if the access token is expired
#! DEPRECATED: This function is no longer used, but it's kept here for reference
def load_access_token():
  # Check if the file exists
  if os.path.exists('access_token.json'):
    with open('access_token.json', 'r') as token_json:
      token_data = token_json.read()
    try:
      token_data = json.loads(token_data)
      # modify global variables according to data retrieved from access_token.json
      global access_token, token_type, token_timestamp
      access_token = token_data["access_token"]
      token_type = token_data["token_type"]
      token_timestamp = token_data["timestamp"]
      print("[green][SUCCESS][/]: access token and token type variables successfully updated")

    # In case the file it loads from is invalid or something
    except json.decoder.JSONDecodeError:
      print("[ERROR]: access_token.json does not contain valid json data. Creating a new access token...")
      get_access_token()
  else:
    print("[WARNING]: no access token has been found, now requesting a new access token")
    get_access_token()
    
    
# TODO: Add logic to update the access token when it's expired

# This function modifies the global variables access_token token_type and token_timestamp and returns the access token query as a dictionary
# ... It just works.
def get_access_token():
  
  # Constant declarations for this function
  global access_token, token_type, token_timestamp

  URL = "https://accounts.spotify.com/api/token"

  HEADER = {
    "Content-Type": "application/x-www-form-urlencoded"
  }
  DATA = {
    "grant_type": "client_credentials",
    "client_id": SPOTIFY_CLIENT_ID,
    "client_secret": SPOTIFY_CLIENT_SECRET
  }

  # First, let's make the request
  response = requests.post(URL, data=DATA, headers=HEADER)
  token_timestamp = time()

  # Honestly I don't know if anything inside this if-statement works, but we'll see
  if response.status_code == 200:
    # save the response in a json file for future use
    response = response.json()
    response["timestamp"] = token_timestamp
#   with open('access_token.json', 'w') as access_token_json:
#     json.dump(response, access_token_json)
#     print("Saved access token as access_token.json")

    # Convert response text (already in json format) to a dictionary
    access_token = response['access_token'] 
    token_type = response['token_type'] 
    print(f'Access token successfully created.')
  #handle error status code  
  else:
    print(f'Failed retrieving data. Status code: {response.status_code}')
    return None

  return response