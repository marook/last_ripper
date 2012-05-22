import pylast
import gdata.youtube.service
import os
import codecs
import re

def getTopTracks(user):
    foundTracks = set()

    for period in ['7day', '3month', '6month', '12month', 'overall']:
        for item in user.get_top_tracks(period = period):
            if item.item in foundTracks:
                continue

            foundTracks.add(item.item)

            yield item.item

class GetVideosService(object):

    def __init__(self, youTubeService):
        self.youTubeService = youTubeService

    def getVideos(self, artistName, trackName):
        query = gdata.youtube.service.YouTubeVideoQuery()
        query.vq = ('%s %s' % (trackName, artistName)).encode('ascii', 'replace')
        query.racy = 'include'
        query.max_results = 5
        query.time = 'this_month'

        return self.youTubeService.YouTubeQuery(query).entry

class VideoUrlParser(object):

    def __init__(self):
        self.pattern = re.compile('.*v=([^&]*)&.*')

    def parse(self, url):
        m = self.pattern.match(url)

        if(not m):
            raise Exception('Can\'t parse video URL: ' + url)

        return {
            'id': m.group(1)
            }

def escapePathForMakefile(path):
    return path.replace(' ', '_').replace("'", '')

class MakefileWriter(object):

    def __init__(self, file):
        self.file = file

    def writeNewLine(self):
        self.file.write('\n')

    def writeVar(self, name, value):
        self.file.write(name)
        self.file.write('=')
        self.file.write(value)
        self.writeNewLine()

    def writeTarget(self, target, dependencies = []):
        self.writeNewLine()
        self.file.write(target)
        self.file.write(': ')
        self.file.write(' '.join(dependencies))
        self.writeNewLine()

    def writeRule(self, rule):
        self.file.write('\t')
        self.file.write(rule)
        self.writeNewLine()

def getVideoTarget(videoUrlParser, video):
    videoId = videoUrlParser.parse(video.media.player.url)['id']

    return 'download/%s/%s.mp3' % (videoId, videoId)

def main():
    import argparse

    parser = argparse.ArgumentParser(description = 'ripps your last.fm tracks from youtube')
    parser.add_argument('--api-key', dest = 'apiKey', help = 'your last.fm API key')
    parser.add_argument('--api-secret', dest = 'apiSecret', help = 'your last.fm API key secret')
    parser.add_argument('--tag', dest = 'tag', action = 'store_const', const = True, default = False, help = 'generate tagfs taggings')
    parser.add_argument('--id3', dest = 'id3', action = 'store_const', const = True, default = False, help = 'generate id3 taggings')
    parser.add_argument('userNames', metavar = 'userName', type = str, nargs = '+', help = 'last.fm user names for which the top tracks should be fetched')

    args = parser.parse_args()

    lastFM = pylast.LastFMNetwork(api_key = args.apiKey, api_secret = args.apiSecret)

    for userName in args.userNames:
        user = lastFM.get_user(userName)

        getVideosService = GetVideosService(gdata.youtube.service.YouTubeService())
        videoUrlParser = VideoUrlParser()

        with codecs.open('Makefile.%s' % userName, 'w', encoding = 'utf-8') as f:
            mw = MakefileWriter(f)

            mw.writeVar('YOUTUBE_DL_BIN', 'youtube-dl')
            mw.writeVar('YOUTUBE_DL_OPTS', '--extract-audio --audio-format mp3')

            if(args.id3):
                mw.writeVar('ID3_BIN', 'id3')

            mw.writeTarget('all', ['downloadMusic'])

            downloadMusicTargets = []
            videos = {}

            for track in getTopTracks(user):
                artistName = track.get_artist().get_name()
                trackName = track.get_name()
                trackVideos = getVideosService.getVideos(artistName, trackName)

                print '%s - %s (%s)' % (artistName, trackName, len(trackVideos))

                for i, trackVideo in enumerate(trackVideos):
                    duration = int(trackVideo.media.duration.seconds)

                    if(duration < 20 or duration > 15 * 60):
                        continue

                    videoUrl = trackVideo.media.player.url

                    videoId = videoUrlParser.parse(videoUrl)['id']
                    target = os.path.join('music', escapePathForMakefile('%s - %s (%s)' % (artistName, trackName, videoId)), escapePathForMakefile('%s.mp3' % videoId))

                    videoTarget = getVideoTarget(videoUrlParser, trackVideo)

                    mw.writeTarget(target, [videoTarget])
                    mw.writeRule('mkdir -p `dirname "$@"`')
                    mw.writeRule('cp "%s" "$@"' % videoTarget)

                    if(args.id3):
                        try:
                            mw.writeRule('${ID3_BIN} -t \'%s\' -a \'%s\' "$@"' % (trackName.replace("'", "\\'"), artistName.replace("'", "\\'")))
                        except:
                            print 'Failed to write ID3 tag rule'

                    if(args.tag):
                        tags = {
                            'artist': artistName,
                            'track': trackName,
                            'duration': str(duration),
                            'videoId': videoId,
                            'videoUrl': videoUrl,
                            'videoTitle': trackVideo.media.title.text,
                            'videoPublishDate': trackVideo.published.text,
                            }

                        if(not trackVideo.rating is None):
                            tags['videoRating'] = trackVideo.rating.average

                        for key, value in tags.iteritems():
                            try:
                                encodedValue = value.decode('utf-8').encode('ascii', 'replace').replace("'", "\\'")

                                mw.writeRule('tag `dirname "$@"` set \'%s:%s\'' % (key, encodedValue))
                            except:
                                print 'Failed to apply tag %s: %s' % (key, value)

                        mw.writeRule('tag `dirname "$@"` add \'lastFmUser:%s\'' % userName)

                    downloadMusicTargets.append(target)

                    if(not videoUrl in videos):
                        videos[videoUrl] = trackVideo

            for video in videos.itervalues():
                mw.writeTarget(getVideoTarget(videoUrlParser, video))
                mw.writeRule('mkdir -p `dirname "$@"`')
                mw.writeRule('cd `dirname "$@"` && ${YOUTUBE_DL_BIN} ${YOUTUBE_DL_OPTS} \'%s\'' % (video.media.player.url))

            mw.writeTarget('downloadMusic', downloadMusicTargets)

if __name__ == '__main__':
    main()
