#!/usr/bin/env python

import unittest
import logging
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

from context import Context


class ContextTests(unittest.TestCase):

    def test_apply(self):

        logging.debug('*** Apply test ***')

        context = Context()

        self.assertEqual(context.get('general.port'), None)

        settings = {
            'spark': {'CISCO_SPARK_BTTN_BOT': 'who_knows'},
            'DEBUG': True,
            'server': {'port': 80, 'url': 'http://www.acme.com/'},
            }

        context.apply(settings)

        self.assertEqual(context.get('general.DEBUG'), True)
        self.assertEqual(context.get('spark.CISCO_SPARK_BTTN_BOT'), 'who_knows')
        self.assertEqual(context.get('server.port'), 80)
        self.assertEqual(context.get('server.url'), 'http://www.acme.com/')

    def test_store(self):

        logging.debug('*** Store test ***')

        context = Context()

        # undefined key
        self.assertEqual(context.get('hello'), None)

        # undefined key with default value
        whatever = 'whatever'
        self.assertEqual(context.get('hello', whatever), whatever)

        # set the key
        context.set('hello', 'world')
        self.assertEqual(context.get('hello'), 'world')

        # default value is meaningless when key has been set
        self.assertEqual(context.get('hello', whatever), 'world')

    def test_gauge(self):

        logging.debug('*** Gauge test ***')

        context = Context()

        # undefined key
        self.assertEqual(context.get('gauge'), None)

        # see if type mismatch would create an error
        context.set('gauge', 'world')
        self.assertEqual(context.get('gauge'), 'world')

        # increment and decrement the counter
        value = context.increment('gauge')
        self.assertEqual(value, 1)
        self.assertEqual(context.get('gauge'), 1)

        self.assertEqual(context.decrement('gauge', 2), -1)

        self.assertEqual(context.increment('gauge', 4), 3)
        self.assertEqual(context.decrement('gauge', 10), -7)
        self.assertEqual(context.increment('gauge', 27), 20)
        self.assertEqual(context.get('gauge'), 20)

        # default value is meaningless when key has been set
        self.assertEqual(context.get('gauge', 'world'), 20)

        # reset the gauge
        context.set('gauge', 123)
        self.assertEqual(context.get('gauge'), 123)

    def test_concurrency(self):

        logging.debug('*** Concurrency test ***')

        from multiprocessing import Process
        import random
        import time

        def worker(id, context):
            for i in range(4):
                r = random.random()
                time.sleep(r)
                value = context.increment('gauge')
                logging.debug('worker %d:counter=%d', id, value)
            logging.debug('worker %d:done', id)

        logging.debug('Creating a counter')
        self.counter = Context()

        logging.debug('Launching incrementing workers')
        workers = []
        for i in range(4):
            p = Process(target=worker, args=(i, self.counter,))
            p.start()
            workers.append(p)

        logging.debug('Waiting for worker threads')
        for p in workers:
            p.join()

        logging.debug('Counter: %d', self.counter.get('gauge'))
        self.assertEqual(self.counter.get('gauge'), 16)


if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    sys.exit(unittest.main())
