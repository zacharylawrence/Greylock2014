from flask import Flask, jsonify
import requests

app = Flask(__name__)

# ECHONEST
ECHONEST_BASE_URL = "http://developer.echonest.com/api/v4/song/search?"
API_KEY = "api_key=J1YY9G8BLXGUET2W9"
FORMAT_TYPE = "&format=json"
RESULT_COUNT = "&results=1"
BUCKET = "&bucket=audio_summary"
SONG_MIN_HOTTTNESSS = "&song_min_hotttnesss=0.8"

# SPOTIFY
SPOTIFY_BASE_URL = "https://api.spotify.com/v1/search?"
SPOTIFY_TYPE = "&type=track"


@app.route("/v1.0/select_song/<sleepiness>")
def select_song(sleepiness):
  sleepiness = int(sleepiness)
  if (0 <= sleepiness <= 333):   # LOWEST
    min_tempo = 50
    max_tempo = 100
    min_liveness = .1
    max_liveness = .3
  if (333 < sleepiness <= 667):  # MIDDLE
    min_tempo = 101
    max_tempo = 150
    min_liveness = .4
    max_liveness = .6
  else:                          # HIGHEST
    min_tempo = 151
    max_tempo = 200
    min_liveness = .7
    max_liveness = .9

  echonest_results = echonest_request(min_tempo, max_tempo, min_liveness, max_liveness)
  spotify_results = spotify_request(str(echonest_results["response"]["songs"][0]["artist_name"]), str(echonest_results["response"]["songs"][0]["title"]))

  return format_response(echonest_results, spotify_results)

# We care about: hotttnesss(constant), tempo, danceability, energy, liveness
# TODO(zlawrence): Add: min_danceability, min_energy, min_liveness
def echonest_request(min_tempo, max_tempo, min_liveness, max_liveness):
  query_string = ECHONEST_BASE_URL + API_KEY + FORMAT_TYPE + RESULT_COUNT + SONG_MIN_HOTTTNESSS + BUCKET +\
    "&min_liveness=" + str(min_liveness) + "&max_liveness=" + str(max_liveness)

  results = requests.get(query_string).json()

  # print "DEBUG: Echonest Request = " + str(query_string)
  # print "DEBUG: Echonest Result = " + str(results)

  if (results["response"]["status"]["code"] == 0 and len(results["response"]["songs"]) > 0):
    return results
  else:
    return "ERROR"

def spotify_request(artist_name, track_name):
  query_string = SPOTIFY_BASE_URL +\
    "q=artist:\"" + artist_name + "\"" +\
    " track:\"" + track_name + "\"" +\
    SPOTIFY_TYPE

  results = requests.get(query_string).json()

  # print "DEBUG: Spotify Request = " + str(query_string)
  # print "DEBUG: Spotify Result = " + str(results)

  if (len(results["tracks"]["items"]) > 0):
    return results
  else:
    return "ERROR"

def format_response(echonest_results, spotify_results):
  if (echonest_results == "ERROR"):
    return jsonify({"status":"error"})

  response = {}
  response["status"] = "success"
  response["artist_name"] = str(echonest_results["response"]["songs"][0]["artist_name"])
  response["track_name"] = str(echonest_results["response"]["songs"][0]["title"])
  response["audio_summary"] = {}
  response["audio_summary"]["tempo"] = str(echonest_results ["response"]["songs"][0]["audio_summary"]["tempo"])
  response["audio_summary"]["danceability"] = str(echonest_results ["response"]["songs"][0]["audio_summary"]["danceability"])
  response["audio_summary"]["energy"] = str(echonest_results ["response"]["songs"][0]["audio_summary"]["energy"])
  response["audio_summary"]["liveness"] = str(echonest_results ["response"]["songs"][0]["audio_summary"]["liveness"])

  response["track_id"] = str(spotify_results["tracks"]["items"][0]["album"]["id"])
  response["album_url"] = str(spotify_results["tracks"]["items"][0]["album"]["images"][0]["url"])

  temp = {}
  temp['results'] = [response]
  return jsonify(temp)

if __name__ == "__main__":
  app.debug = True
  app.run(host='0.0.0.0')
