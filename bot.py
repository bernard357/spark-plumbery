#!/usr/bin/env python
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

# the queue of updates to be sent to Cisco Spark, processed by a Sender
#
mouth = Queue()

# the queue of reports from a Worker, processed by a Speaker
#
outbox = Queue()

# the queue of activities for a Worker, feeded by a Listener
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

# the listener acknowledges commands and feeds the worker via the inbox
#
from listener import Listener
listener = Listener(ears, inbox, mouth)


# the endpoint exposed to Cisco Spark
#
@route("/", method=['GET', 'POST'])
def from_spark():
    """
    Processes the flow of events from Cisco Spark

    This function is called from far far away, over the Internet
    """

    print("Button has been pressed")

    try:

        # step 1 - get a room, or create one if needed
        #
        room_id = get_room()

        # step 2 - ensure they are some listeners here
        #
        add_audience(room_id)

        # step 3 - send a message, or upload a file, or both
        #
        update = build_update()

        # step 4 - do the actual update
        #
        post_update(room_id=room_id, update=update)

        print("Cisco Spark has been updated")
        return "OK\n"

    except Exception as feedback:
        print("ABORTED: fatal error has been encountered")
        print(str(feedback))
        return str(feedback)+'\n'


def get_room():
    """
    Looks for a suitable Cisco Spark room

    :return: the id of the target room
    :rtype: ``str``

    This function creates a new room if necessary
    """

    print("Looking for Cisco Spark room '{}'".format(settings['room']))

    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_PLUMBERY_BOT']}
    response = requests.get(url=url, headers=headers)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    for item in response.json()['items']:
        if settings['room'] in item['title']:
            print("- found it")
            return item['id']

    print("- not found")
    print("Creating Cisco Spark room")

    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_PLUMBERY_BOT']}
    payload = {'title': settings['room'] }
    response = requests.post(url=url, headers=headers, data=payload)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    print("- done")
    return response.json()['id']

def delete_room():
    """
    Deletes the target Cisco Spark room

    This function is useful to restart a clean demo environment
    """

    print("Deleting Cisco Spark room '{}'".format(settings['room']))

    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_PLUMBERY_BOT']}
    response = requests.get(url=url, headers=headers)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    actual = False
    for item in response.json()['items']:

        if settings['room'] in item['title']:
            print("- found it")
            print("- DELETING IT")

            url = 'https://api.ciscospark.com/v1/rooms/{}'.format(item['id'])
            headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_PLUMBERY_BOT']}
            response = requests.delete(url=url, headers=headers)

            if response.status_code != 204:
                raise Exception("Received error code {}".format(response.status_code))

            actual = True

    if actual:
        print("- room will be re-created in Cisco Spark")
    else:
        print("- no room with this name yet")

    settings['shouldAddModerator'] = True

def add_audience(room_id):
    """
    Gives a chance to some listeners to catch updates

    :param room_id: identify the target room
    :type room_id: ``str``

    This function adds pre-defined listeners to a Cisco Spark room if necessary
    """

    if settings['shouldAddModerator'] is False:
        return

    print("Adding moderator to the Cisco Spark room")

    url = 'https://api.ciscospark.com/v1/memberships'
    headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_PLUMBERY_BOT']}
    payload = {'roomId': room_id,
               'personEmail': settings['CISCO_SPARK_PLUMBERY_MAN'],
               'isModerator': 'true' }
    response = requests.post(url=url, headers=headers, data=payload)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    print("- done")

    settings['shouldAddModerator'] = False

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

    if "room" not in settings:
        logging.error("Missing room: configuration information")
        sys.exit(1)

    if "plumbery" not in settings:
        logging.error("Missing plumbery: configuration information")
        sys.exit(1)

    if len(sys.argv) > 1:
        try:
            port_number = int(sys.argv[1])
        except:
            logging.error("Invalid port_number specified")
            sys.exit(1)
    elif "port" in settings:
        port_number = int(settings["port"])
    else:
        port_number = 80
    settings['port'] = port_number

    if 'DEBUG' in settings:
        debug = settings['DEBUG']
    else:
        debug = os.environ.get('DEBUG', False)
    settings['DEBUG'] = debug
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    if 'CISCO_SPARK_PLUMBERY_BOT' not in settings:
        token = os.environ.get('CISCO_SPARK_PLUMBERY_BOT')
        if token is None:
            logging.error("Missing CISCO_SPARK_PLUMBERY_BOT in the environment")
            sys.exit(1)
        settings['CISCO_SPARK_PLUMBERY_BOT'] = token

    if 'CISCO_SPARK_PLUMBERY_MAN' not in settings:
        emails = os.environ.get('CISCO_SPARK_PLUMBERY_MAN')
        if emails is None:
            logging.error("Missing CISCO_SPARK_NTTN_MAN in the environment")
            sys.exit(1)
        settings['CISCO_SPARK_PLUMBERY_MAN'] = emails

    settings['count'] = 0

    return settings

# the program launched from the command line
#
if __name__ == "__main__":

    # read configuration file, look at the environment, and update context
    #
    context.apply(configure())

    # create a clean environment for the demo
    #
    delete_room()

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
        port=settings['port'],
        debug=settings['DEBUG'],
        server=os.environ.get('SERVER', "auto"))

