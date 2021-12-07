import api
import tweepy

users = {}

keys = open("keystwitter.txt", 'r')

CONSUMER_KEY = keys.readline().strip()
CONSUMER_SECRET = keys.readline().strip()
ACCESS_TOKEN = keys.readline().strip()
ACCESS_TOKEN_SECRET = keys.readline().strip()

TwitterAuth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
TwitterAuth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

tweeter = tweepy.API(TwitterAuth)

StinkyChesse = ['mandzio', 'ewroon', 'klaudiacroft']


def initialize():
    file = open("users.txt", "r")
    for data in file:
        user_name = data.strip()
        print(user_name)
        user_id = api.get_user_id(user_name)
        follows = api.get_all_follows(user_id)
        users[user_name] = [user_id, follows]
    print("Bot Launched")


def send_tweet(user_login, user, action):
    if user in StinkyChesse or user_login in StinkyChesse:
        user_login = "🧀 " + user_login
        user = user + " 🧀 "
    try:
        if action == "F":
            tweeter.update_status(user_login + " has just followed " + user)
            print(user_login + " has just followed " + user)
        elif action == "U":
            tweeter.update_status(user_login + " has just unfollowed " + user + "🤯")
            print(user_login + " has just unfollowed " + user + "🤯")
        elif action == "B":
            tweeter.update_status(user_login + " has just been banned.")
            print(user_login + " has just been banned.")
    except tweepy.TweepError as e:
        print(user_login + " has just followed " + user + "is an error - status duplicate")


def check_if_new(user_name, user_id, old_follows):
    try:
        new_follows = api.get_all_follows(user_id)

        follows = list(set(new_follows) - set(old_follows))
        unfollows = list(set(old_follows) - set(new_follows))
        if len(unfollows) > 20:
            send_tweet(user_name, '', 'B')
            return new_follows
        for user in follows:
            target_user = api.get_user_name_from_id(user)
            send_tweet(user_name, target_user, "F")
        for user in unfollows:
            target_user = api.get_user_name_from_id(user)
            send_tweet(user_name, target_user, "U")

        return new_follows
    except Exception as e:
        print(e)
        return old_follows


initialize()
while True:
    for user in users:
        users[user][1] = check_if_new(user, users[user][0], users[user][1])
