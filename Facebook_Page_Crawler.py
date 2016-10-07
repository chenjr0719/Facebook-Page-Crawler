import requests, os, time, json
import argparse, sys
from datetime import datetime

from multiprocessing import Pool

##########################################################################################################
def getRequests(url):

    requests_result = requests.get(url, headers={'Connection':'close'}).json()
    time.sleep(0.01)

    return requests_result

##########################################################################################################
def getFeedIds(feeds, feed_list):

    feeds = feeds['feed'] if 'feed' in feeds else feeds

    for feed in feeds['data']:
        feed_list.append(feed['id'])
        if not stream:
            print('Feed found: ' + feed['id'] + '\n')
            #log.write('Feed found: ' + feed['id'] + '\n')
    
    if 'paging' in feeds and 'next' in feeds['paging']:
        feeds_url = feeds['paging']['next']
        feed_list = getFeedIds(getRequests(feeds_url), feed_list)

    return feed_list

##########################################################################################################
def getComments(comments, comments_count):

    # If comments exist.
    comments = comments['comments'] if 'comments' in comments else comments
    if 'data' in comments:

        if not stream:
            comments_dir = 'comments/'
            if not os.path.exists(comments_dir):
                os.makedirs(comments_dir)

        for comment in comments['data']:

            comment_content = {
                'id': comment['id'],
                'user_id': comment['from']['id'],
                'user_name': comment['from']['name'] if 'name' in comment['from'] else None,
                'message': comment['message'],
                'like_count': comment['like_count'] if 'like_count' in comment else None,
                'created_time': comment['created_time']
            }

            comments_count+= 1

            if stream:
                print(comment_content)
            else:
                print('Processing comment: ' + comment['id'] + '\n')
                comment_file = open(comments_dir + comment['id'] + '.json', 'w')
                comment_file.write(json.dumps(comment_content, indent = 4, ensure_ascii = False))
                comment_file.close()
                #log.write('Processing comment: ' + feed_id + '/' + comment['id'] + '\n')

        # Check comments has next or not.
        if 'next' in comments['paging']:
            comments_url = comments['paging']['next']
            comments_count = getComments(getRequests(comments_url), comments_count)

    return comments_count

##########################################################################################################
def getReactions(reactions, reactions_count_dict):

    # If reactions exist.
    reactions = reactions['reactions'] if 'reactions' in reactions else reactions
    if 'data' in reactions:

        if not stream:
            reactions_dir = 'reactions/'
            if not os.path.exists(reactions_dir):
                os.makedirs(reactions_dir)

        for reaction in reactions['data']:

            if reaction['type'] == 'LIKE':
                reactions_count_dict['like']+= 1
            elif reaction['type'] == 'LOVE':
                reactions_count_dict['love']+= 1
            elif reaction['type'] == 'HAHA':
                reactions_count_dict['haha']+= 1
            elif reaction['type'] == 'WOW':
                reactions_count_dict['wow']+= 1
            elif reaction['type'] == 'SAD':
                reactions_count_dict['sad']+= 1
            elif reaction['type'] == 'ANGRY':
                reactions_count_dict['angry']+= 1

            if stream:
                print(reaction)
            else:
                print('Processing reaction: ' + reaction['id'] + '\n')
                reaction_file = open(reactions_dir + reaction['id'] + '.json', 'w')
                reaction_file.write(json.dumps(reaction, indent = 4, ensure_ascii = False))
                reaction_file.close()
                #log.write('Processing reaction: ' + feed_id + '/' + reaction['id'] + '\n')

        # Check reactions has next or not.
        if 'next' in reactions['paging']:
            reactions_url = reactions['paging']['next']
            reactions_count_dict = getReactions(getRequests(reactions_url), reactions_count_dict)
            
    return reactions_count_dict

##########################################################################################################
def getAttachments(attachments, attachments_content):

    # If attachments exist.
    attachments = attachments['attachments'] if 'attachments' in attachments else attachments
    if 'data' in attachments:
        attachments_content['title'] = attachments['data'][0]['title'] if 'title' in attachments['data'][0] else ''
        attachments_content['description'] = attachments['data'][0]['description'] if 'description' in attachments['data'][0] else ''
        attachments_content['target'] = attachments['data'][0]['target']['url'] if 'target' in attachments['data'][0] and 'url' in attachments['data'][0]['target'] else ''

    return attachments_content

##########################################################################################################
def getFeed(feed_id):

    feed_url = 'https://graph.facebook.com/v2.7/' + feed_id

    if not stream:
        feed_dir = feed_id + '/'
        if not os.path.exists(feed_dir):
            os.makedirs(feed_dir)

        os.chdir(feed_dir)

        print('\nProcessing feed: ' + feed_id + '\nAt: ' + datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') + '\n')
        log = open('../log', 'a')
        log.write('\nProcessing feed: ' + feed_id + '\nAt: ' + datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S') + '\n')
        log.close()

    # For comments.
    comments_url = feed_url + '?fields=comments.limit(100)&' + token
    comments_count = getComments(getRequests(comments_url), 0)

    # For reactions.
    if get_reactions:
        reactions_count_dict = {
            'like': 0,
            'love': 0,
            'haha': 0,
            'wow': 0,
            'sad': 0,
            'angry': 0
        }
        reactions_url = feed_url + '?fields=reactions.limit(100)&' + token
        reactions_count_dict = getReactions(getRequests(reactions_url), reactions_count_dict)
    
    # For attachments.
    attachments_content = {
        'title': '',
        'description': '',
        'target': ''
    }
    attachments_url = feed_url + '?fields=attachments&' + token
    attachments_content = getAttachments(getRequests(attachments_url), attachments_content)

    # For feed content.
    feed = getRequests(feed_url + '?' + token)

    if 'message' in feed:
        feed_content = {
            'id': feed['id'],
            'message': feed['message'],
            'link': feed['link'] if 'link' in feed else None,
            'created_time': feed['created_time'],
            'comments_count': comments_count
        }

        feed_content.update(attachments_content)

        if get_reactions:
            feed_content.update(reactions_count_dict)

        if stream:
            print(feed_content)
        else:
            feed_file = open(feed_id + '.json', 'w')
            feed_file.write(json.dumps(feed_content, indent = 4, ensure_ascii = False))
            feed_file.close()

    os.chdir('../')

##########################################################################################################
if __name__ == '__main__':
    # Set crawler target and parameters.
    parser = argparse.ArgumentParser()

    parser.add_argument("target", help="Set the target fans page you want to crawling. Ex: 'appledaily.tw'")
    parser.add_argument("since", help="Set the start date you want to crawling. Format: 'yyyy-mm-dd HH:MM:SS'")
    parser.add_argument("until", help="Set the end date you want to crawling. Format: 'yyyy-mm-dd HH:MM:SS'")

    parser.add_argument("-r", "--reactions", help="Collect reactions or not. Default is no.")
    parser.add_argument("-s", "--stream", help="If yes, this crawler will turn to streaming mode.")

    args = parser.parse_args()

    target = str(args.target)
    since = str(args.since)
    until = str(args.until)

    if args.reactions == 'yes':
        get_reactions = True
    else:
        get_reactions = False

    if args.stream == 'yes':
        stream = True
    else:
        stream = False

    app_id = 'YOUR_APP_ID'
    app_secret = 'YOUR_APP_SECRET'

    token = 'access_token=' + app_id + '|' + app_secret

    #Create a directory to restore the result if not in stream mode.
    if not stream:
        result_dir = 'Result/' + target + '/'

        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        os.chdir(result_dir)

        log = open('log', 'w')
        start_time = datetime.now()
        execution_start_time = time.time()
        print('Task start at:' + datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S') + '\nTaget: ' + target + '\nSince: ' + since + '\nUntil: ' + until + '\n')
        log.write('Task start at:' + datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S') + '\nTaget: ' + target + '\nSince: ' + since + '\nUntil: ' + until + '\n')
        log.close()

    #Get list of feed id from target.
    feeds_url = 'https://graph.facebook.com/v2.7/' + target + '/?fields=feed.limit(100).since(' + since +').until(' + until + '){id}&' + token
    feed_list = getFeedIds(getRequests(feeds_url), [])

    if not stream:
        feed_list_file = open('feed_ids', 'w')

        for id in feed_list:
            feed_list_file.write(id + '\n')

        feed_list_file.close()

    #Get message, comments and reactions from feed.
    p = Pool()
    p.map(getFeed, feed_list)

    if not stream:
        end_time = datetime.now()
        cost_time = time.time() - execution_start_time
        print('\nTask end Time: ' + datetime.strftime(end_time, '%Y-%m-%d %H:%M:%S') + '\nTime Cost: ' + str(cost_time))
        log = open('log', 'a')
        log.write('\nTask end Time: ' + datetime.strftime(end_time, '%Y-%m-%d %H:%M:%S') + '\nTime Cost: ' + str(cost_time))
        log.close()

