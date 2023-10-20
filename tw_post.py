from tweepy.errors import TweepyException
from dotenv import load_dotenv
import tweepy
import re
import os

load_dotenv()

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_KEY_SECRET = os.getenv("TWITTER_KEY_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

auth = tweepy.Client(
    TWITTER_BEARER_TOKEN,
    TWITTER_API_KEY,
    TWITTER_KEY_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET
)

# Split the summary into paragraphs of 280 characters max
def split_string(input_string: str) -> str:
    result = []

    chunks = input_string.split("- ")
    
    current_string = chunks[0]
    
    for part in chunks[1:]:
        if len(current_string + "-" + part) < 280:
            current_string += "•" + part
        else:
            result.append(current_string)
            current_string = "•" + part

    result.append(current_string)
    
    return result

# Finds the title in the summary
def find_title_between_asterisks(text):
    match = re.search(r'\*(.*?)\*', text)
    if match:
        title = match.group(1)
        return title
    else:
        return None

# Makes the title in bold
def bold(title):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    bold_chars = "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"

    output = ""

    for character in title:
        if character in chars:
            output += bold_chars[chars.index(character)]
        else:
            output += character
    return output

def send_tweets_to_twitter(content: str) -> list:

    if len(content) == 0:
        return 'Content has length 0', 404

    paragraphs = split_string(content) # separa el contenido en parrafos
    title = find_title_between_asterisks(paragraphs[0])  # Obtener el título original
    bold_title = bold(title)  # Obtener el título en negritas
    paragraphs[0] = title  # Reemplazar el título original en el primer párrafo

    if len(paragraphs) == 1:
        try:
            # Si solo hay un párrafo, publica un solo tweet
            response = auth.create_tweet(text=bold_title + '\n' + paragraphs[0])
            return 'Summary sent to Twitter successfully', 200
        except TweepyException as e:
            print('An error occurred:' + str(e))
            return 'An error occurred:' + str(e), 500
    else:
        id = None
        try:
            for i, paragraph in enumerate(paragraphs):
                if i == 0:
                    print('main tweet > ', bold_title + '\n' + paragraphs[0])
                    # response = auth.create_tweet(text=bold_title + '\n' + paragraphs[0])
                    # id = response[0].get("id")
                else:
                    print('paragraph >', paragraph)
                    # response = auth.create_tweet(text=paragraph, in_reply_to_tweet_id=id)
                    # Here the id have to be replace too, for the next threds.
            return 'Summary sent to Twitter successfully', 200
        except TweepyException as e:
            print('An error occurred:' + str(e))
            return 'An error occurred:' + str(e), 500

# Example usage
content = """
*Bitcoin ATM installations hit two-year low worldwide*
- Number of bitcoin ATMs dropped by 17%
- US experienced the biggest decline, now has 26,700 machines
- Europe has only 1,500 machines
- Decline attributed to controversies and criminal use
- Some operators turning off unprofitable ATMs
- Bitcoin Depot sees opportunity for market share growth through acquisitions and retail expansion.
"""

send_tweets_to_twitter(content) # Test sending the tweet








# def split_text_into_paragraphs(text, max_length=270):

#     paragraphs = []
#     current_paragraph = ""

#     for paragraph in text.split('\n'):
#         words = paragraph.split()
#         for word in words:
#             if len(current_paragraph) + len(word) + 1 <= max_length:
#                 current_paragraph += word + " "
#             else:
#                 paragraphs.append(current_paragraph.strip())
#                 current_paragraph = word + " "
#         if current_paragraph:
#             paragraphs.append(current_paragraph.strip())
#         current_paragraph = ""

#     combined_paragraphs = []
#     current_paragraph = ""
#     for paragraph in paragraphs:
#         if len(current_paragraph) + len(paragraph) + 1 <= max_length:
#             if current_paragraph:
#                 current_paragraph += " " + paragraph
#             else:
#                 current_paragraph = paragraph
#         else:
#             combined_paragraphs.append(current_paragraph)
#             current_paragraph = paragraph
#     if current_paragraph:
#         combined_paragraphs.append(current_paragraph)

#     return combined_paragraphs
