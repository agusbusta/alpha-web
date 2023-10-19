import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

TWITTER_API_KEY=os.getenv("TWITTER_API_KEY")
TWITTER_KEY_SECRET=os.getenv("TWITTER_KEY_SECRET")
TWITTER_KEY_SECRET=os.getenv("TWITTER_KEY_SECRET")
TWITTER_ACCESS_TOKEN=os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_BEARER_TOKEN=os.getenv("TWITTER_BEARER_TOKEN")

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
    auth = tweepy.Client(
        TWITTER_BEARER_TOKEN,
        TWITTER_API_KEY,
        TWITTER_KEY_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET
    )
    
    paragraphs = split_text_into_paragraphs(content)

    if len(paragraphs) == 1:
        # Si solo hay un párrafo, publica un solo tweet
        response = auth.create_tweet(text=paragraphs[0])

    else:
        # Si hay varios párrafos, publica un hilo de tweets
        id = None
        for i, paragraph in enumerate(paragraphs):
            if i == 0:
                response = auth.create_tweet(text=paragraph)
                id = response[0].get("id")
            
            else:
                response = auth.create_tweet(text=paragraph, in_reply_to_tweet_id=id)
              
    
    return 'ok', 200

# Example usage
content = "Este es un ejemplo de un texto largo que queremos dividir en párrafos. Cada párrafo no debe exceder los 270 caracteres y debe tener puntos y aparte donde corresponda. Esto es un ejemplo de un párrafo más largo.Este es un ejemplo de un texto largo que queremos dividir en párrafos. Cada párrafo no debe exceder los 270 caracteres y debe tener puntos y aparte donde corresponda. Esto es un ejemplo de un párrafo más largo.."
send_tweets_to_twitter(content)
