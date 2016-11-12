#!/usr/bin/env python

import unittest
import logging
from mock import MagicMock
from multiprocessing import Process, Queue
import os
import random
import sys
import time

sys.path.insert(0, os.path.abspath('..'))

from context import Context
from sender import Sender


class SenderTests(unittest.TestCase):

    def test_stop(self):

        logging.debug('*** Stop test ***')

        mouth = Queue()

        context = Context()
        sender = Sender(mouth)

        sender_process = Process(target=sender.work, args=(context,))
        sender_process.daemon = True
        sender_process.start()

        sender_process.join(1.0)
        if sender_process.is_alive():
            logging.debug('Stopping sender')
            context.set('general.switch', 'off')
            sender_process.join()

        self.assertFalse(sender_process.is_alive())
        self.assertEqual(context.get('sender.counter', 0), 0)

    def test_processing(self):

        logging.debug('*** Processing test ***')

        mouth = Queue()
        mouth.put('hello')
        mouth.put('world')
        mouth.put(Exception('EOQ'))

        context = Context()
        context.set('spark.CISCO_SPARK_PLUMBERY_BOT', 'garbage')
        context.set('spark.room_id', 'fake')

        sender = Sender(mouth)
#        sender.post_update = MagicMock()
        sender.work(context)

        with self.assertRaises(Exception):
            mouth.get_nowait()

if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    sys.exit(unittest.main())
