#!/usr/bin/env python3
import csv
import os
import pickle
import requests
import time
from matplotlib import pyplot as plt
from multiprocessing import Pool

def getDateAndTime(seconds=None):
  return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(seconds))

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
      print('retrying')
      success = False

  return reply

def worker_func(posts):
  for post in posts:
    fetch_comments(post)

def fetch_comments(link_id):
  filename = 'comments/{}'.format(link_id)
  if os.path.exists(filename):
    return
  data_type='comment'         # give me comments, use 'submission' to publish something
  limit=200                     # maximum 1000 comments
  sort_type='created_utc'      # Sort by score (Accepted: 'score', 'num_comments', 'created_utc')
  sort='desc'                  # sort descending

  before_utc = int(time.time())
  comments = []
  fetched = 0
  while True:
    # Call the API
    data = get_pushshift_data(data_type=data_type,
                              limit=limit,
                              sort_type=sort_type,
                              sort=sort,
                              before=before_utc,
                              link_id = link_id).get('data')

    if len(data) == 0:
      break

    fetched += len(data)
    # print(fetched)
    before_utc = data[-1]['created_utc']
    # Append the string to all the permalink entries so that we have a link to the comment
    for x in data:
      x['permalink'] = 'https://reddit.com' + x['permalink']
    comments.extend(data)

  with open(filename, 'wb') as file:
    pickle.dump(comments, file)

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
  # Load post data
  posts = pickle.load(open('test_posts', 'rb'))
  scores = [aurel_first_score(x) for x in posts]

  # Sort by score
  zipped_posts = zip(scores, posts)
  sorted_posts = list(reversed(sorted(zipped_posts, key = lambda x: x[0])))
  filter_posts = [x for x in sorted_posts if 'removed_by_category' not in x[1]]

  # Fetch by score (highest to lowest)
  # print('{} comments total'.format(sum([x[1]['num_comments'] for x in sorted_posts])))

  # Try ot make output directory
  try:
    os.mkdir('comments', mode = 555)
  except FileExistsError as e:
    pass

  n_threads = 2
  work_queues = [[] for _ in range(n_threads)]
  for i in range(len(filter_posts)):
    work_queues[i % n_threads].append(filter_posts[i][1]['id'])
  with Pool(n_threads) as p:
    p.map(worker_func, work_queues)

if __name__ == '__main__':
  main()