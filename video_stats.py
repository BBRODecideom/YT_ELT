import requests
import json
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import date


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


def extract_video_data(video_ids):

    extracted_data = []


    def batch_lists(videos_ids, batch_size):

        for i in range(0, len(videos_ids), batch_size):
            yield videos_ids[i:i + batch_size]


    try:
        for batch in batch_lists(video_ids, maxResults):
            video_ids_str = ",".join(batch)

            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}"
            
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get('items',[]):
                video_id = item['id']
                snippet = item['snippet']
                contentDetails = item['contentDetails']
                statistics = item['statistics']

                video_data = {
                    "video_id": video_id,
                    "title": snippet.get('title'),
                    "publishedAt": snippet.get('publishedAt'),
                    "duration": contentDetails.get('duration'),
                    "viewCount": statistics.get('viewCount', None),
                    "likeCount": statistics.get('likeCount', None),
                    "commentCount": statistics.get('commentCount', None)
                }

                extracted_data.append(video_data)

        return extracted_data
            

    except requests.exceptions.RequestException as e:
        raise e

def save_to_json(extracted_data):

    file_path = f"./data/YT_Data_{date.today()}.json"

    with open(file_path, "w", encoding="utf-8") as json_outfile:
        json.dump(extracted_data, json_outfile, indent=4, ensure_ascii=False)
        


if __name__ == "__main__":

    playlistId = get_playlist_id()
    video_ids = get_video_ids(playlistId)
    video_data = extract_video_data(video_ids)
    save_to_json(video_data)

