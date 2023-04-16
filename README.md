# Reddit Posts Related to Medical AI

This repository contains code for a university project, aimed at uncovering people's outlook on medical AI. 

## Overview

The code includes collecting the reddit posts through the Reddit API, preprocessing the text data, extracting main topics discussed using LDA, performing basic sentiment analysis on the titles, text and all comments to a post, and visualizing the results.

### Filtering of posts overview

To exclude completely irrelevant posts, the following criteria were used:
1. Posts of users with less than 50 karma.
2. Posts related to job search/job offerings (containing "job", "hiring", "offer", "recruiting", "recruitment",
                                                            "recruit", "looking for", "looking for a job",
                                                            "looking for job").

## Files

- `main.py`: Collect reddit posts returned by the search query, and save them to a JSON file. Pagination of 200.
- `sentiment_topics.py`: Read and collate the reddit posts from the JSON files, preprocess the text data, extract main topics discussed using LDA, perform basic sentiment analysis on the titles, text and all comments to a post, and save the results to a JSON file.
- `visualization.py`: Pie chart of sentiment distributions over posts, and word clouds for positive, negative and neutral pharses, topic distribution with weights (LDA output).

## Usage

1. Obtain Reddit API credentials by creating an app on [Reddit's website](https://www.reddit.com/prefs/apps).
2. Add your credentials to the `config.ini` file in the following format:
    
        [credentials]
         CLIENT_ID = your_client_id
         SECRET_KEY =  your_secret_key
3. Install the required packages by running `pip install -r requirements.txt`.
3. Incrementally collect the desired number of reddit posts by running `main.py` :)
4. Run `sentiment_topics.py`, then run `sentiment.py`, then run `visualization.py` to visualize the results.