#!/usr/bin/env python3
 
import praw
import pandas as pd
import datetime as dt

def init() :
  global reddit
  reddit = praw.Reddit(
      client_id="oP8QNoFSN5ho4g",
      client_secret="meofmFup3PnfKkM-Jh9IPnVncw9fTQ",
      redirect_uri="http://localhost:8081",
      user_agent="DH500",
  )

def get_posts(sub, type, limit = 10):
  global reddit
  if type == 'hot':
    posts = reddit.subreddit(sub).hot(limit)
  elif type == 'new':
    posts = reddit.subreddit(sub).new()

  for post in posts:
      print(post.title)

def main():
  init()
  get_posts('WallstreetBets', 'new')
  get_posts('WallstreetBets', 'new')

if __name__ == '__main__':
  main()
