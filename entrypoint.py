#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import base64
import hmac
import hashlib
from random import getrandbits, choice
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from datetime import datetime

from atoma import parse_rss_bytes

from utils import u, html_unescape, escape, filter_json_index_by_year

json_index_content = {}
twitter_api_version = '1.0'
twitter_api_method = 'HMAC-SHA1'
twitter_api_end = 'https://api.twitter.com/1.1/statuses/update.json'
twitter_consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
twitter_consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
twitter_oauth_token = os.environ.get('TWITTER_OAUTH_TOKEN')
twitter_oauth_secret = os.environ.get('TWITTER_OAUTH_SECRET')
feed_url = os.environ.get('FEED_URL')
feed_data = parse_rss_bytes(urlopen(feed_url).read())

current_timestamp = int(datetime.now().strftime('%Y%m%d%H%M%S'))
current_hour = int(datetime.now().strftime('%H'))

if current_hour not in [2, 6, 9, 14, 17, 21]:
    print('Script wasnt called in a recommended hour. Aborting.')
    sys.exit(0)

for post in feed_data.items:
    post_timestamp = post.pub_date.strftime('%Y%m%d%H%M%S')
    json_index_content[post_timestamp] = {
        'title': post.title,
        'url': post.guid,
        'date': post.pub_date
    }

json_index_filtered = filter_json_index_by_year(json_index_content)

if not json_index_filtered:
    print('There are no posts to publish. Aborting.')
    sys.exit(0)

random_post_id = choice(list(json_index_filtered.keys()))
random_post_title = json_index_content[random_post_id]['title']
random_post_title = u(html_unescape(random_post_title))
random_post_url = u('{0}#{1}'.format(
    json_index_filtered[random_post_id]['url'],
    current_timestamp))

twitter_status = '{0} {1}'.format(random_post_title, random_post_url)

signature_timestamp = datetime.now().strftime('%s')
signature_once = str(getrandbits(64))
signature_basestr_auth = {}
signature_basestr_auth['status'] = twitter_status
signature_basestr_auth['oauth_consumer_key'] = twitter_consumer_key
signature_basestr_auth['oauth_nonce'] = signature_once
signature_basestr_auth['oauth_signature_method'] = twitter_api_method
signature_basestr_auth['oauth_timestamp'] = signature_timestamp
signature_basestr_auth['oauth_token'] = twitter_oauth_token
signature_basestr_auth['oauth_version'] = twitter_api_version

signature_basestr_auth = ['{0}={1}'.format(escape(k), escape(v))
                          for k, v in sorted(signature_basestr_auth.items())]
signature_basestr_auth = '&'.join(signature_basestr_auth)

signature_basestr = 'POST&{0}&{1}'.format(escape(twitter_api_end),
                                          escape(signature_basestr_auth))
signature_key = '{0}&{1}'.format(twitter_consumer_secret,
                                 escape(twitter_oauth_secret))

oauth_hmac_hash = hmac.new(signature_key.encode(), signature_basestr.encode(),
                           hashlib.sha1)
oauth_signature = base64.b64encode(oauth_hmac_hash.digest()).decode()

oauth_header = {}
oauth_header['oauth_consumer_key'] = twitter_consumer_key
oauth_header['oauth_nonce'] = signature_once
oauth_header['oauth_signature'] = oauth_signature
oauth_header['oauth_signature_method'] = twitter_api_method
oauth_header['oauth_timestamp'] = signature_timestamp
oauth_header['oauth_token'] = twitter_oauth_token
oauth_header['oauth_version'] = twitter_api_version

oauth_header = ['{0}="{1}"'.format(escape(k), escape(v))
                for k, v in sorted(oauth_header.items())]
oauth_header = ', '.join(oauth_header)
oauth_header = 'OAuth {0}'.format(oauth_header)

http_headers = {'Authorization': oauth_header,
                'Content-Type': 'application/x-www-form-urlencoded'}
http_request = Request(url=twitter_api_end,
                       data=urlencode({'status': twitter_status}).encode(),
                       headers=http_headers)

count = 0
while count < 6:
    try:
        result = json.loads(str(urlopen(http_request).read(), 'utf-8'))
    except Exception as e:
        print('There was an error publishing: {0}'.format(e))
        count += 1
        continue

    if 'errors' in result:
        count += 1
        continue

    print('Successfully published!: {0}'.format(random_post_url))
    break
