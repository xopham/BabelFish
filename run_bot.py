#!/usr/bin/env python3

import sys, os, time
from matrix_client.client import MatrixClient
from babel_fish import BabelFish
basepath = os.path.dirname(os.path.realpath(__file__))

# **** Prelude ****
info = dict()
bf = dict()

with open(os.path.join(basepath, "login")) as f:
    LOGINFO = f.read().splitlines()
USERNAME = LOGINFO[0]
PASSWORD = LOGINFO[1]
SERVER = 'https://' + LOGINFO[2]

# **** Parameters ****
# provide files with people lists for permissions (level owner or user). Owners can invite the bot into rooms.
# Users can benefit from the bot. Setting info['users'] or info['owners'] to "all" unresticts access
with open(os.path.join(basepath, 'owners')) as f:
    info['owners'] = f.read().splitlines()
# info['owners'] = 'all'
with open(os.path.join(basepath, 'users')) as f:
    info['users'] = f.read().splitlines()
# info['users']= 'all'

# **** Functions ****
def handle_message(room, event):
    """This function handles incoming matrix events and reacts on the keyword xkcd.

    :param room: Matrix room where message event occurred
    :param event: Matrix event of the message
    """
    bf[room.room_id].handle_event(event)


def handle_invite(room_id, state):
    """This function handles new invites to Matrix rooms by accepting them.

    :param room_id: Matrix room is
    :param state: State of the Matrix room
    """
    if state['events'][0]['sender'] in info['owners'] or info['owners'] == 'all':
        room = client.join_room(room_id)
        botinfo = info
        botinfo['room_id'] = room_id
        botinfo['room'] = room
        botinfo['state'] = state
        botinfo['caller'] = state['events'][0]['sender']
        bf[room_id] = BabelFish(botinfo)
        room.add_listener(handle_message)
        print('joined room %s' % room_id)
    else:
        print('Unauthorized user access in room %s. I will not join this room.' % room_id)


# **** Main ****
if __name__ == '__main__':
    client = MatrixClient(SERVER)
    client.login_with_password(USERNAME, PASSWORD)
    print('Login as %s successful' % USERNAME)
    client.add_invite_listener(handle_invite)
    for room_id, room in client.get_rooms().items():
        botinfo = info
        botinfo['room_id'] = room_id
        botinfo['room'] = room
        bf[room_id] = BabelFish(botinfo)
        room.add_listener(handle_message)
    client.start_listener_thread()
    print('Listeners started successfully')
    while True:
        time.sleep(0.2)