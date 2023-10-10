# Tweet Analysis

Machine learning pipeline for end-to-end Analysis of Tweets of user using NLP models

---

### Installation

**Required python version: 3.7 or higher and MongoDB Installed Locally.**

```bash
pip install -r requirements.txt
```

### Docker setup

**1. Build docker**:

```bash
docker build --tag tweet_analysis:latest .
```

**2. Run docker server**:

```bash
docker run -d -p 8080:8080 tweet_analysis:latest
```

**3. Use Docker Compose**:
It will create both the images (mongoDB and fastAPI) and start the containers.

```bash
docker-compose up --build
```

### Server API usage

#### Start server

```bash
uvicorn run_server:app --host "0.0.0.0" --port 8000
```

For Visualizing application Visit:
***http://localhost:8000/docs***

#### Endpoints

- `/health` Endpoint for checking server availability.
- `/user/signup` Endpoint for registering a user.
- `/user/login` Endpoint for login a user and providing an access token.
- `/view_tweet/` Endpoint for getting a tweet from its Id.
- `/view_all_tweet_ids/` Endpoint for getting all ids of tweets stored in DB along with Its User Name.
- `/extract_tweets/{user_name}}` Endpoint for extracting loading and transforming tweets from Internet.
- `/analyze_sentiment` Endpoint gives sentiment against a tweet by providing a Tweet ID.
- `/analyze_emotion/ Endpoint gives emotion analysis against a tweet by providing a Tweet ID`

### Run tests

```bash
pytest .
```

## Configuration and file structure

Project file structure is:

```
.
├── tweet_analyzer
│    ├── __init__.py
│    ├── pipeline.py
│    ├── models
│    │    ├── __init__.py
│    │    ├── base.py
│    │    ├── sentiment_classifier.py
│    │    └── emotion_analysis.py
│    │  
│    ├── utils
│    │    ├── __init__.py
│    │    ├── db_utils.py
│    │    ├── fastapi_models.py
│    │    └── parse_config.py
├── test
│   ├──__init__.py
│   ├──test_parse_config.py
│
└── docker-compose.yml
└── Dockerfile
└── config.yaml
└── README.md
└── etl.py
└── server.py
└── requirements.txt
└── model.py
└── .env

```


### Source

For adding the authentication to fastapi endpoints, code was taken from following URL

**https://github.com/BekBrace/FASTAPI-and-JWT-Authentication**

### Contributer

Sibtain Raza
