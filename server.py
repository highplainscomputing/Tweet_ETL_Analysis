import os
import pprint

from typing import Union
from typing_extensions import Annotated

from tweet_analyzer import logger
from tweet_analyzer.pipeline import Pipeline
from tweet_analyzer.utils.parse_config import parse_config

from model import UserSchema, UserLoginSchema
from tweet_analyzer.utils.db_utils import insert_user, check_user, fetch_tweet, initialize_mongodb_instance, initialize_db,cleaner,fetch_all_tweet_ids

from fastapi import FastAPI, Path, Query, Depends, FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

from auth.auth_handler import signJWT
from auth.auth_bearer import JWTBearer

from etl import TweetETL

CONFIG = os.getenv('CONFIG', 'config.yaml')
CFG = parse_config(config_path=CONFIG)

app = FastAPI()

EXTRACTOR = TweetETL()

initialize_db()

MONGO_CLIENT, MONGO_DB, COLLECTION_NAME = initialize_mongodb_instance(config=CFG)

PIPELINE = Pipeline.from_config(CFG)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["GET","POST"],
    allow_headers=["*"],
)

@app.post("/user/signup", tags=["User"])
async def create_user(user: UserSchema = Body(...)):
    response = insert_user(user)
    if response:
        return signJWT(user.email)
    return {"error": "Username already exists"}


@app.post("/user/login", tags=["User"])
async def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        return signJWT(user.email)
    return {
        "error": "Wrong login details!"
    }


@app.get("/view_tweet/",dependencies=[Depends(JWTBearer())],tags=["Read Tweet from DB"])
async def read_tweet(q: Annotated[str, Query(alias="tweet-query-id")]):
    result = await fetch_tweet(tweet_id = q, mongo_client=MONGO_DB, collection_name=COLLECTION_NAME)
    print(result)
    if result:
        info = pprint.pformat(result, indent=4)
        logger.info(info)
        logger.info(q)
        logger.info('Tweet Fetched Successfully.')
    else:
        logger.info('Failed to fetch this tweet.')
        return {"response": "Failed to fetch this tweet."}
    return result

@app.get("/extract_tweets/{user_name}",dependencies=[Depends(JWTBearer())],tags=["ETL"])
async def extract_tweets(user_name: Annotated[str, Path(title="The user name of who posted tweet.")]):
    result = EXTRACTOR.extract_tweets(user_name=user_name)
    logger.info('Tweets Extracted for user %s .',user_name)
    if result:
        result = EXTRACTOR.transform_tweets()
        logger.info('Tweets Transformed.')
        try:
            result = await EXTRACTOR.load_tweets(db_client=MONGO_DB, collection_name=COLLECTION_NAME)
            logger.info('Tweets loaded into DB.')
        except Exception as e:
            return { "response" : f"Database transaction failed. {e}" }
        return { "response" : "Tweets Successfully loaded to database." }
    else:
        return { "response" : "Failed to Perform ETL." }

    

@app.get("/analyze_sentiment/",dependencies=[Depends(JWTBearer())],tags=["Analyze Tweet"])
async def analyze_sentiment(q: Annotated[str, Query(alias="tweet-query-id")]):
    result = await fetch_tweet(tweet_id = q, mongo_client=MONGO_DB, collection_name=COLLECTION_NAME)
    if result:
        cleaned_text = cleaner(result.get('Full_Text'))
        if cleaned_text:
            result = PIPELINE.apply(post=cleaned_text,task="sentiment_classifier")
            return {"Tweet_Text": cleaned_text,"result":result}
        else:
            return {
                "result" : "Empty Tweet."
            }
    else:
        return {
            "result" : "Invalid Tweet"
        }
    

@app.get("/analyze_emotion/",dependencies=[Depends(JWTBearer())],tags=["Analyze Tweet"])
async def analyze_emotion(q: Annotated[str, Query(alias="tweet-query-id")]):
    result = await fetch_tweet(tweet_id = q, mongo_client=MONGO_DB, collection_name=COLLECTION_NAME)
    if result:
        cleaned_text = cleaner(result.get('Full_Text'))
        if cleaned_text:
            result = PIPELINE.apply(post=cleaned_text,task="emotion")
            return {"Tweet_Text": cleaned_text,"result":result}
        else:
            return {
                "result" : "Empty Tweet."
            }
    else:
        return {
            "result" : "Invalid Tweet"
        }
    
@app.get("/view_all_tweet_ids/",dependencies=[Depends(JWTBearer())],tags=["Read Tweet from DB"])
async def read__all_tweet():
    result = await fetch_all_tweet_ids(mongo_client=MONGO_DB, collection_name=COLLECTION_NAME)
    if result:
        info = pprint.pformat(result, indent=4)
        logger.info(info)
        logger.info('Tweets Fetched Successfully.')
    else:
        logger.info('Failed to fetch tweets.')
        return {"response": "Failed to fetch tweets."}
    return result
    