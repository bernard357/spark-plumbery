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
from shell import Shell


class SpeakerTests(unittest.TestCase):

    def test_worker_commands(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        worker_commands = [
            ('deploy', shell.do_deploy),
            ('dispose', shell.do_dispose),
            ('information', shell.do_information),
            ('prepare', shell.do_prepare),
            ('refresh', shell.do_refresh),
            ('start', shell.do_start),
            ('stop', shell.do_stop),
        ]

        for label, do in worker_commands:

            do('123')
            context.set('worker.busy', True)
            do('456')
            context.set('worker.busy', False)
            do('789')
            self.assertEqual(mouth.get(), "Ok, working on it")
            self.assertEqual(mouth.get(), "Ok, will work on it as soon as possible")
            self.assertEqual(mouth.get(), "Ok, working on it")
            with self.assertRaises(Exception):
                mouth.get_nowait()
            self.assertEqual(inbox.get(), (label, '123'))
            self.assertEqual(inbox.get(), (label, '456'))
            self.assertEqual(inbox.get(), (label, '789'))
            with self.assertRaises(Exception):
                inbox.get_nowait()

    def test_do_help(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        shell.do_help()
        mouth.get()
        with self.assertRaises(Exception):
            mouth.get_nowait()
        with self.assertRaises(Exception):
            inbox.get_nowait()

    def test_do_list(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        context.set('plumbery.fittings', os.path.dirname(os.path.realpath(__file__)))

        shell.do_list()
        self.assertEqual(mouth.get(), "You can list templates in following categories:")
        self.assertEqual(mouth.get(), "- category1")
        self.assertEqual(mouth.get(), "- category2")
        self.assertEqual(mouth.get(), "- category3_is_empty")
        with self.assertRaises(Exception):
            mouth.get_nowait()
        with self.assertRaises(Exception):
            inbox.get_nowait()

        shell.do_list('')
        self.assertEqual(mouth.get(), "You can list templates in following categories:")
        self.assertEqual(mouth.get(), "- category1")
        self.assertEqual(mouth.get(), "- category2")
        self.assertEqual(mouth.get(), "- category3_is_empty")
        with self.assertRaises(Exception):
            mouth.get_nowait()
        with self.assertRaises(Exception):
            inbox.get_nowait()

        shell.do_list('*unknown*')
        self.assertEqual(mouth.get(), "No category has this name. Double-check with the list command.")
        with self.assertRaises(Exception):
            mouth.get_nowait()
        with self.assertRaises(Exception):
            inbox.get_nowait()

        shell.do_list('category1')
        self.assertEqual(mouth.get(), "You can use any of following templates:")
        self.assertEqual(mouth.get(), "- category1/fittings1")
        self.assertEqual(mouth.get(), "- category1/fittings2")
        with self.assertRaises(Exception):
            mouth.get_nowait()
        with self.assertRaises(Exception):
            inbox.get_nowait()

        shell.do_list('category2')
        self.assertEqual(mouth.get(), "You can use any of following templates:")
        self.assertEqual(mouth.get(), "- category2/fittings1")
        self.assertEqual(mouth.get(), "- category2/fittings2")
        with self.assertRaises(Exception):
            mouth.get_nowait()
        with self.assertRaises(Exception):
            inbox.get_nowait()

        shell.do_list('category3_is_empty')
        self.assertEqual(mouth.get(), "No template has been found in category 'category3_is_empty'")
        with self.assertRaises(Exception):
            mouth.get_nowait()
        with self.assertRaises(Exception):
            inbox.get_nowait()

        context.set('plumbery.fittings', './perfectly_unknown_path')
        shell.do_list()
        self.assertEqual(mouth.get(), "Invalid path for fittings. Check configuration")
        with self.assertRaises(Exception):
            mouth.get_nowait()
        with self.assertRaises(Exception):
            inbox.get_nowait()


    def test_do_status(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        shell.do_status()
        mouth.get()
        mouth.get()
        with self.assertRaises(Exception):
            mouth.get_nowait()
        with self.assertRaises(Exception):
            inbox.get_nowait()

    def test_do_use(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        self.assertEqual(context.get('plumbery.fittings'), None)
        context.set('plumbery.fittings', os.path.dirname(os.path.realpath(__file__)))

        self.assertEqual(context.get('worker.template'), None)

        shell.do_use()
        self.assertEqual(context.get('worker.template'), None)
        self.assertEqual(mouth.get(), "Please indicate the category and the template that you want to use.")
        with self.assertRaises(Exception):
            mouth.get_nowait()
        with self.assertRaises(Exception):
            inbox.get_nowait()

        shell.do_use('category1')
        self.assertEqual(context.get('worker.template'), None)
        self.assertEqual(mouth.get(), "Please indicate the category and the template that you want to use.")
        with self.assertRaises(Exception):
            mouth.get_nowait()
        with self.assertRaises(Exception):
            inbox.get_nowait()

        shell.do_use('hello/world')
        self.assertEqual(context.get('worker.template'), None)
        self.assertEqual(mouth.get(), "No template has this name. Double-check with the list command.")
        with self.assertRaises(Exception):
            mouth.get_nowait()
        with self.assertRaises(Exception):
            inbox.get_nowait()

        shell.do_use('category1/fittings2')
        self.assertEqual(context.get('worker.template'), 'category1/fittings2')
        self.assertEqual(mouth.get(), "This is well-noted")
        with self.assertRaises(Exception):
            mouth.get_nowait()
        with self.assertRaises(Exception):
            inbox.get_nowait()

        context.set('plumbery.fittings', './perfectly_unknown_path')
        shell.do_use('category2/fittings1')
        self.assertEqual(context.get('worker.template'), 'category1/fittings2')
        self.assertEqual(mouth.get(), "Invalid path for fittings. Check configuration")
        with self.assertRaises(Exception):
            mouth.get_nowait()
        with self.assertRaises(Exception):
            inbox.get_nowait()

    def test_do_version(self):

        context = Context()
        inbox = Queue()
        mouth = Queue()
        shell = Shell(context, inbox, mouth)

        shell.do_version()
        mouth.get()
        with self.assertRaises(Exception):
            mouth.get_nowait()
        with self.assertRaises(Exception):
            inbox.get_nowait()

if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    sys.exit(unittest.main())
