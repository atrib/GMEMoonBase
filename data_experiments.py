#!/usr/bin/env python3
import datetime
import pandas as pd
import plotly
import plotly.express as px
import requests
import time
import math
import numpy as np
import matplotlib.pyplot as plt

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



props_for_filtering = ['author_flair_type','is_video','link_flair_css_class','link_flair_richtext','link_flair_text','num_comments',
                           'total_awards_received','score' ,'upvote_ratio', 'created_utc', 'permalink', 'removed_by_category']
n_posts = 0
n_post_w_upvotes = 0
n_posts_w_comments = 0
df_reddit_data = pd.DataFrame(columns=props_for_filtering)
while 2000 > n_posts:

    # Call the API
    data = get_pushshift_data(data_type=data_type,
                            size=size,
                            sort_type=sort_type,
                            sort=sort,
                            before=before_utc,
                            subreddit=subreddit).get('data')
    
    # Interesting details
    #props = ['author', 'id', 'upvote_ratio', 'score', 'title', 'created_utc', 'permalink']


    # Select the columns you care about
    df = pd.DataFrame.from_records(data)[props_for_filtering]
    
    # Append the string to all the permalink entries so that we have a link to the comment
    df['permalink'] = 'https://reddit.com' + df['permalink'].astype(str)



    for index, row in df.iterrows():

        if type(row['removed_by_category'])!=float:
            importance_rank = -1
        else:
            alpha = 10
            importance_rank = row['num_comments'] + alpha*row['score']


        print(type(row['removed_by_category']))


        utc = row['created_utc']
        if row['score'] >1:
            n_post_w_upvotes+=1
            #print(row)
            #print(row['permalink'])
        if row['num_comments']>0:
            #print(row)
            n_posts_w_comments+=1

        if type(row['removed_by_category'])==float:
            print(row)
            print(row['permalink'])
            n_posts_w_comments+=1




        before_utc = utc


    df_reddit_data = pd.concat([df_reddit_data,df], axis=0)
    print(n_post_w_upvotes)
    print(n_posts_w_comments)
    print()

    print('numb of post', n_posts)
    print('\n')
    n_posts+= len(df)





print(n_posts_w_comments)
print(n_post_w_upvotes)

print(df_reddit_data)

df_reddit_data['removed_by_category'] = df_reddit_data['removed_by_category'].fillna('existing')


plt.hist(df_reddit_data['score'], bins=20, density=True, log=True)
plt.title('score histogram')
plt.show()

plt.hist(df_reddit_data['num_comments'], bins=50, log=True)
plt.title('Number of comments histogram')
plt.show()

plt.hist(df_reddit_data['num_comments'], bins=50, log=True,range=(0, 100))
plt.title('Number of comments histogram without outliers')
plt.show()


print(df_reddit_data['removed_by_category'].unique())
df_agg_removed = df_reddit_data.groupby('removed_by_category').agg('count')['permalink']
print(df_agg_removed)
df_agg_removed.plot(kind='bar')
plt.title('Removed posts')
plt.show()

#first 1000 posts I 23 post with more then 1 upvote


'''author_flair_type
is_video
link_flair_css_class
link_flair_richtext
link_flair_text
num_comments
total_awards_received
score --> u-d
upvote_ratio --> u/(u+d)'''