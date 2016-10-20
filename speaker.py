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

class Speaker(object):
    """
    Translates reports and feeds the mouth
    """

    def __init__(self, outbox, mouth):
        self.outbox = outbox
        self.mouth = mouth
        logging.debug('speaker {}, {}'.format(self.outbox, self.mouth))

    def work(self, context):
        print("Starting speaker")

        self.context = context

        self.context.set('speaker.counter', 0)
        while self.context.get('general.switch', 'on') == 'on':
            try:
                item = self.outbox.get(True, 0.1)
                if isinstance(item, Exception):
                    break
                counter = self.context.increment('speaker.counter')
                self.process(item, counter)
            except Empty:
                pass

    def process(self, item, counter):
        """
        Filters feed-back from the worker
        """
        print('Speaker is working on {}'.format(counter))
        self.mouth.put(item)
