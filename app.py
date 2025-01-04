from flask import Flask, render_template, request, send_file, after_this_request
from werkzeug.utils import secure_filename
import io
import os
import json
import re
import csv
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')

    if not file or file.filename == '':
        return "No selected file", 400

    if file and file.filename.endswith('.js'):
    
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        try:
            # Save uploaded file
            file.save(file_path)

            # Process file and generate CSV 
            csv_data = process_tweets(file_path)

            # Schedule file cleanup
            @after_this_request
            def cleanup(response):
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"Deleted uploaded file: {file_path}", flush=True)
                except Exception as e:
                    print(f"Error during cleanup: {e}", flush=True)
                return response

            # Send the generated CSV as a downloadable file
            return send_file(
                io.BytesIO(csv_data),
                as_attachment=True,
                download_name='your_tweets.csv',
                mimetype='text/csv'
            )

        except Exception as e:
            print(f"Error during file processing: {e}", flush=True)
            return "An error occurred while processing the file.", 500

    return "Invalid file type. Please upload a .js file.", 400


#Process list of dicts to CSV
def process_tweets(file):
    tweets = parse_tweets(file)
    sorted_tweets = sort_tweets(tweets)

<<<<<<< HEAD
    # Write CSV data to a BytesIO object
=======
      # Write CSV data to a BytesIO object
>>>>>>> 6d2158a722c0676d2d9e61ee659c6f031acec35b
    '''(I have no idea how Bytes IO works. Credits to GPT for making this part work. 
    I needed it avoid file locking by not writing the CSV file to disk in the first place lol)'''
    output = io.StringIO()
    csv_writer = csv.writer(output)
    csv_writer.writerow(["Date", "Time", "Tweet", "Links"])

    for tweet in sorted_tweets:
        csv_writer.writerow([
            tweet['formatted_date'],
            tweet['date'].strftime("%H:%M:%S") if tweet['date'] else "",
            tweet['text'],
            tweet['link']
        ])

    return output.getvalue().encode('utf-8')

#Parses the tweets from the JSON file into a list of dictionaries
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

#Sorts the tweets by date in descending order
def sort_tweets(tweets):
    """Sorts tweets by date in descending order."""
    return sorted(
        tweets,
        key=lambda x: x['date'],
        reverse=True
    )


if __name__ == '__main__':
    app.run(debug=True)
