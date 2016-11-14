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
import yaml

help_markdown = """
Some commands that may prove useful:
- show status: @plumby status
- list categories: @plumby list
- list templates: @plumby list analytics
- use template: @plumby use analytics/hadoop-cluster
- deploy template: @plumby deploy
- get information: @plumby information
- stop servers: @plumby stop
- start servers: @plumby start
- destroy resources: @plumby dispose
"""

class Shell(object):
    """
    Parses input and reacts accordingly
    """

    def __init__(self, context, inbox, mouth):
        self.context = context
        self.inbox = inbox
        self.mouth = mouth

    def do(self, line):
        """
        Handles one line of text

        This function uses the first token as a verb, and looks for a method
        of the same name in the shell.

        For example, for the command `use analytics/hadoop-cluster`, the function
        will invoke `shell.do_use('analytics/hadoop-cluster')`.

        If the command does not exist, an error message will be given back to
        the end user.
        """
        tokens = line.split(' ')
        verb = tokens.pop(0)
        if len(verb) < 1:
            verb = 'help'

        if len(tokens) > 0:
            arguments = ' '.join(tokens)
        else:
            arguments = ''

        try:
            method = getattr(self, 'do_'+verb, None)
            if callable(method):
                print("- processing command '{}'".format(line))
                method(arguments)
            else:
                print("- invalid command")
                self.mouth.put("Sorry, I do not know how to handle '{}'".format(verb))

        except:
            print("- unknown command")
            self.mouth.put("Sorry, I do not know how to handle '{}'".format(verb))

    def do_deploy(self, arguments=None):
        if not self.context.get('worker.busy', False):
            self.mouth.put("Ok, working on it")
        else:
            self.mouth.put("Ok, will work on it as soon as possible")
        self.inbox.put(('deploy', arguments))

    def do_dispose(self, arguments=None):
        if not self.context.get('worker.busy', False):
            self.mouth.put("Ok, working on it")
        else:
            self.mouth.put("Ok, will work on it as soon as possible")
        self.inbox.put(('dispose', arguments))

    def do_information(self, arguments=None):
        if not self.context.get('worker.busy', False):
            self.mouth.put("Ok, working on it")
        else:
            self.mouth.put("Ok, will work on it as soon as possible")
        self.inbox.put(('information', arguments))

    def do_help(self, arguments=None):
        self.mouth.put({'markdown': help_markdown})

    def do_list(self, arguments=None):
        root =  self.context.get('plumbery.fittings', '.')
        if not os.path.isdir(root):
            self.mouth.put("Invalid path for fittings. Check configuration")
            return

        if arguments is None or len(arguments) == 0:
            count = 0
            for category in os.listdir(root):
                c_path = os.path.join(root,category)
                if not os.path.isdir(c_path):
                    continue
                if category[0] == '.':
                    continue
                if count == 0:
                    self.mouth.put("You can list templates in following categories:")
                count += 1
                self.mouth.put("- {}".format(category))
            if count == 0:
                self.mouth.put("No category has been found. Check configuration")
            return

        c_path = os.path.join(root,arguments)
        if not os.path.isdir(c_path):
            self.mouth.put("No category has this name. Double-check with the list command.".format(arguments))
            return

        count = 0
        for fittings in os.listdir(c_path):
            f_path = os.path.join(c_path,fittings)
            try:
                with open(os.path.join(f_path, 'fittings.yaml'), 'r') as f:
                    if count == 0:
                        self.mouth.put("You can use any of following templates:")
                    count += 1
                    self.mouth.put("- {}".format(arguments+'/'+fittings))
            except IOError:
                pass

        if count == 0:
            self.mouth.put("No template has been found in category '{}'".format(arguments))

    def do_parameters(self, argument=None):
        root =  self.context.get('plumbery.fittings', '.')
        if not os.path.isdir(root):
            self.mouth.put("Invalid path for fittings. Check configuration")
            return

        if argument is None or len(argument) < 1:
            argument = self.context.get('worker.template', 'example/first')

        if '/' not in argument:
            self.mouth.put("Please indicate the category and the template that you want to use.")
            return

        f_path = os.path.join(root,argument)
        try:
            with open(os.path.join(f_path, 'fittings.yaml'), 'r') as handle:
                plan = handle.read()
                documents = plan.split('\n---')
                for document in documents:
                    if '\n' in document:
                        settings = yaml.load(document)

                        if 'parameters' in settings:
                            self.mouth.put('Available parameters:')
                            for key in sorted(settings['parameters'].keys()):
#                                if 'parameter.'+key in parameters:
#                                    continue
                                if 'default' not in settings['parameters'][key]:
                                    raise ValueError("Parameter '{}' has no default value"
                                                     .format(key))
#                                parameters['parameter.'+key] = settings['parameters'][key]['default']
                                self.mouth.put('- {}: {}'.format(key, settings['parameters'][key]['default']))
                        else:
                            self.mouth.put('No parameter for {}'.format(argument))
                        break
                    else:
                        self.mouth.put('No parameter for {}'.format(argument))
        except IOError:
            self.mouth.put("No template has this name. Double-check with the list command.")

    def do_prepare(self, argument=None):
        if not self.context.get('worker.busy', False):
            self.mouth.put("Ok, working on it")
        else:
            self.mouth.put("Ok, will work on it as soon as possible")
        self.inbox.put(('prepare', argument))

    def do_refresh(self, argument=None):
        if not self.context.get('worker.busy', False):
            self.mouth.put("Ok, working on it")
        else:
            self.mouth.put("Ok, will work on it as soon as possible")
        self.inbox.put(('refresh', argument))

    def do_start(self, argument=None):
        if not self.context.get('worker.busy', False):
            self.mouth.put("Ok, working on it")
        else:
            self.mouth.put("Ok, will work on it as soon as possible")
        self.inbox.put(('start', argument))

    def do_status(self, argument=None):
        self.mouth.put("Using {}".format(self.context.get('worker.template', 'example/first')))
        if self.context.get('worker.busy', False):
            self.mouth.put("On-going processing")
        else:
            self.mouth.put("Ready to process commands")

    def do_stop(self, argument=None):
        if not self.context.get('worker.busy', False):
            self.mouth.put("Ok, working on it")
        else:
            self.mouth.put("Ok, will work on it as soon as possible")
        self.inbox.put(('stop', argument))

    def do_use(self, argument=None):
        root =  self.context.get('plumbery.fittings', '.')
        if not os.path.isdir(root):
            self.mouth.put("Invalid path for fittings. Check configuration")
            return

        if argument is None:
            self.mouth.put("Please indicate the category and the template that you want to use.")
            return

        if '/' not in argument:
            self.mouth.put("Please indicate the category and the template that you want to use.")
            return

        f_path = os.path.join(root,argument)
        try:
            with open(os.path.join(f_path, 'fittings.yaml'), 'r') as f:
                self.context.set('worker.template', argument)
                self.mouth.put("This is well-noted")
        except IOError:
            self.mouth.put("No template has this name. Double-check with the list command.")

    def do_version(self, argument=None):
        self.mouth.put("Version {}".format(self.context.get('plumby.version', '*unknown*')))
