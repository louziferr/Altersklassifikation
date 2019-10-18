import tweepy  # https://github.com/tweepy/tweepy
import json
import sys

# Twitter API credentials
access_key = "994948929711235077-LUDHhUc639aToGuh7YAhHc8DYWB4XBe"
access_secret = "BwjFkyvgU2xAxKGz7K3hDNiIpSxxg9EjX8Vkm0IaE4yjb"
owner = "louziferr"
owner_ID = "994948929711235077"
consumer_key = "img2e2Vtap54SB5SbDFx1XV1W"
consumer_secret = "WHOgGgzcABTX3rWER2mw5PNrxCMSpynnPHIQszZCpdAXIenqEf"


def get_all_tweets(hashtag):
    # Twitter only allows access to a users most recent 3240 tweets with this method

    # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    alltweets = dict()
    i = 0
    id_file = open("tweet_ids.txt", "w")

    for tweet in tweepy.Cursor(api.search, tweet_mode='extended', q=hashtag + "-filter:retweets", lang="de", since="2010-01-01").items(200):
        info = dict()
        info["id"] = tweet.id
        info["text"] = tweet.full_text
        info["date"] = str(tweet.created_at)
        print(tweet.id)
        alltweets[i] = info
        i += 1

    id_file.close()

    with open(str(hashtag) + ".json", "w") as f:
        json.dump(alltweets, f, indent=2)


if __name__ == "__main__":
    get_all_tweets(sys.argv[1])
    print("done")

