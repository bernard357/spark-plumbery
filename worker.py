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

import logging
from Queue import Empty
import random
import time
from plumbery.engine import PlumberyEngine

class Worker(object):
    """
    Takes activities from the inbox and puts reports in the outbox
    """

    def __init__(self, inbox, outbox):
        self.inbox = inbox
        self.outbox = outbox
        logging.debug('worker {}, {}'.format(self.inbox, self.outbox))

    def work(self, context):
        print("Starting worker")

        self.context = context

        self.context.set('worker.counter', 0)
        while self.context.get('general.switch', 'on') == 'on':
            try:
                item = self.inbox.get(True, 0.1)
                counter = self.context.increment('worker.counter')
                self.process(item, counter)
            except Empty:
                pass

    def process(self, item, counter):
        """
        Processes one action

        Example actions:

            ('deploy', '')
            ('dispose', '')

        """
        print('Worker is working on {}'.format(counter))

        (verb, parameters) = item

        try:

            fittings = self.context.get('general.fittings', '.')+'/fittings.yaml'
            print('- reading {}'.format(fittings))

            print('- loading plumbery engine')
            engine = PlumberyEngine(fittings)

        except Exception as feedback:
            print("Error while reading fittings plan")
            self.outbox.put("Error while reading fittings plan")
            return

        try:
            engine.do(verb)

            self.outbox.put(engine.document_elapsed())

        except Exception as feedback:
            print("Unable to do '{}'".format(verb))
            self.outbox.put("Unable to do '{}'".format(verb))
            return
