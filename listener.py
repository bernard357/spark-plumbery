# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
from Queue import Empty
import random
import time

class Listener(object):
    """
    Acknowledges commands and feeds the worker
    """

    def __init__(self, ears, inbox, mouth):
        self.ears = ears
        self.inbox = inbox
        self.mouth = mouth
        logging.debug('listener {} {} {}'.format(
            self.ears, self.inbox, self.mouth))

    def work(self, context):
        print("Starting listener")

        self.context = context

        self.context.set('listener.counter', 0)
        while self.context.get('general.switch', 'on') == 'on':
            try:
                item = self.ears.get(True, 0.1)
                counter = self.context.increment('listener.counter')
                self.process(item, counter)
            except Empty:
                pass

    def process(self, item, counter):
        """
        Processes bits coming from Cisco Spark

        This function listens for specific commands in the coming flow.
        When a command has been identified, it is acknowledged immediately.
        Commands that require significant processing time are pushed
        to the inbox.

        Example command received from Cisco Spark:

            {
              "id" : "Z2lzY29zcGFyazovL3VzL01FU1NBR0UvOTJkYjNiZTAtNDNiZC0xMWU2LThhZTktZGQ1YjNkZmM1NjVk",
              "roomId" : "Y2lzY29zcGFyazovL3VzL1JPT00vYmJjZWIxYWQtNDNmMS0zYjU4LTkxNDctZjE0YmIwYzRkMTU0",
              "roomType" : "group",
              "toPersonId" : "Y2lzY29zcGFyazovL3VzL1BFT1BMRS9mMDZkNzFhNS0wODMzLTRmYTUtYTcyYS1jYzg5YjI1ZWVlMmX",
              "toPersonEmail" : "julie@example.com",
              "text" : "/plumby use containers/docker",
              "personId" : "Y2lzY29zcGFyazovL3VzL1BFT1BMRS9mNWIzNjE4Ny1jOGRkLTQ3MjctOGIyZi1mOWM0NDdmMjkwNDY",
              "personEmail" : "matt@example.com",
              "created" : "2015-10-18T14:26:16+00:00",
              "mentionedPeople" : [ "Y2lzY29zcGFyazovL3VzL1BFT1BMRS8yNDlmNzRkOS1kYjhhLTQzY2EtODk2Yi04NzllZDI0MGFjNTM", "Y2lzY29zcGFyazovL3VzL1BFT1BMRS83YWYyZjcyYy0xZDk1LTQxZjAtYTcxNi00MjlmZmNmYmM0ZDg" ]
            }

        """
        print('Listener is working on {}'.format(counter))

        # sanity check
        #
        if not isinstance(item, dict):
            print("- not for me, thrown away")
            return

        input = item.get('text', '')
        if not input.startswith('/plumby '):
            print("- not for me, thrown away")
            return

        line = input[len('/plumby '):]
        tokens = line.split(' ')
        verb = tokens.pop(0)
        if len(tokens) > 0:
            parameters = ' '.join(tokens)
        else:
            parameters = ''

        if verb.lower() not in ['use', 'deploy', 'dispose']:
            print("- unknown command")
            self.mouth.put("Sorry, I do not know how to handle '{}'".format(verb))
            return

        print("- processing command '{}'".format(verb))
        if verb == 'use':
            self.context.set('listener.use', parameters)
            self.mouth.put("This is well-noted")
            return

        self.inbox.put((verb, parameters))
        self.mouth.put("Ok, working on it")
