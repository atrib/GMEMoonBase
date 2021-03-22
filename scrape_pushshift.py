#!/usr/bin/env python3
import csv
import datetime
import pandas as pd
import pickle
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

def get_data(after_utc, before_utc, data_filter):
    data_type='submission'          # give me comments, use 'submission' to publish something
    query='python'               # Add your query
    size=400                    # maximum 1000 comments
    sort_type='created_utc'      # Sort by score (Accepted: 'score', 'num_comments', 'created_utc')
    sort='desc'                  # sort descending
    subreddit='Wallstreetbets'   # From particular subreddit

    net_data = []
    total_post_count = 0
    saved_post_count = 0
    while before_utc > after_utc:
        # Call the API
        data = get_pushshift_data(data_type=data_type,
                                size=size,
                                sort_type=sort_type,
                                sort=sort,
                                before=before_utc,
                                subreddit=subreddit).get('data')
        
        total_post_count += len(data)
        # Take timestamp of oldest post for next query
        before_utc = data[-1]['created_utc']
        # Filter out important posts
        data = [x for x in data if data_filter(x)]
        saved_post_count += len(data)
        # Append the string to all the permalink entries so that we have a link to the comment
        for x in data:
            x['permalink'] = 'https://reddit.com' + x['permalink']

        net_data.extend(data)

        if(len(data) > 0):
            last_post = data[-1]
            print('{}: {} {}'.format(last_post['id'], getDateAndTime(last_post['created_utc']), last_post['title']))
            print('{}/{} posts'.format(saved_post_count, total_post_count))
        # for index, row in df.iterrows():
        #     utc = row['created_utc']
        #     for prop in props:
        #         if prop == 'created_utc':
        #             print('{}: {} {}'.format(prop, row[prop], getDateAndTime(row[prop])))
        #         else:
        #             print('{}: {}'.format(prop, row[prop]))
        #     before_utc = utc

    return net_data

def aurel_first_filter(record, threshold = 12.0):
    return aurel_first_score(record) > threshold

def aurel_first_score(record):
    if 'removed_by_category' in record:
        importance_rank = -1
    # elif type(record['removed_by_category']) != float:
    #     importance_rank = -1
    # else:
    alpha = 10
    importance_rank = record['num_comments'] +    alpha*record['score']

    return importance_rank
    

def main():

    start_utc = datetime.datetime(2021, 1, 1).replace(tzinfo=datetime.timezone.utc).timestamp()
    end_utc = int(time.time())
    
    posts = get_data(start_utc, end_utc, aurel_first_filter)

    # Dump list of importance as calculated by aurel into a csv
    importances = [aurel_first_score(x) for x in posts]
    with open('test_importances.csv', 'w') as file:
        csv.writer(file).writerow(importances)

    # Store full list of posts in pickle
    with open('test_posts', 'wb') as file:
        pickle.dump(posts, file)

if __name__ == '__main__':
    main()