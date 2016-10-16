#!/usr/bin/env python

import unittest
import logging
import os
from Queue import Queue
import random
import sys
from threading import Thread
import time

sys.path.insert(0, os.path.abspath('..'))

from context import Context
from speaker import Speaker


class SpeakerTests(unittest.TestCase):

    def test_stop(self):

        logging.debug('*** Stop test ***')

        outbox = Queue()
        mouth = Queue()
        speaker = Speaker(outbox, mouth)

        context = Context()

        speaker_thread = Thread(target=speaker.work, args=(context,))
        speaker_thread.start()

        speaker_thread.join(1.0)
        if speaker_thread.isAlive():
            logging.debug('Stopping speaker')
            context.set('general.switch', 'off')
            speaker_thread.join()

        self.assertFalse(speaker_thread.isAlive())
        self.assertEqual(context.get('speaker.counter', 0), 0)

    def test_processing(self):

        logging.debug('*** Processing test ***')

        outbox = Queue()
        outbox.put('hello')
        outbox.put('world')
        self.assertEqual(outbox.qsize(), 2)

        mouth = Queue()
        self.assertEqual(mouth.qsize(), 0)

        speaker = Speaker(outbox, mouth)

        context = Context()

        speaker_thread = Thread(target=speaker.work, args=(context,))
        speaker_thread.start()

        speaker_thread.join(1.0)
        if speaker_thread.isAlive():
            logging.debug('Stopping speaker')
            context.set('general.switch', 'off')
            speaker_thread.join()

        self.assertEqual(mouth.qsize(), 2)

if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    sys.exit(unittest.main())
