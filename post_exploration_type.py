#!/usr/bin/env python3
import datetime
import pickle
from matplotlib import pyplot as plt
from matplotlib import gridspec

num_days = 76
posttype_by_day = {'text': [0] * num_days, 'link': [0] * num_days}
linkflair_by_day = {}
linkflair_by_day_weighted = {}

baseday = (datetime.datetime(2021,1,1) - datetime.datetime(1970,1,1)).total_seconds()
def get_day(timestamp):
    return int((timestamp - baseday) / (24 * 60 * 60))

def post_get_day(post):
    return get_day(post['created_utc'])

def get_posttype(post):
    if post['url'] == post['full_link']:
        posttype = 'text'
    else:
        posttype = 'link'
    return posttype

def account_posttype(post):
    posttype = get_posttype(post)
    day = post_get_day(post)
    posttype_by_day[posttype][day] += 1

def account_linkflair(post):
    if get_posttype(post) != 'link':
        return

    if 'link_flair_text' not in post:
        flair = 'None'
    else:
        flair = post['link_flair_text']

    if flair not in linkflair_by_day:
        linkflair_by_day[flair] = [0] * num_days
        linkflair_by_day_weighted[flair] = [0] * num_days

    day = post_get_day(post)
    linkflair_by_day[flair][day] += 1
    linkflair_by_day_weighted[flair][day] += post['score']

def data_printer():
    f = plt.figure()
    ax1 = plt.subplot(211)
    ax1.plot(posttype_by_day['text'], label = 'text')
    ax1.fill_between(range(0, num_days), posttype_by_day['text'], color = 'skyblue')
    sum_by_day = [x + y for (x,y) in zip(posttype_by_day['text'], posttype_by_day['link'])]
    ax1.plot(sum_by_day, color = 'darkorange', label = 'link')
    ax1.fill_between(range(0, num_days), posttype_by_day['text'], sum_by_day, color = 'peachpuff')
    ax1.legend()
    ax1.set_ylabel('Number of posts')
    ax2 = plt.subplot(212)
    ratio_link = [((text / (link + text)) if (link + text) != 0 else 0.5) for (link, text) in zip(posttype_by_day['link'], posttype_by_day['text'])]
    ax2.plot(ratio_link)
    ax2.fill_between(range(0, num_days), ratio_link, color = 'skyblue')
    ax2.plot([1] * num_days, color = 'darkorange', label = 'link')
    ax2.fill_between(range(0, num_days), [1] * num_days, ratio_link, color = 'peachpuff')
    ax2.set_xlabel('Days since 01/01/2021')
    ax2.set_ylabel('Ratio of posts')
    f.savefig("post_count.pdf", bbox_inches='tight')
    f.savefig("post_count.png", bbox_inches='tight', dpi=300)

    categories = linkflair_by_day.keys()
    f = plt.figure()
    gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])
    ax1 = plt.subplot(gs[0])
    sum_by_day = [0] * num_days
    count = 0
    colors_line = ['crimson',   'steelblue', 'orange',   'indigo',  'tomato',    'seagreen',   'darkblue', 'olive',       'turquoise', 'deeppink', 'slategrey',      'lime',      'dimgray',   'tan',    'firebrick',  'black']
    colors_fill = ['lightpink', 'lightblue', 'moccasin', 'thistle', 'mistyrose', 'mediumseagreen', 'lavender', 'lightyellow', 'azure',     'plum',     'lightsteelblue', 'palegreen', 'gainsboro', 'bisque', 'lightcoral', 'silver']
    for category in categories:
        tmp = [((x / y) if y != 0 else (1/len(categories))) for (x,y) in zip(linkflair_by_day[category], posttype_by_day['link'])]
        tmp = [x + y for (x,y) in zip(sum_by_day, tmp)]
        ax1.plot(tmp, color = colors_line[count])
        ax1.fill_between(range(0, num_days), sum_by_day, tmp, color = colors_fill[count], label = category)
        sum_by_day = tmp
        count += 1
    ax2 = plt.subplot(gs[1])
    aggreg = {category: sum(linkflair_by_day[category]) for category in categories}
    total_link_posts = sum(aggreg.values())
    subsum = 0
    count = 0
    for category in categories:
        ax2.bar(['Aggregate'], [aggreg[category] / total_link_posts], bottom = [subsum / total_link_posts], color = colors_fill[count])
        subsum += aggreg[category] 
        count += 1
    ax1.legend(bbox_to_anchor=(1.5, 1))
    ax1.set_xlabel('Days since 01/01/2021')
    ax1.set_ylabel('Fraction of link posts')
    f.savefig('linkpost_breakdown.pdf', bbox_inches = 'tight')
    f.savefig('linkpost_breakdown.png', bbox_inches = 'tight', dpi = 300)

    categories = linkflair_by_day_weighted.keys()
    f = plt.figure()
    gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])
    ax1 = plt.subplot(gs[0])
    sum_by_day = [0] * num_days
    count = 0
    sumweighted_by_day = [0] * num_days
    for category in categories:
        sumweighted_by_day = [x + y for (x, y) in zip(sumweighted_by_day, linkflair_by_day_weighted[category])]
    for category in categories:
        tmp = [((x / y) if y != 0 else (1/len(categories))) for (x,y) in zip(linkflair_by_day_weighted[category], sumweighted_by_day)]
        tmp = [x + y for (x,y) in zip(sum_by_day, tmp)]
        ax1.plot(tmp, color = colors_line[count])
        ax1.fill_between(range(0, num_days), sum_by_day, tmp, color = colors_fill[count], label = category)
        sum_by_day = tmp
        count += 1
    ax2 = plt.subplot(gs[1])
    aggreg = {category: sum(linkflair_by_day_weighted[category]) for category in categories}
    total_link_posts = sum(aggreg.values())
    subsum = 0
    count = 0
    for category in categories:
        print('Bottom {} top {} category {}'.format(subsum / total_link_posts, (subsum + aggreg[category]) / total_link_posts, category))
        ax2.bar(['Aggregate'], [aggreg[category] / total_link_posts], bottom = [subsum / total_link_posts], color = colors_fill[count])
        subsum += aggreg[category] 
        count += 1
    ax1.legend(bbox_to_anchor=(1.5, 1))
    ax1.set_xlabel('Days since 01/01/2021')
    ax1.set_ylabel('Fraction of link posts')
    f.savefig('linkpost_breakdown_weighted.pdf', bbox_inches = 'tight')
    f.savefig('linkpost_breakdown_weighted.png', bbox_inches = 'tight', dpi = 300)



def main():
    with open('test_posts', 'rb') as fd:
        posts = pickle.load(fd)
    
    for post in posts:
        account_posttype(post)
        account_linkflair(post)

    data_printer()

    print(posttype_by_day)
    print(linkflair_by_day)
    print(linkflair_by_day_weighted)

if __name__ == '__main__':
    main()