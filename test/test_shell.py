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

    def test_worker_commands(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        long_commands = [
            ('deploy', shell.do_deploy),
            ('dispose', shell.do_dispose),
            ('information', shell.do_information),
            ('prepare', shell.do_prepare),
            ('refresh', shell.do_refresh),
            ('start', shell.do_start),
            ('stop', shell.do_stop),
        ]

        for label, do in long_commands:
            print('- {}'.format(label))

            do('123')
            context.set('worker.busy', True)
            do('456')
            context.set('worker.busy', False)
            do('789')
            if label not in ('list'):
                self.assertEqual(mouth.qsize(), 3)
                self.assertEqual(mouth.get_nowait(), "Ok, working on it")
                self.assertEqual(mouth.get_nowait(), "Ok, will work on it as soon as possible")
                self.assertEqual(mouth.get_nowait(), "Ok, working on it")
                self.assertEqual(inbox.qsize(), 3)
                self.assertEqual(inbox.get_nowait(), (label, '123'))
                self.assertEqual(inbox.get_nowait(), (label, '456'))
                self.assertEqual(inbox.get_nowait(), (label, '789'))

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
        self.assertEqual(mouth.qsize(), 3)
        self.assertEqual(mouth.get_nowait(), "You can list templates in following categories:")
        self.assertEqual(mouth.get_nowait(), "- category1")
        self.assertEqual(mouth.get_nowait(), "- category2")
        self.assertEqual(inbox.qsize(), 0)

        shell.do_list('*unknown*')
        self.assertEqual(mouth.qsize(), 1)
        self.assertEqual(mouth.get_nowait(), "There is no category '*unknown*'")
        self.assertEqual(inbox.qsize(), 0)

        shell.do_list('category1')
        self.assertEqual(mouth.qsize(), 3)
        self.assertEqual(mouth.get_nowait(), "You can use any of following templates:")
        self.assertEqual(mouth.get_nowait(), "- category1/fittings1")
        self.assertEqual(mouth.get_nowait(), "- category1/fittings2")
        self.assertEqual(inbox.qsize(), 0)

        shell.do_list('category2')
        self.assertEqual(mouth.qsize(), 3)
        self.assertEqual(mouth.get_nowait(), "You can use any of following templates:")
        self.assertEqual(mouth.get_nowait(), "- category2/fittings1")
        self.assertEqual(mouth.get_nowait(), "- category2/fittings2")
        self.assertEqual(inbox.qsize(), 0)

    def test_do_status(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        shell.do_status()
        self.assertEqual(mouth.qsize(), 2)
        self.assertEqual(inbox.qsize(), 0)

    def test_do_use(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        self.assertEqual(context.get('general.fittings'), None)
        shell.do_use('hello/world')
        self.assertEqual(context.get('worker.template'), 'hello/world')
        self.assertEqual(mouth.qsize(), 1)
        self.assertEqual(inbox.qsize(), 0)

    def test_do_version(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        shell.do_version()
        self.assertEqual(mouth.qsize(), 1)
        self.assertEqual(inbox.qsize(), 0)

if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    sys.exit(unittest.main())
