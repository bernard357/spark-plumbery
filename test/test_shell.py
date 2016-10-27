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
from shell import Shell


class SpeakerTests(unittest.TestCase):

    def test_do_deploy(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        shell.do_deploy('123')
        context.set('worker.busy', True)
        shell.do_deploy('456')
        context.set('worker.busy', False)
        shell.do_deploy('789')
        self.assertEqual(mouth.qsize(), 3)
        self.assertEqual(mouth.get(), "Ok, working on it")
        self.assertEqual(mouth.get(), "Ok, will work on it as soon as possible")
        self.assertEqual(mouth.get(), "Ok, working on it")
        self.assertEqual(inbox.qsize(), 3)
        self.assertEqual(inbox.get(), ('deploy', '123'))
        self.assertEqual(inbox.get(), ('deploy', '456'))
        self.assertEqual(inbox.get(), ('deploy', '789'))

    def test_do_dispose(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        shell.do_dispose('123')
        context.set('worker.busy', True)
        shell.do_dispose('456')
        context.set('worker.busy', False)
        shell.do_dispose('789')
        self.assertEqual(mouth.qsize(), 3)
        self.assertEqual(mouth.get(), "Ok, working on it")
        self.assertEqual(mouth.get(), "Ok, will work on it as soon as possible")
        self.assertEqual(mouth.get(), "Ok, working on it")
        self.assertEqual(inbox.qsize(), 3)
        self.assertEqual(inbox.get(), ('dispose', '123'))
        self.assertEqual(inbox.get(), ('dispose', '456'))
        self.assertEqual(inbox.get(), ('dispose', '789'))

    def test_do_help(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        shell.do_help()
        self.assertEqual(mouth.qsize(), 1)
        self.assertEqual(inbox.qsize(), 0)

    def test_do_list(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        shell.do_list()
        self.assertEqual(mouth.qsize(), 5)
        self.assertEqual(inbox.qsize(), 0)

    def test_do_status(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        shell.do_status()
        self.assertEqual(mouth.qsize(), 1)
        self.assertEqual(inbox.qsize(), 0)

    def test_do_use(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        self.assertEqual(context.get('general.fittings'), None)
        shell.do_use('hello/world')
        self.assertEqual(context.get('general.fittings'), 'hello/world')
        self.assertEqual(mouth.qsize(), 1)
        self.assertEqual(inbox.qsize(), 0)

if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    sys.exit(unittest.main())
