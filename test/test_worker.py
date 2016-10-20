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
from worker import Worker


class WorkerTests(unittest.TestCase):

    def test_stop(self):

        logging.debug('*** Stop test ***')

        inbox = Queue()
        outbox = Queue()

        context = Context()
        worker = Worker(inbox, outbox)

        worker_thread = Thread(target=worker.work, args=(context,))
        worker_thread.setDaemon(True)
        worker_thread.start()

        worker_thread.join(1.0)
        if worker_thread.isAlive():
            logging.debug('Stopping worker')
            context.set('general.switch', 'off')
            worker_thread.join()

        self.assertFalse(worker_thread.isAlive())
        self.assertEqual(context.get('worker.counter', 0), 0)

    def test_processing(self):

        logging.debug('*** Processing test ***')

        inbox = Queue()
        inbox.put(('deploy', ''))
        inbox.put(('dispose', ''))
        inbox.put(('unknownCommand', ''))
        inbox.put(Exception('EOQ'))
        self.assertEqual(inbox.qsize(), 4)

        outbox = Queue()
        self.assertEqual(outbox.qsize(), 0)

        context = Context()
        context.set('general.fittings',
                         os.path.abspath(os.path.dirname(__file__)))

        worker = Worker(inbox, outbox)

        worker.work(context)

        self.assertEqual(context.get('worker.counter'), 3)
        self.assertEqual(inbox.qsize(), 0)
        self.assertTrue(outbox.qsize() > 2)

        logging.debug('{} items in outbox'.format(outbox.qsize()))

if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    sys.exit(unittest.main())
