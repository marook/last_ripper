from unittest import TestCase, main
from lastRipper import getTopTracks

class TrackMock(object):

    def __init__(self, id):
        self.item = id

class UserMock(object):

    def __init__(self, test):
        self.test = test
        self.topTracks = {}

    def get_top_tracks(self, period = None):
        self.test.assertIn(period, set(self.topTracks.iterkeys()))

        return self.topTracks[period]

class GetTopTracksSmallTest(TestCase):

    def setUp(self):
        self.user = UserMock(self)

        for period in ['7day', '3month', '6month', '12month', 'overall']:
            self.user.topTracks[period] = []
            
    def assertTopTracks(self, expectedTracks):
        topTracks = list(getTopTracks(self.user))
    
        self.assertEqual(topTracks, [t.item for t in expectedTracks]);

    def testGetTopTracksFor7DayPeriod(self):
        t1 = TrackMock('t1')

        self.user.topTracks['7day'].append(t1)

        self.assertTopTracks([t1])

    def testGetTrackOnlyOnceIfItAppearsInMultiplePeriods(self):
        t1 = TrackMock('t1')

        self.user.topTracks['7day'].append(t1)
        self.user.topTracks['3month'].append(t1)

        self.assertTopTracks([t1])

if __name__ == '__main__':
    main()
