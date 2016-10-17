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

        shell.do_deploy('1234')
        self.assertEqual(mouth.qsize(), 1)
        self.assertEqual(inbox.qsize(), 1)
        self.assertEqual(inbox.get(), ('deploy', '1234'))

    def test_do_dispose(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        shell.do_dispose('abcdef')
        self.assertEqual(mouth.qsize(), 1)
        self.assertEqual(inbox.qsize(), 1)
        self.assertEqual(inbox.get(), ('dispose', 'abcdef'))

    def test_do_help(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        shell.do_help('abcdef')
        self.assertEqual(mouth.qsize(), 1)
        self.assertEqual(inbox.qsize(), 0)

    def test_do_list(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        shell.do_list('abcdef')
        self.assertEqual(mouth.qsize(), 1)
        self.assertEqual(inbox.qsize(), 0)

    def test_do_status(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        shell.do_status('abcdef')
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
