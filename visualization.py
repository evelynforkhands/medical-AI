import json
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re

# Load the results from the JSON file
with open("results.json", "r") as infile:
    results = json.load(infile)

# Pie chart for sentiment distribution
sentiments = results["sentiments"]
labels = ["Positive", "Negative", "Neutral"]
sizes = [sentiments["positive"], sentiments["negative"], sentiments["neutral"]]
colors = ["#99ff99", "#ff9999", "#c2c2d6"]
explode = (0.1, 0.1, 0.1)

plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct="%1.1f%%", shadow=True, startangle=90)
plt.title("Sentiment Distribution")
plt.axis("equal")
plt.savefig("plots/sentiment distribution.png")
plt.clf()

# Bar chart for topic distribution
topics = results["topics"]
# labels are the actual topic names
topic_labels = [re.findall("\"([a-zA-Z]+)\"", topic[1])[0] for topic in topics]



topic_weights = [sum([float(weight) for weight in re.findall("\d+\.\d+", topic[1])]) for topic in topics]
# space out the bars
plt.figure(figsize=(20, 5))
# sort the bars by weight
topic_labels, topic_weights = zip(*sorted(zip(topic_labels, topic_weights), key=lambda x: x[1], reverse=True))
plt.bar(topic_labels, topic_weights, color="#4caf50")
plt.title("Topic Distribution")
plt.xlabel("Topics")
plt.ylabel("Weights")
plt.savefig("plots/topic distribution.png")
plt.clf()
