import json
import time
import praw
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

CLIENT_ID = config.get("credentials", "CLIENT_ID")
SECRET_KEY = config.get("credentials", "SECRET_KEY")


post_number = 0
total_posts = 200
last_post_id = '12i2oy5'

reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=SECRET_KEY,
                     user_agent='medical-ai')

subreddit = reddit.subreddit('all')

query = 'medical AI'
search_results = subreddit.search(query, limit=total_posts, sort='new', params={'after': last_post_id})

filename = 'reddit_posts/600_800.json'
posts_data = []

try:
    for post in search_results:
        try:
            post_data = {
                "title": post.title if hasattr(post, 'title') else None,
                "id": post.id if hasattr(post, 'id') else None,
                "text": post.selftext if hasattr(post, 'selftext') else None,
                "url": post.url if hasattr(post, 'url') else None,
                "score": post.score if hasattr(post, 'score') else None,
                "time": post.created_utc if hasattr(post, 'created_utc') else None,
                "author": {
                    "name": post.author.name if hasattr(post.author, 'name') else None,
                    "karma": post.author.total_karma if hasattr(post.author, 'total_karma') else None,
                    "age": post.author.created_utc if hasattr(post.author, 'created_utc') else None
                },
                "comments": []
            }
            for comment in post.comments:
                comment_data = {
                    "text": comment.body if hasattr(comment, 'body') else None,
                    "score": comment.score if hasattr(comment, 'score') else None,
                    "time": comment.created_utc if hasattr(comment, 'created_utc') else None
                }
                post_data["comments"].append(comment_data)
            posts_data.append(post_data)
            post_number += 1
            print(f'Post {post_number} of {total_posts} scraped')
            time.sleep(1)
        except Exception as e:
            print('Error: ', e)
            with open(filename, 'w') as f:
                json.dump(posts_data, f, indent=4)
            continue
except Exception as e:
    print('Error: ', e)
    with open(filename, 'w') as f:
        json.dump(posts_data, f, indent=4)


with open(filename, 'w') as f:
    json.dump(posts_data, f, indent=4)
