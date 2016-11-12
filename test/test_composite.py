#!/usr/bin/env python

import unittest
import logging
from mock import MagicMock
import os
from multiprocessing import Process, Queue
import random
import sys
import time

sys.path.insert(0, os.path.abspath('..'))

from context import Context
from listener import Listener
from shell import Shell
from worker import Worker
from speaker import Speaker
from sender import Sender


class CompositeTests(unittest.TestCase):

    def test_static(self):

        logging.debug('*** Static test ***')

        context = Context()

        ears = Queue()
        inbox = Queue()
        outbox = Queue()
        mouth = Queue()

        shell = Shell(context, inbox, mouth)
        listener = Listener(ears, shell)
        worker = Worker(inbox, outbox)
        speaker = Speaker(outbox, mouth)
        sender = Sender(mouth)

        sender_process = Process(target=sender.work, args=(context,))
        sender_process.start()

        speaker_process = Process(target=speaker.work, args=(context,))
        speaker_process.start()

        worker_process = Process(target=worker.work, args=(context,))
        worker_process.start()

        listener_process = Process(target=listener.work, args=(context,))
        listener_process.start()

        listener_process.join(1.0)
        if listener_process.is_alive():
            logging.debug('Stopping all threads')
            context.set('general.switch', 'off')
            listener_process.join()
            worker_process.join()
            speaker_process.join()
            sender_process.join()

        self.assertEqual(context.get('listener.counter', 0), 0)
        self.assertEqual(context.get('worker.counter', 0), 0)
        self.assertEqual(context.get('speaker.counter', 0), 0)
        self.assertEqual(context.get('sender.counter', 0), 0)

    def test_dynamic(self):

        logging.debug('*** Dynamic test ***')

        context = Context()
        context.set('general.fittings',
                         os.path.abspath(os.path.dirname(__file__)))

        ears = Queue()
        inbox = Queue()
        outbox = Queue()
        mouth = Queue()

        shell = Shell(context, inbox, mouth)
        listener = Listener(ears, shell)
        worker = Worker(inbox, outbox)
        speaker = Speaker(outbox, mouth)
        sender = Sender(mouth)
        sender.post_update = MagicMock()

        sender_process = Process(target=sender.work, args=(context,))
        sender_process.daemon = True
        sender_process.start()

        speaker_process = Process(target=speaker.work, args=(context,))
        speaker_process.daemon = True
        speaker_process.start()

        worker_process = Process(target=worker.work, args=(context,))
        worker_process.daemon = True
        worker_process.start()

        listener_process = Process(target=listener.work, args=(context,))
        listener_process.daemon = True
        listener_process.start()

        ears.put('hello world')

        ears.put({
              "id" : "1_lzY29zcGFyazovL3VzL01FU1NBR0UvOTJkYjNiZTAtNDNiZC0xMWU2LThhZTktZGQ1YjNkZmM1NjVk",
              "roomId" : "Y2lzY29zcGFyazovL3VzL1JPT00vYmJjZWIxYWQtNDNmMS0zYjU4LTkxNDctZjE0YmIwYzRkMTU0",
              "roomType" : "group",
              "toPersonId" : "Y2lzY29zcGFyazovL3VzL1BFT1BMRS9mMDZkNzFhNS0wODMzLTRmYTUtYTcyYS1jYzg5YjI1ZWVlMmX",
              "toPersonEmail" : "julie@example.com",
              "text" : "PROJECT UPDATE - A new project plan has been published on Box: http://box.com/s/lf5vj. The PM for this project is Mike C. and the Engineering Manager is Jane W.",
              "markdown" : "**PROJECT UPDATE** A new project plan has been published [on Box](http://box.com/s/lf5vj). The PM for this project is <@personEmail:mike@example.com> and the Engineering Manager is <@personEmail:jane@example.com>.",
              "files" : [ "http://www.example.com/images/media.png" ],
              "personId" : "Y2lzY29zcGFyazovL3VzL1BFT1BMRS9mNWIzNjE4Ny1jOGRkLTQ3MjctOGIyZi1mOWM0NDdmMjkwNDY",
              "personEmail" : "matt@example.com",
              "created" : "2015-10-18T14:26:16+00:00",
              "mentionedPeople" : [ "Y2lzY29zcGFyazovL3VzL1BFT1BMRS8yNDlmNzRkOS1kYjhhLTQzY2EtODk2Yi04NzllZDI0MGFjNTM", "Y2lzY29zcGFyazovL3VzL1BFT1BMRS83YWYyZjcyYy0xZDk1LTQxZjAtYTcxNi00MjlmZmNmYmM0ZDg" ]
            })

        ears.put({
              "id" : "2_2lzY29zcGFyazovL3VzL01FU1NBR0UvOTJkYjNiZTAtNDNiZC0xMWU2LThhZTktZGQ1YjNkZmM1NjVk",
              "roomId" : "Y2lzY29zcGFyazovL3VzL1JPT00vYmJjZWIxYWQtNDNmMS0zYjU4LTkxNDctZjE0YmIwYzRkMTU0",
              "roomType" : "group",
              "toPersonId" : "Y2lzY29zcGFyazovL3VzL1BFT1BMRS9mMDZkNzFhNS0wODMzLTRmYTUtYTcyYS1jYzg5YjI1ZWVlMmX",
              "toPersonEmail" : "julie@example.com",
              "text" : "/plumby use containers/docker",
              "personId" : "Y2lzY29zcGFyazovL3VzL1BFT1BMRS9mNWIzNjE4Ny1jOGRkLTQ3MjctOGIyZi1mOWM0NDdmMjkwNDY",
              "personEmail" : "matt@example.com",
              "created" : "2015-10-18T14:26:16+00:00",
              "mentionedPeople" : [ "Y2lzY29zcGFyazovL3VzL1BFT1BMRS8yNDlmNzRkOS1kYjhhLTQzY2EtODk2Yi04NzllZDI0MGFjNTM", "Y2lzY29zcGFyazovL3VzL1BFT1BMRS83YWYyZjcyYy0xZDk1LTQxZjAtYTcxNi00MjlmZmNmYmM0ZDg" ]
            })

        ears.put({
              "id" : "3_2lzY29zcGFyazovL3VzL01FU1NBR0UvOTJkYjNiZTAtNDNiZC0xMWU2LThhZTktZGQ1YjNkZmM1NjVk",
              "roomId" : "Y2lzY29zcGFyazovL3VzL1JPT00vYmJjZWIxYWQtNDNmMS0zYjU4LTkxNDctZjE0YmIwYzRkMTU0",
              "roomType" : "group",
              "toPersonId" : "Y2lzY29zcGFyazovL3VzL1BFT1BMRS9mMDZkNzFhNS0wODMzLTRmYTUtYTcyYS1jYzg5YjI1ZWVlMmX",
              "toPersonEmail" : "julie@example.com",
              "text" : "/plumby deploy",
              "personId" : "Y2lzY29zcGFyazovL3VzL1BFT1BMRS9mNWIzNjE4Ny1jOGRkLTQ3MjctOGIyZi1mOWM0NDdmMjkwNDY",
              "personEmail" : "matt@example.com",
              "created" : "2015-10-18T14:26:16+00:00",
              "mentionedPeople" : [ "Y2lzY29zcGFyazovL3VzL1BFT1BMRS8yNDlmNzRkOS1kYjhhLTQzY2EtODk2Yi04NzllZDI0MGFjNTM", "Y2lzY29zcGFyazovL3VzL1BFT1BMRS83YWYyZjcyYy0xZDk1LTQxZjAtYTcxNi00MjlmZmNmYmM0ZDg" ]
            })

        ears.put({
              "id" : "4_2lzY29zcGFyazovL3VzL01FU1NBR0UvOTJkYjNiZTAtNDNiZC0xMWU2LThhZTktZGQ1YjNkZmM1NjVk",
              "roomId" : "Y2lzY29zcGFyazovL3VzL1JPT00vYmJjZWIxYWQtNDNmMS0zYjU4LTkxNDctZjE0YmIwYzRkMTU0",
              "roomType" : "group",
              "toPersonId" : "Y2lzY29zcGFyazovL3VzL1BFT1BMRS9mMDZkNzFhNS0wODMzLTRmYTUtYTcyYS1jYzg5YjI1ZWVlMmX",
              "toPersonEmail" : "julie@example.com",
              "text" : "PROJECT UPDATE - A new project plan has been published on Box: http://box.com/s/lf5vj. The PM for this project is Mike C. and the Engineering Manager is Jane W.",
              "markdown" : "**PROJECT UPDATE** A new project plan has been published [on Box](http://box.com/s/lf5vj). The PM for this project is <@personEmail:mike@example.com> and the Engineering Manager is <@personEmail:jane@example.com>.",
              "files" : [ "http://www.example.com/images/media.png" ],
              "personId" : "Y2lzY29zcGFyazovL3VzL1BFT1BMRS9mNWIzNjE4Ny1jOGRkLTQ3MjctOGIyZi1mOWM0NDdmMjkwNDY",
              "personEmail" : "matt@example.com",
              "created" : "2015-10-18T14:26:16+00:00",
              "mentionedPeople" : [ "Y2lzY29zcGFyazovL3VzL1BFT1BMRS8yNDlmNzRkOS1kYjhhLTQzY2EtODk2Yi04NzllZDI0MGFjNTM", "Y2lzY29zcGFyazovL3VzL1BFT1BMRS83YWYyZjcyYy0xZDk1LTQxZjAtYTcxNi00MjlmZmNmYmM0ZDg" ]
            })


        listener_process.join(7.0)
        if listener_process.is_alive():
            logging.debug('Stopping all threads')
            context.set('general.switch', 'off')
            listener_process.join()
            worker_process.join()
            speaker_process.join()
            sender_process.join()

        self.assertEqual(context.get('listener.counter', 0), 5)
        self.assertEqual(context.get('worker.counter', 0), 1)
        self.assertEqual(context.get('speaker.counter', 0), 1)
        self.assertEqual(context.get('sender.counter', 0), 3)


if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    sys.exit(unittest.main())
