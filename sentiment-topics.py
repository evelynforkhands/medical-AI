import json
import re
from gensim.models import LdaModel
from gensim.corpora import Dictionary
from nltk.corpus import stopwords
from textblob import TextBlob
import os
import json

folder_path = "reddit_posts"

combined_data = []

for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r") as file:
            data = json.load(file)
            combined_data.extend(data)

print(f"Total number of posts in combined dataset: {len(combined_data)}")
# total number of comments in combined dataset
total_comments = sum(len(post["comments"]) for post in combined_data)
print(f"Total number of comments in combined dataset: {total_comments}")



def preprocess_text(text):
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.lower()
    words = text.split()
    stopword_extended = stopwords.words("english")
    stopword_extended.extend(["http", "https", "www", "com", "org", "net", "edu", "reddit", "redditcom", "redditcomr", "redditcomrall", "en"])
    words = [word for word in words if word not in stopword_extended]
    return words


def extract_topics(corpus, num_topics=20):
    dictionary = Dictionary(corpus)
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in corpus]
    lda = LdaModel(doc_term_matrix, num_topics=num_topics, id2word=dictionary, passes=50)
    return lda.print_topics()


def sentiment_analysis(text):
    text_str = ' '.join(text)
    analysis = TextBlob(text_str)
    sentiment = analysis.sentiment.polarity

    return sentiment

minimum_karma = 50

credible_data = [post for post in combined_data if post["author"]["karma"] >= minimum_karma]
# exclude posts that are about looking for jobs/offering jobs/hiring
data = [post for post in credible_data if not any(word in post["title"].lower() for word in ["job", "hiring", "offer", "recruiting", "recruitment", "recruit", "looking for", "looking for a job", "looking for job"])]

print(f"Total number of posts in credible dataset: {len(data)}")
# total number of comments in credible dataset
total_comments = sum(len(post["comments"]) for post in data)
print(f"Total number of comments in credible dataset: {total_comments}")

preprocessed_titles = [preprocess_text(post["title"] + " " + post["text"]) for post in data]
preprocessed_comments = [preprocess_text(comment["text"]) for post in data for comment in post["comments"]]

topics = extract_topics(preprocessed_titles + preprocessed_comments)

sentiments = [sentiment_analysis(text) for text in preprocessed_titles + preprocessed_comments]
positive_count = sum(1 for sentiment in sentiments if sentiment > 0)
negative_count = sum(1 for sentiment in sentiments if sentiment < 0)
neutral_count = sum(1 for sentiment in sentiments if sentiment == 0)

results = {
    "topics": topics,
    "sentiments": {
        "positive": positive_count,
        "negative": negative_count,
        "neutral": neutral_count
    }
}

# Save the results to a JSON file
with open("results.json", "w") as outfile:
    json.dump(results, outfile, indent=4)
