#!/usr/bin/env python3
import pickle
import os
import os.path
import shutil
from multiprocessing import Pool

posts_by_id = {}

def process_post(inp_dir, post):
  srcfile = f'{inp_dir}/{post}'
  post_comment_rels = []
  comment_comment_rels = []
  with open(srcfile, 'rb') as srcfd:
    comments = pickle.load(srcfd)
    # Remove all deleted comments
    comments = [comment for comment in comments if comment['body'] != '[removed]']
    # Create dict of comments by id
    comments_by_id = {comment['id']: comment for comment in comments}
    # List of all (id, parent_id) relations
    rels = [(comment['id'], comment['parent_id']) for comment in comments]

    for (comment_id, parent_id_full) in rels:
      parent_id_trunc = parent_id_full[3:]
      comment = comments_by_id[comment_id]
      comment_author = comment['author']
      
      if post == parent_id_trunc:
        post_author = posts_by_id[post]['author']
        post_comment_rels.append((comment_id, comment_author, parent_id_trunc, post_author))
      elif parent_id_trunc in comments_by_id:
        parent_comment_author = comments_by_id[parent_id_trunc]['author']
        comment_comment_rels.append((comment_id, comment_author, parent_id_trunc, parent_comment_author))
    
  return (post_comment_rels, comment_comment_rels)

def main():
  global posts_by_id
  inp_dir = 'comments'
  out_dir = 'comments_relations'

  posts = pickle.load(open('test_posts', 'rb'))
  posts_by_id = {post['id']: post for post in posts}

  # Basic checks
  if not (os.path.exists(inp_dir) and os.path.isdir(inp_dir)):
    print('No input dir')
    return

  if os.path.exists(out_dir):
    if os.path.isdir(out_dir):
      shutil.rmtree(out_dir)
    else:
      print('Output dir exists, but not as dir')
      return
  os.mkdir(out_dir)

  post_comment_rels = []
  comment_comment_rels = []

  file_list = os.listdir(inp_dir)
  count = 0
  last_perc = -1
  for file in file_list:
    (post_comment_rels_post, comment_comment_rels_post) = process_post(inp_dir, file)
    post_comment_rels.extend(post_comment_rels_post)
    comment_comment_rels.extend(comment_comment_rels_post)

    count += 1
    perc = int(count * 100 / len(file_list))
    if perc != last_perc:
      print(f'Done {perc}%')
      last_perc = perc


  out_tc_rels_filename = f'{out_dir}/post_comments'
  with open(out_tc_rels_filename, 'wb') as fd:
    pickle.dump(post_comment_rels, fd)

  out_cc_rels_filename = f'{out_dir}/comment_comments'
  with open(out_cc_rels_filename, 'wb') as fd:
    pickle.dump(comment_comment_rels, fd)

if __name__ == '__main__':
  main()