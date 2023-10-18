import tweepy
import os

TWITTER_API_KEY=os.getenv("TWITTER_API_KEY")
TWITTER_KEY_SECRET=os.getenv("TWITTER_KEY_SECRET")
TWITTER_KEY_SECRET=os.getenv("TWITTER_KEY_SECRET")
TWITTER_ACCESS_TOKEN=os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_BEARER_TOKEN=os.getenv("TWITTER_BEARER_TOKEN")

def send_tweets_to_twitter(content):

    # Authenticate to Twitter
    auth = tweepy.Client(
        TWITTER_BEARER_TOKEN,
        TWITTER_API_KEY,
        TWITTER_KEY_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET
    )

    data = auth.create_tweet(text=content)
    print('funciono')
    print(f'{data}')
    print(f'{data[0].get("id")}')
    print(f'{data[1]}')

# Example usage
content = "This is  1. This is  2. This is  3."
send_tweets_to_twitter(content)



##############



import tweepy

def send_tweets_to_twitter(content):
    

    # Authenticate to Twitter
    auth = tweepy.Client(
        TWITTER_BEARER_TOKEN,
        TWITTER_API_KEY,
        TWITTER_KEY_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET
    )

    try:
        # Validate input
        if not content or len(content) == 0:
            return "Error: Text is required and must have a length > 0", 400

        # Split content into paragraphs
        paragraphs = content.split(". ")
        print(paragraphs)
        
        if len(paragraphs) == 1:
            # If there's only one paragraph, post a single tweet
            status = auth.create_tweet(text=paragraphs[0])
            print('1 tweet created and posted a')
            return "Success: Tweet posted successfully", 200
        else:
            # If there are multiple paragraphs, post as a thread
            tweet_thread = []

            for i, paragraph in enumerate(paragraphs):
                # Ignore empty paragraphs
                if not paragraph:
                    continue

                tweet_text = paragraph

                if i == 0:
                    # For the first paragraph, create a tweet
                    status = auth.create_tweet(text=tweet_text)
                    print(f"1 tweet created and posted b: {tweet_text}")
                else:
                    # For subsequent paragraphs, reply to the previous tweet
                    status = auth.create_tweet(
                        text=tweet_text,
                        in_reply_to_status_id=tweet_thread[-1].id,
                        auto_populate_reply_metadata=True
                    )
                    print(f"Reply tweet created: {tweet_text}")
                
                tweet_thread.append(status)

            print('Thread posted successfully')
            return "Success: Thread posted successfully.", 200

    except Exception as e:
        return f"Error: {str(e)}", 500

# Example usage
content = "This is paragraph 1. This is paragraph 2. This is paragraph 3. "
send_tweets_to_twitter(content)
