#!/usr/bin/env python

import unittest
import logging
import os
from multiprocessing import Process, Queue
import random
import sys
import time

sys.path.insert(0, os.path.abspath('..'))

from context import Context
from speaker import Speaker


class SpeakerTests(unittest.TestCase):

    def test_stop(self):

        logging.debug('*** Stop test ***')

        outbox = Queue()
        mouth = Queue()

        context = Context()
        speaker = Speaker(outbox, mouth)

        speaker_process = Process(target=speaker.work, args=(context,))
        speaker_process.daemon = True
        speaker_process.start()

        speaker_process.join(1.0)
        if speaker_process.is_alive():
            logging.debug('Stopping speaker')
            context.set('general.switch', 'off')
            speaker_process.join()

        self.assertFalse(speaker_process.is_alive())
        self.assertEqual(context.get('speaker.counter', 0), 0)

    def test_processing(self):

        logging.debug('*** Processing test ***')

        outbox = Queue()
        outbox.put('hello')
        outbox.put('world')
        outbox.put(Exception('EOQ'))

        mouth = Queue()

        context = Context()
        speaker = Speaker(outbox, mouth)
        speaker.work(context)

        self.assertEqual(mouth.get(), 'hello')
        self.assertEqual(mouth.get(), 'world')
        with self.assertRaises(Exception):
            mouth.get_nowait()
        with self.assertRaises(Exception):
            outbox.get_nowait()

if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    sys.exit(unittest.main())
