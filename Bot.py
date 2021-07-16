import requests,json,sys
import time
import tweepy
BASE_URL = 'https://api.twitch.tv/helix/'
authURL = 'https://id.twitch.tv/oauth2/token'


CLIENT_ID = ''
token = ''
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""

TwitterAuth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
TwitterAuth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(TwitterAuth)


AutParams = {'client_id': CLIENT_ID,
             'client_secret': token,
             'grant_type': 'client_credentials'
             }

AUTCALL = requests.post(url=authURL, params=AutParams)
ACCESS_TOKEN = AUTCALL.json()['access_token']
HEADERS = {'Client-ID' : CLIENT_ID, 'Authorization' :  "Bearer " + ACCESS_TOKEN}

def get_response(query):
    url = BASE_URL + query
    response = requests.get(url, headers=HEADERS)
    return response

def get_user_query(user_login):
    return 'users?login={0}'.format(user_login)

def get_follows_query(User_follows, pagination):
    user_id = get_User_ID(User_follows)
    return 'users/follows?from_id={0}&first=100&after={1}'.format(user_id,pagination)


def get_User_ID(user_login):
    query = get_user_query(user_login)
    response = get_response(query)
    response_json = response.json()
    try:
        User_ID = response_json['data'][0]['id']
        return (User_ID)
    except:
        Sadge = 1

def GetAllFollows(user_login):
    pagination = ""
    Follows = []
    while True:
        query = get_follows_query(user_login, pagination)
        response = get_response(query)
        response_json = response.json()
        length = len(response_json['data'])

        for x in range(length):
            try:
                Follows.append(response_json['data'][x]['to_name'])
            except:
                Sadge = 1
        try:
            pagination = response_json['pagination']['cursor']
        except:
            return Follows


def CheckNew (user_login, Follows):
    NewFollows = GetAllFollows(user_login)

    Follow = list(set(NewFollows)-set(Follows))
    Unfollows = list(set(Follows)-set(NewFollows))

    for user in Follow:
        try:
            api.update_status(user_login + " has just followed " + user)
            print(user_login + " has just followed " + user)
        except tweepy.TweepError as e:
            print(user_login + " has just followed " + user + "is an error - status duplicate")

    for user in Unfollows:
        try:
            api.update_status(user_login + " has just unfollowed " + user + "🤯")
            print(user_login + " has just unfollowed " + user + "🤯")
        except tweepy.TweepError as e:
            print(user_login + " has just unfollowed " + user + "is an error - status duplicate")

    return NewFollows

file = open("users.txt","r")
Users = []
for x in file:
    if x.endswith("\n"):
        StreamersName = x[:-1]
    else:
        StreamersName = x
    Follows = GetAllFollows(StreamersName)
    Users.append([StreamersName,Follows])

print("Bot Launcehd")

while True:
    start = time.time()
    for user in Users:
        Follows = user[1]
        StreamersName = user[0]
        user[1]=CheckNew(StreamersName, Follows)
        end = time.time()
        ##print(end-start)
