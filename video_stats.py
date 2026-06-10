import requests
import json
import os
from dotenv import load_dotenv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "bendu78130new"
maxResults = 10


def get_playlist_id():

    try:

        url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"


        response = requests.get(url)

        response.raise_for_status()

        #print(response) 

        data = response.json() 

        #print(data)

        ##method use to convert url to json and 4 is a convention
        #print(json.dumps(data, indent=4))
        ##id = channel id. uploads = playlist id

        channel_items = data['items'][0]
        channel_playlist_id = channel_items['contentDetails']['relatedPlaylists']['uploads']

        print(channel_playlist_id) 
        return channel_playlist_id
    
    except requests.exceptions.RequestException as e:
        raise e
    

def get_video_ids(playlistId):

    video_ids=[]

    pageToken = None 

    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistId}&key={API_KEY}"

    try:

        while True:
            
            url = base_url

            if pageToken:
                url += f"&pageToken={pageToken}"
            
            response = requests.get(url)

            response.raise_for_status()

            data = response.json()

            for item in data.get('items', []):
            
                video_id = item['contentDetails']['videoId']          
                video_ids.append(video_id)
            

            if 'nextPageToken' in data:
                pageToken = data['nextPageToken']
            else:
                break

            return video_ids

    except requests.exceptions.RequestException as e:
        raise e


if __name__ == "__main__":

    playlistId = get_playlist_id()
    video_ids = get_video_ids(playlistId)
    print(video_ids)

