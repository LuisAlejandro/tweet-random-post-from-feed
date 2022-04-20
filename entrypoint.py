# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
# Copyright (C) 2020-2022 Luis Alejandro Martínez Faneyth.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import datetime
from urllib.request import urlopen
from html import unescape
from random import choice

from atoma import parse_rss_bytes
from tweepy import OAuth1UserHandler, API


count = 0
json_index_content = {}
consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
oauth_token = os.environ.get('TWITTER_OAUTH_TOKEN')
oauth_secret = os.environ.get('TWITTER_OAUTH_SECRET')
feed_url = os.environ.get('FEED_URL')
max_post_age = int(os.environ.get('MAX_POST_AGE', 365))

if not feed_url:
    raise Exception('No FEED_URL provided.')

auth = OAuth1UserHandler(consumer_key, consumer_secret,
                         oauth_token, oauth_secret)
api = API(auth, wait_on_rate_limit=True)

feed_data = parse_rss_bytes(urlopen(feed_url).read())
today = datetime.datetime.now()
max_age_delta = today - datetime.timedelta(days=max_post_age)
max_age_timestamp = int(max_age_delta.strftime('%Y%m%d%H%M%S'))

for post in feed_data.items:

    item_timestamp = int(post.pub_date.strftime('%Y%m%d%H%M%S'))

    if item_timestamp > max_age_timestamp:

        json_index_content[str(item_timestamp)] = {
            'title': post.title,
            'url': post.guid,
            'date': post.pub_date
        }

random_post_id = choice(list(json_index_content.keys()))
random_post_title = json_index_content[random_post_id]['title']
status_text = '{0} {1}#{2}'.format(
    unescape(random_post_title),
    json_index_content[random_post_id]['url'],
    today.strftime('%Y%m%d%H%M%S'))

api.update_status(status_text)
