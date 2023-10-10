import re
import json
import httpx
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from tweet_analyzer.utils.db_utils import insert_tweets
from parsel import Selector



HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TweetETL:
    def __init__(self):
        self.base_url = "https://syndication.twitter.com/srv/timeline-profile/screen-name/{user_name}"
        self.tweet_fields = ['location','conversation_id_str','created_at','entities','full_text','lang','user']
        self.user_fields = ['description','id_str','location','name','is_blue_verified','screen_name']
        self.list_of_tweets = []

    def extract_tweets(self,user_name:str) -> dict:
        """
        Function to fetch tweets from a user profile using embedded url
        """
        with httpx.Client(http2=True, headers=HEADERS) as client:
            complete_url = self.base_url.format(user_name=user_name)
            try:
                response = client.get(url = complete_url)
                if response.status_code == 200:
                    sel = Selector(response.text)
                    data = json.loads(sel.css("script#__NEXT_DATA__::text").get())
                    data = data["props"]["pageProps"]["timeline"]["entries"]
                    self.list_of_tweets = [tweet["content"]["tweet"] for tweet in data]
                    return {
                        "response" : f"Tweets Extracted For User {user_name}"
                    }

            except Exception as exception:
                logging.exception("An error occurred: %s", str(exception))

    def text_clean(self,text):
        text = re.sub(r'@\w+', 'mentioned_person', text)
        text = re.sub(r'https?://\S+|www\.\S+', 'mentioned_url', text)
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}-\d{2}-\d{4}',
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,\s+\d{4}'
            ]
        
        for pattern in date_patterns:
            text = re.sub(pattern, 'mentioned_date', text)

        time_patterns = [
            r'\d{1,2}:\d{2}\s?(?:AM|PM|am|pm)?',
            r'\d{1,2}:\d{2}'
            ]
        
        for pattern in time_patterns:
            text = re.sub(pattern, 'mentioned_time', text)

        return text
    
    def transform_tweets(self):
        """
        This function parse every tweet and gets the required and 
        important information for our analysis from every tweet.
        It also does text cleaning to remove irrelevant information from tweets.
        """


        #First we filter important fields of tweets

        self.parsed_tweets = [
            {
                key.title(): tweet[key] for key in tweet.keys() if key in self.tweet_fields
            }
            for tweet in self.list_of_tweets
        ]

        #In second iteration we filter the values of user information

        self.parsed_tweets = [
            {
                key: (tweet[key] if key != "User" else {sub_key.title(): tweet[key][sub_key] for sub_key in self.user_fields})
                for key in tweet.keys()
            }
            for tweet in self.parsed_tweets
        ]

        # Finally we clean our text information in tweets

        self.parsed_tweets = [
            {
                key: self.text_clean(tweet[key]) if key=="Full_Text" else tweet[key] for key in tweet.keys()
                
            }
            for tweet in self.parsed_tweets
        ]
        return {
            "response" : f"Tweets Transformed and Cleaned."
        }
    
    async def load_tweets(self, db_client: AsyncIOMotorClient, collection_name: str):
        """
        This function loads the parsed and filtered tweets into mongodb
        """
        response = await insert_tweets(self.parsed_tweets, mongo_client=db_client, collection_name=collection_name)
        print(response)
        return response