from unittest import TestCase, main
from lastRipper import VideoUrlParser

class VideoUrlParserSmallTest(TestCase):

    def testParseVideoIdFromUrl(self):
        parser = VideoUrlParser()

        self.assertEqual(parser.parse('https://www.youtube.com/watch?v=hwz4GpJZ6tQ&feature=youtube_gdata_player')['id'], 'hwz4GpJZ6tQ')

if __name__ == '__main__':
    main()
