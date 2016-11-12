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
from worker import Worker


class WorkerTests(unittest.TestCase):

    def test_stop(self):

        logging.debug('*** Stop test ***')

        inbox = Queue()
        outbox = Queue()

        context = Context()
        worker = Worker(inbox, outbox)

        worker_process = Process(target=worker.work, args=(context,))
        worker_process.daemon = True
        worker_process.start()

        worker_process.join(1.0)
        if worker_process.is_alive():
            logging.debug('Stopping worker')
            context.set('general.switch', 'off')
            worker_process.join()

        self.assertFalse(worker_process.is_alive())
        self.assertEqual(context.get('worker.counter', 0), 0)

    def test_processing(self):

        logging.debug('*** Processing test ***')

        inbox = Queue()
        inbox.put(('deploy', ''))
        inbox.put(('dispose', ''))
        inbox.put(('unknownCommand', ''))
        inbox.put(Exception('EOQ'))

        outbox = Queue()

        context = Context()
        context.set('general.fittings',
                         os.path.abspath(os.path.dirname(__file__)))

        worker = Worker(inbox, outbox)

        worker.work(context)

        self.assertEqual(context.get('worker.counter'), 3)
        with self.assertRaises(Exception):
            inbox.get_nowait()

if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    sys.exit(unittest.main())
