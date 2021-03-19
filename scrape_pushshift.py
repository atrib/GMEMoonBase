#!/usr/bin/env python3
import datetime
import pandas as pd
import plotly.express as px
import requests
import time

def get_pushshift_data(data_type, **kwargs):
    '''
    Gets data from the pushshift api.
 
    data_type can be 'comment' or 'submission'
    The rest of the args are interpreted as payload.
 
    Read more: https://github.com/pushshift/api
    '''
 
    base_url = f'https://api.pushshift.io/reddit/search/{data_type}/'
    payload = kwargs

    success = False
    while not success:
        try:
            request = requests.get(base_url, params=payload)
            reply = request.json()
            success = True
        except:
            success = False

    return reply

def getDateAndTime(seconds=None):
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(seconds))

data_type='submission'          # give me comments, use 'submission' to publish something
query='python'               # Add your query
size=400                    # maximum 1000 comments
sort_type='created_utc'      # Sort by score (Accepted: 'score', 'num_comments', 'created_utc')
sort='desc'                  # sort descending
subreddit='Wallstreetbets'   # From particular subreddit

before_utc = int(time.time())
dt = datetime.datetime(2021, 1, 1)
after_utc = dt.replace(tzinfo=datetime.timezone.utc).timestamp()

while before_utc > after_utc:
    # Call the API
    data = get_pushshift_data(data_type=data_type,
                            size=size,
                            sort_type=sort_type,
                            sort=sort,
                            before=before_utc,
                            subreddit=subreddit).get('data')
    
    # Interesting details
    props = ['author', 'id', 'upvote_ratio', 'score', 'title', 'created_utc', 'permalink']

    # Select the columns you care about
    df = pd.DataFrame.from_records(data)[props]
    
    # Append the string to all the permalink entries so that we have a link to the comment
    df['permalink'] = 'https://reddit.com' + df['permalink'].astype(str)
    
    for index, row in df.iterrows():
        utc = row['created_utc']
        for prop in props:
            if prop == 'created_utc':
                print('{}: {} {}'.format(prop, row[prop], getDateAndTime(row[prop])))
            else:
                print('{}: {}'.format(prop, row[prop]))
        before_utc = utc
