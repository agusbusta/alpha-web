import tweepy
from tweepy.errors import TweepyException
import os
from dotenv import load_dotenv

load_dotenv()


TWITTER_API_KEY=os.getenv("TWITTER_API_KEY")
TWITTER_KEY_SECRET=os.getenv("TWITTER_KEY_SECRET")
TWITTER_KEY_SECRET=os.getenv("TWITTER_KEY_SECRET")
TWITTER_ACCESS_TOKEN=os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_BEARER_TOKEN=os.getenv("TWITTER_BEARER_TOKEN")

auth = tweepy.Client(
        TWITTER_BEARER_TOKEN,
        TWITTER_API_KEY,
        TWITTER_KEY_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET
    )

print('Logged user > ', auth.get_me()[0])

def split_string(input_string):
    result = []

    chunks = input_string.split("-")
    
    current_string = chunks[0]
    
    for part in chunks[1:]:
        print('current_string > ', current_string)
        print('part > ', part)
        # Verificamos si el string actual junto con el próximo fragmento, incluyendo el dash
        # tiene menos de 280 caracteres
        if len(current_string + "-" + part) < 280:
            # Si es así, agregamos el fragmento y el dash al string actual
            current_string += "-" + part
        else:
            # Si supera los 280 caracteres, agregamos el string actual a la lista de resultados
            result.append(current_string)
            # Empezamos un nuevo string con el fragmento actual
            current_string = "-" + part

    # Agregamos el último string al resultado
    result.append(current_string)
    
    return result

def split_text_into_paragraphs(text, max_length=270):
    paragraphs = []
    current_paragraph = ""

    for paragraph in text.split('\n'):
        words = paragraph.split()
        for word in words:
            if len(current_paragraph) + len(word) + 1 <= max_length:
                current_paragraph += word + " "
            else:
                paragraphs.append(current_paragraph.strip())
                current_paragraph = word + " "
        if current_paragraph:
            paragraphs.append(current_paragraph.strip())
        current_paragraph = ""

    combined_paragraphs = []
    current_paragraph = ""
    for paragraph in paragraphs:
        if len(current_paragraph) + len(paragraph) + 1 <= max_length:
            if current_paragraph:
                current_paragraph += " " + paragraph
            else:
                current_paragraph = paragraph
        else:
            combined_paragraphs.append(current_paragraph)
            current_paragraph = paragraph
    if current_paragraph:
        combined_paragraphs.append(current_paragraph)

    return combined_paragraphs

def send_tweets_to_twitter(content):

    if len(content) == 0:
        return 'Content has length 0', 404
   
    paragraphs = split_string(content)

    if len(paragraphs) == 1:
        try:
            # Si solo hay un párrafo, publica un solo tweet
            response = auth.create_tweet(text=paragraphs[0])
            print('response in length == 1 > ', response)
            return 'Summary sent to twitter successfully', 200
        except TweepyException as e:
            print('An error occured:' + str(e))
            return 'An error occured:' + str(e), 500

    else:
        # Si hay varios párrafos, publica un hilo de tweets
        id = None
        try:
            for i, paragraph in enumerate(paragraphs):
                if i == 0:
                    print('paragraph 0 > ', paragraph)
                    response = auth.create_tweet(text=paragraph)
                    id = response[0].get("id")
                    print('response in i == 0 > ', response)
                
                else:
                    print('next paragraph> ', paragraph)
                    response = auth.create_tweet(text=paragraph, in_reply_to_tweet_id=id)
                    print('response in i > 0 > ', response)
            return 'Summary sent to twitter successfully', 200
        except TweepyException as e:
            print('An error occured:' + str(e))
            return 'An error occured:' + str(e), 500
              
    


# Example usage
content = """
Bitcoin ATM installations hit two-year low worldwide
- Number of bitcoin ATMs dropped by 17%
- US experienced the biggest decline, now has 26,700 machines
- Europe has only 1,500 machines
- Decline attributed to controversies and criminal use
- Some operators turning off unprofitable ATMs
- Bitcoin Depot sees opportunity for market share growth through acquisitions and retail expansion.
"""
print(split_string(content))
# send_tweets_to_twitter(content)
