#!/usr/bin/env python

import unittest
import logging
from mock import MagicMock
import os
from Queue import Queue
import random
import sys
from threading import Thread
import time

sys.path.insert(0, os.path.abspath('..'))

from context import Context
from sender import Sender


class SenderTests(unittest.TestCase):

    def test_stop(self):

        logging.debug('*** Stop test ***')

        mouth = Queue()
        sender = Sender(mouth)

        context = Context()

        sender_thread = Thread(target=sender.work, args=(context,))
        sender_thread.start()

        sender_thread.join(1.0)
        if sender_thread.isAlive():
            logging.debug('Stopping sender')
            context.set('general.switch', 'off')
            sender_thread.join()

        self.assertFalse(sender_thread.isAlive())
        self.assertEqual(context.get('sender.counter', 0), 0)

    def test_processing(self):

        logging.debug('*** Processing test ***')

        mouth = Queue()
        mouth.put('hello')
        mouth.put('world')
        self.assertEqual(mouth.qsize(), 2)

        sender = Sender(mouth)
#        sender.post_update = MagicMock()

        context = Context()
        context.set('general.CISCO_SPARK_PLUMBERY_BOT', 'garbage')
        context.set('general.room_id', 'fake')

        sender_thread = Thread(target=sender.work, args=(context,))
        sender_thread.start()

        sender_thread.join(4.0)
        if sender_thread.isAlive():
            logging.debug('Stopping sender')
            context.set('general.switch', 'off')
            sender_thread.join()

        self.assertEqual(mouth.qsize(), 0)

if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    sys.exit(unittest.main())
