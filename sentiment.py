import os
import json
import re
from gensim.models import LdaModel
from gensim.corpora import Dictionary
from nltk.corpus import stopwords
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def remove_links(text):
    text = re.sub(r'http\S+', '', text)
    return text


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
    text = re.sub(r'\n', ' ', str(text))
    text = re.sub(r'\t', ' ', str(text))
    text = re.sub(r'\W', ' ', str(text))
    text = re.sub(r'\s+', ' ', str(text))
    text = text.lower()
    words = text.split()
    stopword_extended = stopwords.words("english")
    stopword_extended.extend(
        ["http", "https", "www", "com", "org", "net", "edu", "reddit", "redditcom", "redditcomr", "redditcomrall",
         "en", "x200b", "png", "webp", "jpg", "jpeg", "gif", "html", "n", "u",
         "healthcare", "ai", "need", "medical"])
    words = [word for word in words if word not in stopword_extended]
    return words


folder_path = "reddit_posts/medical_ai"
minimum_karma = 50

combined_data = []

for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r") as file:
            data = json.load(file)
            combined_data.extend(data)

with open('banned_words.json', 'r') as file:
    banned_words = json.load(file)

credible_data = [post for post in combined_data if post["author"]["karma"] >= minimum_karma]
# exclude posts that are about looking for jobs/offering jobs/hiring
credible_data = [post for post in credible_data if not any(word in post["title"].lower() + post["text"].lower() for word in
                                                           banned_words)]

print(f"Total number of credible posts in combined dataset: {len(credible_data)}")
print(f"Total number of comments for all credible posts: {sum([len(post['comments']) for post in credible_data])}")



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


# preprocessed_titles = [preprocess_text(post["title"] + " " + post["text"]) for post in credible_data]
# preprocessed_comments = [preprocess_text(comment["text"]) for post in credible_data for comment in post["comments"]]

full_texts = [remove_links(post["title"]) + " " + remove_links(post["text"]) for post in credible_data]
full_texts.append([remove_links(comment["text"]) for post in credible_data for comment in post["comments"]])


sentiments = [sentiment_analysis(text) for text in full_texts]
# plot the distribution of sentiments, percentage of positive, negative and neutral sentiments
plt.figure(figsize=(10, 5))

num_positive = len([sentiment for sentiment in sentiments if sentiment > 0.1])
num_negative = len([sentiment for sentiment in sentiments if sentiment < -0.1])
num_neutral = len([sentiment for sentiment in sentiments if sentiment <= 0.1 and sentiment >= -0.1])

total_phrases = num_positive + num_negative + num_neutral
positive_percentage = (num_positive / total_phrases) * 100
negative_percentage = (num_negative / total_phrases) * 100
neutral_percentage = (num_neutral/ total_phrases) * 100

labels = ['Positive', 'Negative', 'Neutral']
sizes = [positive_percentage, negative_percentage, neutral_percentage]
colors = ['#99ff99', '#ff9999', '#66b3ff']
explode = (0.1, 0.1, 0.1)

plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)

plt.axis('equal')

plt.show()


positive_phrases = [text for text, sentiment in zip(full_texts, sentiments) if sentiment > 0.1]
negative_phrases = [text for text, sentiment in zip(full_texts, sentiments) if sentiment < -0.1]
neutral_phrases = [text for text, sentiment in zip(full_texts, sentiments) if sentiment <= 0.1 and sentiment >= -0.1]

# save positive, negative and neutral phrases to json files, including their sentiments
with open("positive_phrases_with_sentiment.json", "w") as file:
    json.dump([(text, sentiment) for text, sentiment in zip(positive_phrases, sentiments) if sentiment > 0], file)

with open("negative_phrases_with_sentiment.json", "w") as file:
    json.dump([(text, sentiment) for text, sentiment in zip(negative_phrases, sentiments) if sentiment < 0], file)

with open("neutral_phrases_with_sentiment.json", "w") as file:
    json.dump([(text, sentiment) for text, sentiment in zip(neutral_phrases, sentiments) if sentiment == 0], file)



preprocessed_positive_phrases = [preprocess_text(text) for text in positive_phrases]
preprocessed_negative_phrases = [preprocess_text(text) for text in negative_phrases]
preprocessed_neutral_phrases = [preprocess_text(text) for text in neutral_phrases]
topics = extract_topics(preprocessed_positive_phrases + preprocessed_negative_phrases + preprocessed_neutral_phrases, num_topics=10)



print("Positive word cloud:")
generate_wordcloud(preprocessed_positive_phrases, type="positive")

print("Negative word cloud:")
generate_wordcloud(preprocessed_negative_phrases, type="negative")

print("Neutral word cloud:")
generate_wordcloud(preprocessed_neutral_phrases, type="neutral")

results = {
    "topics": topics,
    "sentiments": {
        "positive": len(positive_phrases),
        "negative": len(negative_phrases),
        "neutral": len(neutral_phrases)
    }
}

with open("results.json", "w") as outfile:
    json.dump(results, outfile, indent=4)
