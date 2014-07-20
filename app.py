from flask import Flask, jsonify
import requests

app = Flask(__name__)

# ECHONEST
ECHONEST_BASE_URL = "http://developer.echonest.com/api/v4/song/search?"
API_KEY = "api_key=J1YY9G8BLXGUET2W9"
FORMAT_TYPE = "&format=json"
RESULT_COUNT = "&results=1"
BUCKET = "&bucket=audio_summary&bucket=song_hotttnesss"
SONG_MIN_HOTTTNESSS = "&song_min_hotttnesss=0.6"
ARTIST_START_YEAR_AFTER = "&artist_start_year_after=1980"

# SPOTIFY
SPOTIFY_BASE_URL = "https://api.spotify.com/v1/search?"
SPOTIFY_TYPE = "&type=track"

low_iteration = 0
middle_iteration = 0
high_iteration = 0

@app.route("/v1.0/select_song/<sleepiness>")
def select_song(sleepiness):
  global low_iteration
  global middle_iteration
  global high_iteration

  sleepiness = int(sleepiness)
  if (0 <= sleepiness <= 333):     # LOWEST
    min_tempo = 5
    max_tempo = 108  # 76
    min_liveness = 0
    max_liveness = .3
    iteration = low_iteration
    low_iteration += 1
  elif (333 < sleepiness <= 667):  # MIDDLE
    min_tempo = 76
    max_tempo = 168
    min_liveness = .3
    max_liveness = .7
    iteration = middle_iteration
    middle_iteration += 1
  else:                            # HIGHEST
    min_tempo = 121 # 168
    max_tempo = 500
    min_liveness = .7
    max_liveness = 1
    iteration = high_iteration
    high_iteration += 1

  echonest_results = echonest_request(iteration, min_tempo, max_tempo, min_liveness, max_liveness)
  if (echonest_results == "ERROR"):
    return jsonify({"status":"error"})

  spotify_results = spotify_request(echonest_results["response"]["songs"][0]["artist_name"].encode('utf-8').strip(), echonest_results["response"]["songs"][0]["title"].encode('utf-8').strip())
  if (spotify_results == "ERROR"):
    return jsonify({"status":"error"})

  return format_response(echonest_results, spotify_results)

# We care about: hotttnesss(constant), tempo, liveness
def echonest_request(iteration, min_tempo, max_tempo, min_liveness, max_liveness):
  query_string = ECHONEST_BASE_URL + API_KEY + FORMAT_TYPE + RESULT_COUNT + SONG_MIN_HOTTTNESSS + BUCKET + ARTIST_START_YEAR_AFTER +\
    "&min_tempo=" + str(min_tempo) + "&max_tempo=" + str(max_tempo) +\
    "&min_liveness=" + str(min_liveness) + "&max_liveness=" + str(max_liveness) +\
    "&start=" + str(iteration)

  results = requests.get(query_string).json()

  if (results["response"]["status"]["code"] == 0 and len(results["response"]["songs"]) > 0):
    return results
  else:
    print "DEBUG: Echonest Error Request = " + query_string
    print "DEBUG: Echonest Error Response = " + str(results)
    return "ERROR"

def spotify_request(artist_name, track_name):
  query_string = SPOTIFY_BASE_URL +\
    "q=artist:\"" + artist_name + "\"" +\
    " track:\"" + track_name + "\"" +\
    SPOTIFY_TYPE

  results = requests.get(query_string).json()

  if ('tracks' in results.keys() and len(results["tracks"]["items"]) > 0):
    return results
  else:
    print "DEBUG: Spotify Error Request = " + query_string
    print "DEBUG: Spotify Error Response = " + str(results)
    return "ERROR"

def format_response(echonest_results, spotify_results):
  response = {}
  response["status"] = "success"
  response["artist_name"] = echonest_results["response"]["songs"][0]["artist_name"].encode('utf-8').strip()
  response["track_name"] = echonest_results["response"]["songs"][0]["title"].encode('utf-8').strip()
  response["duration"] = str(spotify_results["tracks"]["items"][0]["duration_ms"])
  response["tempo"] = str(echonest_results["response"]["songs"][0]["audio_summary"]["tempo"])
  response["liveness"] = str(echonest_results["response"]["songs"][0]["audio_summary"]["liveness"])
  response["hotttnesss"] = str(echonest_results["response"]["songs"][0]["song_hotttnesss"])

  response["track_id"] = str(spotify_results["tracks"]["items"][0]["id"])
  response["album_url"] = str(spotify_results["tracks"]["items"][0]["album"]["images"][0]["url"])

  return jsonify(response)

if __name__ == "__main__":
  app.debug = True
  app.run(host='0.0.0.0')
