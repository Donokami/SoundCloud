# -*- coding: utf-8 -*-

"""Download a single track"""

import urllib, re, os.path, soundcloud
import utils
import eyed3
import eyed3.id3

def download_from_url(client_id, track_url, dir, override=False):
    """Download from URL"""
    client = soundcloud.Client(client_id=client_id)
    track = client.get('/resolve', url=track_url)
    download(client, track, dir, override)


def download_from_id(client_id, track_id, dir, override=False):
    """Download using the song id"""
    client = soundcloud.Client(client_id=client_id)
    track = client.get('/tracks/%d' % track_id, allow_redirects=False)
    download(client, track, dir, override)


def download(client, track, dir, override=False):
    """Download a track using the given SC client"""
    title = fix_title(track.title, track.user['username'])
    print '"%s"' % title
    if not dir: dir = 'mp3'
    utils.create_dir(dir)
    file_name = utils.build_file_name(dir, title)

    if not override and os.path.exists(file_name):
        print "File already exists, skipped"
        return False

    stream_url = client.get(track.stream_url, allow_redirects=False)
    urllib.urlretrieve(stream_url.location, file_name)
    if track.artwork_url is None:
        track.artwork_url = track.user['avatar_url']
    track.artwork_url = track.artwork_url.replace("-large.", "-t500x500.", 1)
    track.artwork_url = track.artwork_url.replace("https:", "http:", 1)
    imagedata = urllib.urlopen(track.artwork_url).read()
    audiofile = eyed3.load(file_name)
    audiofile.tag = eyed3.id3.Tag()
    audiofile.tag.file_info = eyed3.id3.FileInfo(file_name)
    audiofile.tag.images.set(3,imagedata,"image/jpeg")
    audiofile.tag.artist = u"%s" % track.user['username']
    audiofile.tag.album = u"%s" % track.user['username']
    audiofile.tag.album_artist = u"%s" % track.user['username']
    audiofile.tag.title = u"%s" % track.title
    audiofile.tag.save()
    return True


def fix_title(title, user_name):
    """Fix title (missing space, illegal chars, missing author)"""
    # Add missing dash
    title = re.sub(r"^(.*\S)- (.*)$", r"\1 - \2", title)

    # Remove adds
    title = title.split('//', 1)[0]

    # Prepend username if author seems to be missing
    if ' - ' not in title:
        title = '%s - %s' % (user_name, title)

    return title.strip()
