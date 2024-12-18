from flask import Flask, render_template, request, send_file
import os
import json
import re
import csv
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file uploads
@app.route('/upload', methods=['POST'])
def upload_file():

    file = request.files['file']

    if file.filename == '':
        return "No selected file", 400

    if file and file.filename.endswith('.js'):
        # Save uploaded file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename) #Set file Directory
        file.save(file_path)

        # Process file
        output_csv = process_tweets(file_path)

        # Send the generated CSV as a downloadable file user
        return send_file(output_csv, as_attachment=True)

    return "Invalid file type. Please upload a .js file.", 400

# Functions to process tweets and generate CSV
def process_tweets(file):
    tweets = parse_tweets(file)
    sorted_tweets = sort_tweets(tweets)
    return write_tweets_to_csv(sorted_tweets)

def parse_tweets(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        content = file.read()

    if content.startswith("window.YTD.tweets.part0 ="):
        content = content.replace("window.YTD.tweets.part0 =", "").strip()

    tweets = json.loads(content)
    parsed_tweets = []

    for tweet in tweets:
        try:
            tweet_text = tweet['tweet']['full_text']
            text = re.sub(r'https?://\S+', '', tweet_text).strip()
        except (KeyError, TypeError):
            text = None

        try:
            tweet_time = tweet['tweet']['created_at']
            parsed_datetime = datetime.strptime(tweet_time, "%a %b %d %H:%M:%S +0000 %Y")
        except (KeyError, TypeError, ValueError):
            parsed_datetime = None

        if parsed_datetime:
            formatted_date = parsed_datetime.strftime("%Y %b %d, %a")

            urls = tweet['tweet']['entities'].get('urls', [])
            media = tweet['tweet']['entities'].get('media', [])

            if urls:
                link = urls[0].get('expanded_url') or urls[0].get('url')
            elif media:
                link = media[0].get('expanded_url') or media[0].get('url')
            else:
                link = "No link available"

            parsed_tweets.append({
                'date': parsed_datetime,
                'formatted_date': formatted_date,
                'text': text,
                'link': link
            })

    return parsed_tweets

def sort_tweets(tweets):
    return sorted(
        tweets,
        key=lambda x: x['date'] or datetime.min,
        reverse=True
    )

def write_tweets_to_csv(tweets):
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'tweets.csv')
    with open(output_path, 'w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["Date", "Time", "Tweet", "Links"])

        for tweet in tweets:
            csv_writer.writerow([
                tweet['formatted_date'],
                tweet['date'].strftime("%H:%M:%S") if tweet['date'] else "",
                tweet['text'],
                tweet['link']
            ])

    return output_path

if __name__ == '__main__':
    app.run(debug=True)