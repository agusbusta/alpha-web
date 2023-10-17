import tweepy

def send_tweets_to_twitter(content, image_urls):
    TWITTER_API_KEY="QTouviuIjjlHKpKy3aeheBkxf"
    TWITTER_KEY_SECRET="ExOZb4GVXlQZG4owCwWvN7fczUDstKyGqnelNPcJ8Lt2PsP8be"
    TWITTER_ACCESS_TOKEN="1659350701040971782-yH1W9bX6apmjjQglROL3sAsf8d58wi"
    TWITTER_ACCESS_TOKEN_SECRET="naoDyxY14AjwEeu9Gb6XR3x20TnFlSaNfnNKlxSba2Tcg"

        # Authenticate to Twitter
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, 
        TWITTER_KEY_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, 
       TWITTER_ACCESS_TOKEN_SECRET )

    api = tweepy.API(auth)

    try:
        api.verify_credentials()
        print("Authentication OK")
    except:
        print("Error during authentication")


    # Validate the input
    if not content or len(content) == 0:
        print("Text is required and must have a length > 0.")
        return "Text is required and must have a length > 0.", 400

    try:
        # Split the content into chunks of 280 characters or less
        # while considering "-" as the divisor line
        text_chunks = content.split("-")
        tweets_to_post = []

        for chunk in text_chunks:
            chunk = chunk.strip()  # Remove leading/trailing spaces

            # Split the chunk into multiple tweets of 280 characters
            for i in range(0, len(chunk), 280):
                tweet_text = chunk[i:i + 280]

                # Check if there's more content to add to the thread
                if i + 280 < len(chunk):
                    tweet_text += "..."
                
                tweets_to_post.append(tweet_text)

        # Post tweets as a thread
        tweet_thread = []
        for i, tweet_text in enumerate(tweets_to_post):
            if i == 0:
                status = api.update_status(status=tweet_text)
            else:
                status = api.update_status(status=tweet_text, in_reply_to_status_id=status.id)
            tweet_thread.append(status)

        # Attach images to tweets
        for i, status in enumerate(tweet_thread):
            tweet_image = image_urls[i] if i < len(image_urls) else None
            if tweet_image:
                try:
                    api.update_with_media(filename=tweet_image, status="", in_reply_to_status_id=status.id)
                except tweepy.TweepError as e:
                    print(f"Error posting tweet: {str(e)}")
                    return f"Error posting tweet: {str(e)}", 500

        print("Thread posted successfully.")
        return "Thread posted successfully.", 200

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}", 500

content= "Test"
image_urls = ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]
result, status_code = send_tweets_to_twitter(content, image_urls)
print(result, status_code)