import spotify_handler as spotify
import argparse
import music_tag
import subprocess
import os



if __name__ == '__main__':
  
  # Initializing the parser
  parser = argparse.ArgumentParser(description="Parse album_id and path (optional)")
  parser.add_argument("album_id", help="The Spotify album id, you know how to get it.")
  parser.add_argument("-p", "--path", default=os.getcwd())
  

  args = parser.parse_args()

  # Initializing the album
  album = spotify.Album(args.album_id)

  # A list with the absolute routes for each file in the folder
  track_files = [os.path.join(args.path, f) for f in os.listdir(args.path) if os.path.isfile(os.path.join(args.path, f))]
  if len(track_files) == album.total_tracks:
    print("it seems you're in the right folder. Applying tags now...")
    count = 0
    for disc, tracks in album.tracklist.items():
      for track in tracks:
        track_file = music_tag.load_file(track_files[count])
        track_file["tracktitle"] = track.title
        track_file["album"] = album.title
        track_file["albumartist"] = ", ".join(album.albumartists)
        track_file["artist"] = ", ".join(track.artists)
        track_file["discnumber"] = disc
        track_file["tracknumber"] = track.number
        track_file["year"] = album.year
        track_file.save()
        count += 1

  else:
    print("it looks like you're not in the right directory... check the directory you're working on and try again :)")


  

  