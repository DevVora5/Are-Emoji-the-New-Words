import csv
import os
import re
import logging
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize logging
logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Regular expression to detect emojis
emoji_pattern = re.compile(
    "[" 
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "]+", flags=re.UNICODE)

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Input file
input_csv = "sample_data.csv"

# Ensure the output directory exists
output_dir = "Outputs"
os.makedirs(output_dir, exist_ok=True)

# Output CSV file path for sentiment analysis results
output_csv = os.path.join(output_dir, "output_sample_data.csv")

# Store the compound scores to calculate averages
compound_scores = []
compound_scores_with_emojis = []
compound_scores_without_emojis = []

# Variables for tracking statistics
highest_likes = float('-inf')
lowest_likes = float('inf')
highest_retweets = float('-inf')
lowest_retweets = float('inf')
tweet_count_processed = 0
total_likes = 0
total_retweets = 0
total_emoji_count = 0

# Counters for tweets with different emoji counts
emoji_0_count = 0
emoji_1_count = 0
emoji_2_count = 0
emoji_3_count = 0
emoji_4_count = 0
emoji_more_than_4_count = 0

# Read data and perform sentiment analysis
with open(input_csv, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)

    with open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['text', 'neg', 'neu', 'pos', 'compound', 'emoji_count']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            text = row['Text']
            sentiment = analyzer.polarity_scores(text)
            compound_scores.append(sentiment['compound'])

            # Count emojis
            emoji_count = len(emoji_pattern.findall(text))
            total_emoji_count += emoji_count

            # Categorize tweets based on emoji usage
            if emoji_count > 0:
                compound_scores_with_emojis.append(sentiment['compound'])
            else:
                compound_scores_without_emojis.append(sentiment['compound'])

            if emoji_count == 0:
                emoji_0_count += 1
            elif emoji_count == 1:
                emoji_1_count += 1
            elif emoji_count == 2:
                emoji_2_count += 1
            elif emoji_count == 3:
                emoji_3_count += 1
            elif emoji_count == 4:
                emoji_4_count += 1
            else:
                emoji_more_than_4_count += 1

            # Get likes and retweets
            likes = int(row['Likes'])
            retweets = int(row['Retweets'])

            highest_likes = max(highest_likes, likes)
            lowest_likes = min(lowest_likes, likes)
            highest_retweets = max(highest_retweets, retweets)
            lowest_retweets = min(lowest_retweets, retweets)

            total_likes += likes
            total_retweets += retweets
            tweet_count_processed += 1

            # Write results to output file
            writer.writerow({
                'text': text,
                'neg': sentiment['neg'],
                'neu': sentiment['neu'],
                'pos': sentiment['pos'],
                'compound': sentiment['compound'],
                'emoji_count': emoji_count
            })

# Calculate averages
avg_compound = sum(compound_scores) / len(compound_scores) if compound_scores else 0
avg_compound_with_emojis = sum(compound_scores_with_emojis) / len(compound_scores_with_emojis) if compound_scores_with_emojis else 0
avg_compound_without_emojis = sum(compound_scores_without_emojis) / len(compound_scores_without_emojis) if compound_scores_without_emojis else 0
avg_likes = total_likes / tweet_count_processed if tweet_count_processed else 0
avg_retweets = total_retweets / tweet_count_processed if tweet_count_processed else 0
avg_emoji_count = total_emoji_count / tweet_count_processed if tweet_count_processed else 0

# Summary file path
summary_csv = os.path.join(output_dir, "sentiment_summary.csv")

# Check if the summary file exists, if not, create it and add headers
file_exists = os.path.isfile(summary_csv)

with open(summary_csv, mode='a', newline='', encoding='utf-8') as summary_file:
    fieldnames = [
        'query', 'date', 'average_compound', 'highest_likes', 'lowest_likes', 'highest_retweets', 
        'lowest_retweets', 'tweet_count', 'average_likes', 'average_retweets', 
        'avg_compound_with_emojis', 'avg_compound_without_emojis', 'avg_emoji_count',
        'emoji_0_count', 'emoji_1_count', 'emoji_2_count', 'emoji_3_count', 'emoji_4_count', 'emoji_more_than_4_count'
    ]
    writer = csv.DictWriter(summary_file, fieldnames=fieldnames)

    if not file_exists:
        writer.writeheader()

    writer.writerow({
        'query': 'sample_data',
        'date': datetime.now().strftime("%d-%m-%Y"),
        'average_compound': avg_compound,
        'highest_likes': highest_likes,
        'lowest_likes': lowest_likes,
        'highest_retweets': highest_retweets,
        'lowest_retweets': lowest_retweets,
        'tweet_count': tweet_count_processed,
        'average_likes': avg_likes,
        'average_retweets': avg_retweets,
        'avg_compound_with_emojis': avg_compound_with_emojis,
        'avg_compound_without_emojis': avg_compound_without_emojis,
        'avg_emoji_count': avg_emoji_count,
        'emoji_0_count': emoji_0_count,
        'emoji_1_count': emoji_1_count,
        'emoji_2_count': emoji_2_count,
        'emoji_3_count': emoji_3_count,
        'emoji_4_count': emoji_4_count,
        'emoji_more_than_4_count': emoji_more_than_4_count
    })

logging.info(f'Sentiment analysis completed. Results saved to {output_csv}')
logging.info(f'Query and summary appended to {summary_csv}')
