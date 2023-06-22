import requests
import json
import tweepy
import time

BASE_URL = 'https://api.twitch.tv/helix/'
AUTH_URL = 'https://id.twitch.tv/oauth2/token'

keys = open("newkeys.txt", 'r')

CLIENT_ID = keys.readline().strip()
token = keys.readline().strip()
oauth = keys.readline().strip()

keys_twitter = open("keystwitterNEW.txt", 'r')

CONSUMER_KEY = keys_twitter.readline().strip()
CONSUMER_SECRET = keys_twitter.readline().strip()
ACCESS_TOKEN = keys_twitter.readline().strip()
ACCESS_TOKEN_SECRET = keys_twitter.readline().strip()
BARRER = keys_twitter.readline().strip()
tweeter = tweepy.Client(BARRER)

tweeter = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

AutParams = {'client_id': CLIENT_ID,
             'client_secret': token,
             'grant_type': 'client_credentials'
             }

AUTCALL = requests.post(url=AUTH_URL, params=AutParams)
ACCESS_TOKEN = AUTCALL.json()['access_token']
HEADERS = {'Client-ID': CLIENT_ID, 'Authorization': "Bearer " + ACCESS_TOKEN}


def get_follows(channel_id):
    cursor = ''
    follows = []
    while cursor is not None:
        url = f'{BASE_URL}users/follows?from_id={channel_id}&first=100&after={cursor}'
        response = requests.get(url, headers=HEADERS).json()
        if response['pagination']:
            cursor = response['pagination']['cursor']
        else:
            cursor = None
        for follow in response['data']:
            follows.append(follow['to_id'])
    return follows


def get_all_info(users):
    all_info = {}
    for user, user_id in users.items():
        follows = get_follows(user_id)
        all_info[user] = follows
    return all_info


def save_to_json(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)


def load_from_json():
    with open('data.json', 'r') as f:
        return json.load(f)


def get_unfollows(old_follows, new_follows):
    return list(set(old_follows) - set(new_follows))


def get_new_follows(old_follows, new_follows):
    return list(set(new_follows) - set(old_follows))


def get_ban(channel):
    query = f"""query {{userResultByLogin(login: "{channel}") {{
        ...on UserDoesNotExist
    {{
        key
        reason
    }}
    }}}}"""

    headers_ql = {'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
                  "Content-Type": "application/json"
                  }
    response = requests.post('https://gql.twitch.tv/gql', json={"query": query}, headers=headers_ql).json()
    return response['data']['userResultByLogin']

def send_ban_tweet(channel, type):
    tweeter.create_tweet(text=f'{channel} has been banned. Ban_type: {type}')

send_ban_tweet('chuj','chuj')

def is_banned(channel):
    ban_type = get_ban(channel)
    if ban_type and channel not in banned:
        send_ban_tweet(channel, ban_type['reason'])
        banned.append(channel)
        with open("banned.txt", 'a') as b:
            b.write(channel+'\n')
        return True
    else:
        return False


def get_num_follow(channel_id):
    url = f'{BASE_URL}users/follows?to_id={channel_id}'
    return requests.get(url, headers=HEADERS).json()['total']


def get_user_id(user):
    url = f'{BASE_URL}users?login={user}'
    return requests.get(url, headers=HEADERS).json()['data'][0]['id']


def get_users_with_num_follows(users):
    users_with_follows_num = {}
    for user in users:
        users_with_follows_num[user] = get_num_follow(get_user_id(user))
    users_with_follows_num = sorted(users_with_follows_num.items(), key=lambda item: item[1], reverse=True)
    return users_with_follows_num


def get_top_ten(users_with_follows_num):
    return [name for name, key in users_with_follows_num[:10]]


def send_unfollow_tweet(user, unfollows, comment):
    tweeter.create_tweet(text=f"{user} has just unfollowed {', '.join(unfollows)} {comment} 🤯")


def send_follow_tweet(user, unfollows, comment):
    tweeter.create_tweet(text=f"{user} has just followed {', '.join(unfollows)} {comment}")


def get_name_from_id(id):
    url = f'{BASE_URL}users?id={id}'
    response = requests.get(url, headers=HEADERS).json()
    if response['data']:
        return response['data'][0]['display_name']
    else:
        return None


def change_id_to_name(ids):
    names = []
    for id in ids:
        name = get_name_from_id(id)
        if name:
            names.append(name)
    return names


def get_changes_and_send_tweets(user, user_id, old_follows):
    if is_banned(user):
        return
    follows = get_follows(user_id)
    unfollows_ids = get_unfollows(old_follows, follows)
    new_follows_ids = get_new_follows(old_follows, follows)
    unfollows_names = change_id_to_name(unfollows_ids)
    follows_names = change_id_to_name(new_follows_ids)

    try:
        if len(unfollows_names) > 10:
            top = get_top_ten(get_users_with_num_follows(unfollows_names))
            send_unfollow_tweet(user, top, 'i paru innych laczków xD')
        elif len(unfollows_names) > 0:
            send_unfollow_tweet(user, unfollows_names, '')
        if len(follows_names) > 10:
            top = get_top_ten(get_users_with_num_follows(follows_names))
            send_follow_tweet(user, top, 'i paru innych laczków xD')
        elif len(follows_names) > 0:
            send_follow_tweet(user, follows_names, '')
        if follows:
            return follows
        else:
            return old_follows
    except:
        print('Tweet duplicate')
        return old_follows


if __name__ == "__main__":
    users = {}
    banned = []
    with open("banned.txt", 'r') as b:
        for line in b:
            banned.append(line.strip())
    with open('user_ids.txt', 'r') as f:
        for line in f:
            values = line.strip().split(' ')
            users[values[0]] = values[1]
    new_data = {}
    old_follows = load_from_json()
    for username, user_id in users.items():
            print(username)
            try:
                if username in old_follows:
                    new_data[username] = get_changes_and_send_tweets(username, user_id, old_follows[username])
                else:
                    new_data[username] = get_follows(user_id)
            except:
                new_data[username] = old_follows[username]
    save_to_json(new_data)

'''    test_follow = {}
    for k, v in users.items():
        test_follow[k] = get_follows(v)
        print(k, v,'done')
    save_to_json(test_follow)
    print('done')'''
