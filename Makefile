PYTHON=python

all:

clean:
	rm -rf *.pyc
	rm -f .*.lastRun
	find download -type f -iname '*.flv' -exec rm {} \;
	find download -type f -iname '*.mp4' -exec rm {} \;
	find download -type f -iname '*.part' -exec rm {} \;

test: .lastRipperGetTopTracksSmallTest.py.lastRun .lastRipperVideoUrlParserSmallTest.py.lastRun .lastRipperMakefileWriterSmallTest.py.lastRun

.lastRipperGetTopTracksSmallTest.py.lastRun: lastRipperGetTopTracksSmallTest.py lastRipper.py
	${PYTHON} lastRipperGetTopTracksSmallTest.py
	touch "$@"

.lastRipperVideoUrlParserSmallTest.py.lastRun: lastRipperVideoUrlParserSmallTest.py lastRipper.py
	${PYTHON} lastRipperVideoUrlParserSmallTest.py
	touch "$@"

.lastRipperMakefileWriterSmallTest.py.lastRun: lastRipperMakefileWriterSmallTest.py lastRipper.py
	${PYTHON} lastRipperMakefileWriterSmallTest.py
	touch "$@"
