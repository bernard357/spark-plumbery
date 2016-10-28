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
import os

help_markdown = """
Some commands that may prove useful:
- show status: @plumby status
- list templates: @plumby list
- use template: @plumby use analytics/hadoop-cluster
- deploy template: @plumby deploy
- stop servers: @plumby stop
- start servers: @plumby start
- destroy resources: @plumby dispose
- prepare servers: @plumby prepare
- refresh servers: @plumby refresh
- get information: @plumby information
"""

class Shell(object):
    """
    Parses input and reacts accordingly
    """

    def __init__(self, context, inbox, mouth):
        self.context = context
        self.inbox = inbox
        self.mouth = mouth

    def do_deploy(self, parameters=None):
        if not self.context.get('worker.busy', False):
            self.mouth.put("Ok, working on it")
        else:
            self.mouth.put("Ok, will work on it as soon as possible")
        self.inbox.put(('deploy', parameters))

    def do_dispose(self, parameters=None):
        if not self.context.get('worker.busy', False):
            self.mouth.put("Ok, working on it")
        else:
            self.mouth.put("Ok, will work on it as soon as possible")
        self.inbox.put(('dispose', parameters))

    def do_information(self, parameters=None):
        if not self.context.get('worker.busy', False):
            self.mouth.put("Ok, working on it")
        else:
            self.mouth.put("Ok, will work on it as soon as possible")
        self.inbox.put(('information', parameters))

    def do_help(self, parameters=None):
        self.mouth.put({'markdown': help_markdown})

    def do_list(self, parameters=None):

        root =  self.context.get('general.fittings', '.')
        print('- listing fittings at {}'.format(root))
        count = 0
        for category in os.listdir(root):
            c_path = os.path.join(root,category)
            if not os.path.isdir(c_path):
                continue
            for fittings in os.listdir(c_path):
                f_path = os.path.join(c_path,fittings)
                try:
                    with open(os.path.join(f_path, 'fittings.yaml'), 'r') as f:
                        if count == 0:
                            self.mouth.put("You can use any of following templates:")
                        count += 1
                        self.mouth.put("- {}".format(category+'/'+fittings))
                except:
                    pass
        print('- found {} fittings'.format(count))
        if count == 0:
            self.mouth.put("No template has been found")

    def do_prepare(self, parameters=None):
        if not self.context.get('worker.busy', False):
            self.mouth.put("Ok, working on it")
        else:
            self.mouth.put("Ok, will work on it as soon as possible")
        self.inbox.put(('prepare', parameters))

    def do_refresh(self, parameters=None):
        if not self.context.get('worker.busy', False):
            self.mouth.put("Ok, working on it")
        else:
            self.mouth.put("Ok, will work on it as soon as possible")
        self.inbox.put(('refresh', parameters))

    def do_start(self, parameters=None):
        if not self.context.get('worker.busy', False):
            self.mouth.put("Ok, working on it")
        else:
            self.mouth.put("Ok, will work on it as soon as possible")
        self.inbox.put(('start', parameters))

    def do_status(self, parameters=None):
        self.mouth.put("Using {}".format(self.context.get('worker.template', 'example/first')))
        if self.context.get('worker.busy', False):
            self.mouth.put("On-going processing")
        else:
            self.mouth.put("Ready to process commands")

    def do_stop(self, parameters=None):
        if not self.context.get('worker.busy', False):
            self.mouth.put("Ok, working on it")
        else:
            self.mouth.put("Ok, will work on it as soon as possible")
        self.inbox.put(('stop', parameters))

    def do_use(self, parameters):
        self.context.set('worker.template', parameters)
        self.mouth.put("This is well-noted")
