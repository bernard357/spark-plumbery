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
* list templates: @plumby list
* use template: @plumby use analytics/hadoop-cluster
* show template: @plumby status
* deploy template: @plumby deploy
* destroy template: @plumby dispose
"""

class Shell(object):
    """
    Parses input and reacts accordingly
    """

    def __init__(self, context, inbox, mouth):
        self.context = context
        self.inbox = inbox
        self.mouth = mouth

    def list_verbs(self):
        return [
            'deploy',
            'dispose',
            'help',
            'list',
            'status',
            'use',
            ]

    def do_deploy(self, parameters):
        if not self.context.get('worker.busy', False):
            self.mouth.put("Ok, working on it")
        else:
            self.mouth.put("Ok, will work on it as soon as possible")
        self.inbox.put(('deploy', parameters))

    def do_dispose(self, parameters):
        if not self.context.get('worker.busy', False):
            self.mouth.put("Ok, working on it")
        else:
            self.mouth.put("Ok, will work on it as soon as possible")
        self.inbox.put(('dispose', parameters))

    def do_help(self, parameters):
        self.mouth.put({'markdown': help_markdown})

    def do_list(self, parameters):

        root =  self.context.get('fittings', '.')
        print('- listing fittings in {}'.format(root))
        self.mouth.put("You can use any of following fittings:")
        count = 0
        for category in os.listdir(root):
            c_path = os.path.join(root,category)
            if not os.path.isdir(c_path):
                continue
            for fittings in os.listdir(c_path):
                f_path = os.path.join(c_path,fittings)
                try:
                    with open(os.path.join(f_path, 'fittings.yaml'), 'r') as f:
                        count += 1
                        self.mouth.put("- {}".format(category+'/'+fittings))
                except:
                    pass
        print('- found {} fittings'.format(count))

    def do_status(self, parameters):
        self.mouth.put("Using {}".format(self.context.get('general.fittings')))
        if self.context.get('worker.busy', False):
            self.mouth.put("Plumbery is busy")

    def do_use(self, parameters):
        self.context.set('general.fittings', parameters)
        self.mouth.put("This is well-noted")
