import os
import json
import re
from gensim.models import LdaModel
from gensim.corpora import Dictionary
from nltk.corpus import stopwords
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt


def sentiment_analysis(text):
    text_str = ' '.join(text)
    analysis = TextBlob(text_str)
    sentiment = analysis.sentiment.polarity

    return sentiment


def extract_topics(corpus, num_topics=20):
    dictionary = Dictionary(corpus)
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in corpus]
    lda = LdaModel(doc_term_matrix, num_topics=num_topics, id2word=dictionary, passes=50)
    return lda.print_topics()


def preprocess_text(text):
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.lower()
    words = text.split()
    stopword_extended = stopwords.words("english")
    stopword_extended.extend(
        ["http", "https", "www", "com", "org", "net", "edu", "reddit", "redditcom", "redditcomr", "redditcomrall",
         "en"])
    words = [word for word in words if word not in stopword_extended]
    return words


folder_path = "reddit_posts"
minimum_karma = 50

combined_data = []

for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r") as file:
            data = json.load(file)
            combined_data.extend(data)

credible_data = [post for post in combined_data if post["author"]["karma"] >= minimum_karma]
# exclude posts that are about looking for jobs/offering jobs/hiring
credible_data = [post for post in credible_data if not any(word in post["title"].lower() for word in
                                                           ["job", "hiring", "offer", "recruiting", "recruitment",
                                                            "recruit", "looking for", "looking for a job",
                                                            "looking for job"])]

print(f"Total number of credible posts in combined dataset: {len(credible_data)}")


def preprocess_text(text):
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.lower()
    words = text.split()
    stopword_extended = stopwords.words("english")
    stopword_extended.extend(
        ["http", "https", "www", "com", "org", "net", "edu", "reddit", "redditcom", "redditcomr", "redditcomrall",
         "en"])
    words = [word for word in words if word not in stopword_extended]
    return words


def generate_wordcloud(corpus, type="positive"):
    text = ' ||| '.join([' '.join(phrase) for phrase in corpus])
    wordcloud = WordCloud(width=800, height=800, background_color='white', collocations=False).generate(text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    # save the word cloud
    if not os.path.exists("wordclouds"):
        os.makedirs("wordclouds")
    wordcloud.to_file(f"wordclouds/wordcloud_{type}.png")


preprocessed_titles = [preprocess_text(post["title"] + " " + post["text"]) for post in credible_data]
preprocessed_comments = [preprocess_text(comment["text"]) for post in credible_data for comment in post["comments"]]

topics = extract_topics(preprocessed_titles + preprocessed_comments)

sentiments = [sentiment_analysis(text) for text in preprocessed_titles + preprocessed_comments]

positive_phrases = [text for text, sentiment in zip(preprocessed_titles + preprocessed_comments, sentiments) if
                    sentiment > 0]
negative_phrases = [text for text, sentiment in zip(preprocessed_titles + preprocessed_comments, sentiments) if
                    sentiment < 0]
neutral_phrases = [text for text, sentiment in zip(preprocessed_titles + preprocessed_comments, sentiments) if
                   sentiment == 0]

print("Positive word cloud:")
generate_wordcloud(positive_phrases, type="positive")

print("Negative word cloud:")
generate_wordcloud(negative_phrases, type="negative")

print("Neutral word cloud:")
generate_wordcloud(neutral_phrases, type="neutral")

results = {
    "topics": topics,
    "sentiments": {
        "positive": len(positive_phrases),
        "negative": len(negative_phrases),
        "neutral": len(neutral_phrases)
    }
}

# Save the results to a JSON file
with open("results.json", "w") as outfile:
    json.dump(results, outfile, indent=4)
