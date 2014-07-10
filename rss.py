#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                    Version 2, December 2004
#
# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>
#
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#  0. You just DO WHAT THE FUCK YOU WANT TO.


import feedparser
import urllib
import pickle
import cgi
import hashlib
import os.path

FEEDS = [
       "http://www.nyaa.se/?page=rss&cats=1_37&filter=2&term=Akame+ga+Kill+Horrible+1080p",
    ]

DOWNLOAD_DIR = "Torrents"
TIMESTAMP    = "rsstorrent.stamp"
OLD_DATA     = dict()
NEW_DATA     = dict()


# Load data
try:
    with open(TIMESTAMP, 'rb') as f:
        # The protocol version used is detected automatically, so we do not
        # have to specify it.
        OLD_DATA = pickle.load(f)
except FileNotFoundError:
    pass


for feed in FEEDS:

    # Hooray feedparser
    d = feedparser.parse(feed)
    entries = d.entries

    # We are using the MD5 hash of the url, and of the name of the newest entry to determine if there's new elements or not
    torrend_feed_md5 = hashlib.md5(feed.encode('utf-8')).hexdigest()
    torrent_last_title_md5 = hashlib.md5(entries[0].title.encode('utf-8')).hexdigest()

    # If the feed is new, we don't want to download all the torrents file of the feed
    if torrend_feed_md5 not in OLD_DATA:
        OLD_DATA[torrend_feed_md5] = torrent_last_title_md5

    # So, if there's new elements :
    if torrent_last_title_md5 != OLD_DATA[torrend_feed_md5]:

        for entry in entries:

            # We compare the actual entry title to the last entry title checked last time
            if(hashlib.md5(entry.title.encode('utf-8')).hexdigest() == OLD_DATA[torrend_feed_md5]):
                break;        

            """ And we download the torrent file """
            torrent_file = urllib.request.urlopen(entry.link)
            _, params = cgi.parse_header(torrent_file.headers.get('Content-Disposition', ''))

            with open(os.path.join(DOWNLOAD_DIR, params['filename']), 'b+w') as f:
                f.write(torrent_file.read())
            """ That's it ! """
        
        # So, we can finally store de first element
        OLD_DATA[torrend_feed_md5] = hashlib.md5(entries[0].title.encode('utf-8')).hexdigest()

# And we don't forget to save changes
with open(TIMESTAMP, 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(OLD_DATA, f, pickle.HIGHEST_PROTOCOL)
