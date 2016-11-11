#!/usr/bin/env python
from gevent import monkey; monkey.patch_all()
import json
import logging
import os
from Queue import Queue
import requests
from requests_toolbelt import MultipartEncoder
import sys
from threading import Thread
import time
import yaml
from bottle import route, run, request, abort

# the safe-thread store that is shared across components
#
from context import Context
context = Context()
context.set('plumby.version', '0.2 alpha')

# the queue of updates to be sent to Cisco Spark, processed by a Sender
#
mouth = Queue()

# the queue of reports from a Worker, processed by a Speaker
#
outbox = Queue()

# the queue of activities for a Worker, feeded by a Listener and Shell
#
inbox = Queue()

# the streams of information coming from Cisco Spark, handled by a Listener
#
ears = Queue()

# the sender of updates to Cisco Spark is processing the mouth queue
#
from sender import Sender
sender = Sender(mouth)

# the speaker translates reports from the outbox, and feeds the mouth
#
from speaker import Speaker
speaker = Speaker(outbox, mouth)

# the worker takes activities from the inbox and puts reports in the outbox
#
from worker import Worker
worker = Worker(inbox, outbox)

# the shell handles immediate commands and delegates others to the worker
#
from shell import Shell
shell = Shell(context, inbox, mouth)

# the listener acknowledges commands and feeds the worker via the inbox
#
from listener import Listener
listener = Listener(ears, shell)


# the endpoint exposed to Cisco Spark
#
@route("/", method=['GET', 'POST'])
def push_from_spark():
    """
    Processes the flow of events from Cisco Spark

    This function is called from far far away, over the Internet
    """

    try:

        print('Receiving data from webhook')

        # step 1 -- we got message id, but no content
        #
        message_id = request.json['data']['id']

        # step 2 -- get the message itself
        #
        url = 'https://api.ciscospark.com/v1/messages/{}'.format(message_id)
        bearer = context.get('spark.CISCO_SPARK_PLUMBERY_BOT')
        headers = {'Authorization': 'Bearer '+bearer}
        response = requests.get(url=url, headers=headers)

        if response.status_code != 200:
            raise Exception("Received error code {}".format(response.status_code))

        # step 3 -- push it in the handling queue
        #
        ears.put(response.json())

        return "OK\n"

    except Exception as feedback:
        print("ABORTED: fatal error has been encountered")
        raise


def pull_from_spark():
    """
    Processes the flow of events from Cisco Spark

    This function senses new items at regular intervals
    """

    print('Fetching data pro-actively')

    bearer = context.get('spark.CISCO_SPARK_PLUMBERY_BOT')
    room_id = context.get('spark.room_id')
    last_id = 0
    while self.context.get('general.switch', 'on') == 'on':

        try:
            url = 'https://api.ciscospark.com/v1/messages'
            headers = {'Authorization': 'Bearer '+bearer}
            payload = {'roomId': room_id, 'max': 10 }
            response = requests.get(url=url, headers=headers, data=payload)

            if response.status_code != 200:
                raise Exception("Received error code {}".format(response.status_code))

            items = response.json()['items']

            index = 0
            while index < len(items):
                if items[index]['id'] == last_id:
                    break
                index += 1

            if index > 0:
                print("Fetching {} new messages".format(index))

            while index > 0:
                index -= 1
                last_id = items[index]['id']
                ears.put(items[index])

            time.sleep(1)

        except Exception as feedback:
            print("ERROR: exception raised while fetching ùessages")
            raise


def delete_room(context):
    """
    Deletes the target Cisco Spark room

    This function is useful to restart a clean demo environment
    """

    room = context.get('spark.room')
    bearer = context.get('spark.CISCO_SPARK_PLUMBERY_BOT')

    print("Deleting Cisco Spark room '{}'".format(room))

    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {'Authorization': 'Bearer '+bearer}
    response = requests.get(url=url, headers=headers)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    actual = False
    for item in response.json()['items']:

        if room in item['title']:
            print("- found it")
            print("- DELETING IT")

            url = 'https://api.ciscospark.com/v1/rooms/{}'.format(item['id'])
            headers = {'Authorization': 'Bearer '+bearer}
            response = requests.delete(url=url, headers=headers)

            if response.status_code != 204:
                raise Exception("Received error code {}".format(response.status_code))

            actual = True

    if actual:
        print("- room will be re-created in Cisco Spark")
    else:
        print("- no room with this name yet")

    context.set('spark.room_id', None)

def get_room(context):
    """
    Looks for a suitable Cisco Spark room

    :return: the id of the target room
    :rtype: ``str``

    This function creates a new room if necessary
    """

    room = context.get('spark.room')
    bearer = context.get('spark.CISCO_SPARK_PLUMBERY_BOT')

    print("Looking for Cisco Spark room '{}'".format(room))

    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {'Authorization': 'Bearer '+bearer}
    response = requests.get(url=url, headers=headers)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    for item in response.json()['items']:
        if room in item['title']:
            print("- found it")
            return item['id']

    print("- not found")
    print("Creating Cisco Spark room")

    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {'Authorization': 'Bearer '+bearer}
    payload = {'title': room }
    response = requests.post(url=url, headers=headers, data=payload)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    print("- done")
    room_id = response.json()['id']
    context.set('spark.room_id', room_id)

    print("Adding moderators to the Cisco Spark room")

    for item in context.get('spark.moderators', ()):
        print("- {}".format(item))
        add_person(room_id, person=item, isModerator='true')

    print("Adding participants to the Cisco Spark room")

    for item in context.get('spark.participants', ()):
        print("- {}".format(item))
        add_person(room_id, person=item)

    print("Getting bot id")

    url = 'https://api.ciscospark.com/v1/people/me'
    headers = {'Authorization': 'Bearer '+bearer}
    response = requests.get(url=url, headers=headers)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    print("- done")
    context.set('spark.bot_id', response.json()['id'])

def add_person(room_id, person=None, isModerator='false'):
    """
    Adds a person to a room

    :param room_id: identify the target room
    :type room_id: ``str``

    :param person: e-mail address of the person to add
    :type person: ``str``

    :param isModerator: for medrators
    :type isModerator: `true` or `false`

    """

    url = 'https://api.ciscospark.com/v1/memberships'
    headers = {'Authorization': 'Bearer '+context.get('spark.CISCO_SPARK_PLUMBERY_BOT')}
    payload = {'roomId': room_id,
               'personEmail': person,
               'isModerator': isModerator }
    response = requests.post(url=url, headers=headers, data=payload)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))


def register_hook(context):
    """
    Asks Cisco Spark to send updates

    """

    room_id = context.get('spark.room_id')
    bearer = context.get('spark.CISCO_SPARK_PLUMBERY_BOT')
    webhook = context.get('server.url')

    print("Registering webhook to Cisco Spark")
    print("- {}".format(webhook))

    url = 'https://api.ciscospark.com/v1/webhooks'
    headers = {'Authorization': 'Bearer '+bearer}
    payload = {'name': 'controller-webhook',
               'resource': 'messages',
               'event': 'created',
               'filter': 'roomId='+room_id,
               'targetUrl': webhook }
    response = requests.post(url=url, headers=headers, data=payload)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    print("- done")

    mouth.put("Ready to take your commands starting with @plumby")
    mouth.put("For example, start with: @plumby help")

def configure(name="settings.yaml"):
    """
    Reads configuration information

    :param name: the file that contains configuration information
    :type name: ``str``

    The function loads configuration from the file and from the environment.
    Port number can be set from the command line.

    Look at the file `settings.yaml` that is coming with this project
    """

    print("Loading the configuration")

    with open(name, 'r') as stream:
        try:
            settings = yaml.load(stream)
            print("- from '{}'".format(name))
        except Exception as feedback:
            logging.error(str(feedback))
            sys.exit(1)

    if "spark" not in settings:
        logging.error("Missing spark: configuration information")
        sys.exit(1)

    if "room" not in settings['spark']:
        logging.error("Missing room: configuration information")
        sys.exit(1)

    if "moderators" not in settings['spark']:
        logging.error("Missing moderators: configuration information")
        sys.exit(1)

    if "bot" not in settings['spark']:
        settings['spark']['bot'] = 'plumby'

    if 'CISCO_SPARK_PLUMBERY_BOT' not in settings['spark']:
        token = os.environ.get('CISCO_SPARK_PLUMBERY_BOT')
        if token is None:
            logging.error("Missing CISCO_SPARK_PLUMBERY_BOT in the environment")
            sys.exit(1)
        settings['spark']['CISCO_SPARK_PLUMBERY_BOT'] = token

    if "plumbery" not in settings:
        logging.error("Missing plumbery: configuration information")
        sys.exit(1)

    if "fittings" not in settings['plumbery']:
        logging.error("Missing fittings: configuration information")
        sys.exit(1)

    if "server" not in settings:
        logging.error("Missing server: configuration information")
        sys.exit(1)

    if "url" not in settings['server']:
        logging.error("Missing url: configuration information")
        sys.exit(1)

    if len(sys.argv) > 1:
        try:
            port_number = int(sys.argv[1])
        except:
            logging.error("Invalid port_number specified")
            sys.exit(1)
    elif "port" in settings['server']:
        port_number = int(settings['server']['port'])
    else:
        port_number = 80
    settings['server']['port'] = port_number

    if 'DEBUG' in settings:
        debug = settings['DEBUG']
    else:
        debug = os.environ.get('DEBUG', False)
    settings['DEBUG'] = debug
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    return settings

# the program launched from the command line
#
if __name__ == "__main__":

    # read configuration file, look at the environment, and update context
    #
    context.apply(configure())

    # create a clean environment for the demo
    #
    delete_room(context)

    # create room if needed, and get its id
    #
    get_room(context)

    # ask Cisco Spark to send updates
    #
    register_hook(context)

    # start processing threads in the background
    #
    w = Thread(target=sender.work, args=(context,))
    w.setDaemon(True)
    w.start()

    w = Thread(target=speaker.work, args=(context,))
    w.setDaemon(True)
    w.start()

    w = Thread(target=worker.work, args=(context,))
    w.setDaemon(True)
    w.start()

    w = Thread(target=listener.work, args=(context,))
    w.setDaemon(True)
    w.start()

    print("Starting web endpoint")
    run(host='0.0.0.0',
        port=context.get('server.port'),
        debug=context.get('general.DEBUG'),
        server=os.environ.get('SERVER', 'gevent'))

