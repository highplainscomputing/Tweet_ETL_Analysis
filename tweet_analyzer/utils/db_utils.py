"""
Utility Functions for async database operations

TODO: Improving the CRUD Operations utility functions
"""
import os
import sqlite3
import asyncio

from typing import Dict, Any
from model import UserSchema, UserLoginSchema
from passlib.hash import bcrypt
from tweet_analyzer import logger
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.encoders import jsonable_encoder



def deserializer(object) -> dict:
    """Helper function to decode Comment Object to general dict"""
    return {
        key:object[key] if key!="_id" else str(object[key]) for key in object.keys()
        }

def asyncio_process(db_query):
    """decorator for async database operation"""

    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(db_query(*args, **kwargs))

    return wrapper


@asyncio_process
async def create_collection(async_db, collection_name):
    list_of_collection = await async_db.list_collection_names()
    if collection_name not in list_of_collection:
        async_db.create_collection(collection_name)


def initialize_db():
    """
    Create a User Table in sqlite DB to store registered users. 
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def insert_user(user: UserLoginSchema):
    """
    
    """
    hashed_password = bcrypt.hash(user.password)

    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", (user.username,user.email ,hashed_password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    
def check_user(user: UserLoginSchema):
    """
    
    """
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE email = ?", (user.email,))
        result = cursor.fetchone()
        conn.close()
        if result is None:
            return False
        stored_hashed_password = result[0]
        if not bcrypt.verify(user.password, stored_hashed_password):
            return False
        return True
    except Exception as e:
        print(e) # remove this statement with logging call
    return False

def initialize_mongodb_instance(config: Dict[str, Any]) -> (AsyncIOMotorClient, Any, str):
    """
    Initialize a MongoDB Async Instance using Motor Client and
    Creates a collection for insertion of Json Objects.

    Returns:
        AsyncIOMotorClient, Doc Collection Name

    """

    db_url = os.getenv('DB_URL', '')
    if not db_url:
        db_config = config['database']['no_sql']
        user = db_config.get('user', 'sibtain')
        host = db_config.get('host', '0.0.0.0')
        port = db_config.get('port', '27017')
        db_url = 'mongodb://{}:{}/{}'.format(host, port, user)
    mongodb_async_client = AsyncIOMotorClient(db_url)
    collection_name = config['database']['no_sql'].get('collection', 'tweets')
    db_name = config['database']['no_sql'].get('db_name', 'Tweet_DB')
    async_db = mongodb_async_client[db_name]
    return mongodb_async_client, async_db, collection_name

def cleaner(text):
    text = text.strip().replace('"','').replace("'",'').replace('\\','').replace('/','')
    text = "\n".join([s for s in text.split("\n") if s])
    text = ' '.join(text.split())
    return text.strip()
    

async def insert_single_tweet(tweet_json: Dict[str, Any], mongo_client: AsyncIOMotorClient, collection_name: str):
    
    inserted_object = await mongo_client[collection_name].insert_one(tweet_json)
    logger.info('Tweet {} Successfully Added to Collection'.format(inserted_object.inserted_id))
    return inserted_object.inserted_id


async def insert_tweets(list_of_json: Dict[str, Any], mongo_client: AsyncIOMotorClient, collection_name: str):
    inserted_object = await mongo_client[collection_name].insert_many(list_of_json)
    logger.info('All tweets inserted Successfully Added to Collection')
    return inserted_object


async def fetch_tweet(tweet_id: str, mongo_client: AsyncIOMotorClient, collection_name: str):
    try:
        doc_id = {"Conversation_Id_Str": tweet_id}
        fetched_object = await mongo_client[collection_name].find_one(doc_id)
        if fetched_object:
            logger.info("Tweet retrieved successfully.")
            return deserializer(fetched_object)
        return None
    except Exception as e:
        logger.error("Failed to Retrieve Tweet %s.",e)
        return None
    
async def fetch_all_tweet_ids(mongo_client: AsyncIOMotorClient, collection_name: str):
    try:
        
        fetched_object = await mongo_client[collection_name].find({}, {"_id":0, "Conversation_Id_Str": 1, "User.Screen_Name": 1 }).to_list(1000)
        if fetched_object:
            logger.info("All Tweet Ids retrieved successfully.")
            return fetched_object
        return None
    except Exception as e:
        logger.error("Failed to Retrieve Tweet Ids. %s",e)
        return None



