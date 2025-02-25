from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
def search_youtube(query, api_key, max_results=3):
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    try:
        request = youtube.search().list(
            q=query,
            part='snippet',
            maxResults=max_results,
            type='video'
        )
        response = request.execute()
        
        print("YouTube API Response:", response) 

        video_results = []
        for item in response.get('items', []):
            video_id = item['id'].get('videoId', '')
            video_link = f"https://www.youtube.com/watch?v={video_id}"
            thumbnail_url = item['snippet']['thumbnails']['high']['url']
            video_title = item['snippet']['title'] 
            
            video_results.append({
                "title": video_title,  
                "link": video_link,
                "thumbnail": thumbnail_url
            })
        
        return video_results
    
    except Exception as e:
        print("YouTube API Error:", str(e)) 
        return []

def main():
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        print("Error: YouTube API key not found. Please check your .env file.")
        return
    
    recipe_name = "how to make " + input("Enter the recipe name: ")
    print(f"Searching YouTube for '{recipe_name}'...")
    video_results = search_youtube(recipe_name, api_key)
    
    if video_results:
        print("\nHere are some video links with thumbnails:")
        for video in video_results:
            print(f"Link: {video['link']}, Thumbnail: {video['thumbnail']}")
    else:
        print("No videos found.")

if __name__ == "__main__":
    main()
