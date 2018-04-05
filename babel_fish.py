import os, time, sys, string
from googletrans import Translator

# Prelude
basepath = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(basepath, "login")) as f:
    LOGINFO = f.read().splitlines()
USERNAME = LOGINFO[0]
PASSWORD = LOGINFO[1]
SERVER = 'https://' + LOGINFO[2]


# Main
class BabelFish(object):
    """This is the BabelFish class that implements the matrix-bot "BabelFish"

        :param info: The dictionary with all relevant parameters.
            Needed parameters are: owners, users, room, room_id..
            Potential parameters:  ..
        :type info: dict
        """

    necessary_info = ('owners', 'users', 'room', 'room_id')

    def __init__(self, info):
        if not all(param in info for param in self.necessary_info):
            raise KeyError("Please provide all of the following parameters in a dict: %s"
                           % str(self.necessary_info))

        name = info['room_id'][1:info['room_id'].rfind(':')]

        print('Initializing BabelFish for room "' + info['room_id'] + '"...')

        self.info = dict()
        self.info['translate?'] = True
        self.info['ttl'] = 60 * 1000
        self.info['caller'] = ''
        for key in info:
            self.info[key] = info[key]
        self.info['name'] = name
        self.info['basepath'] = basepath
        self.info['username'] = '@' + USERNAME + ':' + LOGINFO[2]
        self.user_language = dict()

        print('...BabelFish ' + self.info['name'] + ' was born.')
        self.info['room'].send_text('Hello! I am BabelFish.')
        self.funcs = {'translate': self.translate, 'language': self.set_user_language,
                      'live_translate': self.switch_live_translate}

    def __del__(self):
        self.notes.note('info', 'BabelFish ' + self.info['name'] + ' is dead.')

    @staticmethod
    def __clean_sting__(txt):
        return ''.join(x for x in txt if x in string.printable)

    @staticmethod
    def __uniquify__(seq):
        return list(set(seq))

    def stop_bot(self):
        print('stopping BabelFish ' + self.info['name'] + '...')
        self.info['room'].send_text('bye')
        print('...BabelFish ' + self.info['name'] + ' stopped.')

    def status(self):
        print(self.info['name'] + ' IS ALIVE.')

    def handle_event(self, event):
        self.crnt_event = event
        if event['unsigned']['age'] < self.info['ttl'] and event['type'] == 'm.room.message':
            if self.crnt_event['content']['msgtype'] == 'm.text':
                self.crnt_sender = self.crnt_event['sender']
                self.crnt_msg = self.crnt_event['content']['body']
                if self.crnt_sender in self.info['users']:
                    self.live_translate()
                    self.handle_functions()
                elif self.crnt_sender == self.info['username']:
                    self.hello_message()
                else:
                    self.info['room'].send_text('no valid user!')

    def hello_message(self):
        if self.crnt_event['sender'] == self.info['username']:
            try:
                if self.crnt_event['content']['body'] == 'Hello! I am BabelFish.':
                    time.sleep(1)
                    self.info['room'].send_text(
                        'I am a artificial being. I will help you speak to other people in foreign languages.')
                    time.sleep(1)
                    self.info['room'].send_text(
                        'For now just tell me your language and you are good to go. The command is:\n"BabelFish: '
                        '-language your contry code (de for Germany)"')
                    self.info['room'].send_text(
                        'To learn more about my commands and functions, you can simply call "BabelFish:"\n   ')
                    introtext = 'Viel Spass beim Reden mit Menschen weltweit!'
                    self.info['room'].send_text('BabelFish: -translate ' + introtext)
                    self.translate(arg=introtext)
            except KeyError:
                return

    def list_commands(self):
        self.info['room'].send_text(
            'I am a artificial being. I will help you speak to people in foreign languages. You can command me via:' +
            '\n"BabelFish: -command argument of one or multiple words"')
        self.info['room'].send_text('Available commands are: ' + ', '.join(
            [key for key in self.funcs]) + '\nJust try them out!')
        self.info['room'].send_text(
            'To get information on the expected argument, call the function w/o argument "BabelFish: -command"')
        self.info['room'].send_text('To see the list of functions again, you can simply call "BabelFish:"\n   ')

        txt = 'Viel Spass! Verbinde Dich mit anderen Menschen auf der ganzen Welt...'
        self.info['room'].send_text('Example:\nBabelFish: -translate ' + txt)
        self.translate(arg=txt)

    def live_translate(self):
        if self.info['translate?'] and self.crnt_sender in self.user_language.keys() and self.__clean_sting__(self.crnt_msg):
            ldict = dict()
            for key, value in self.user_language.items():
                if key != self.crnt_sender:
                    ldict[key] = value

            languages = self.__uniquify__(list(ldict.values()))
            for language in languages:
                txt = Translator().translate(text=self.__clean_sting__(self.crnt_msg),dest=language).text
                print('live translating "%s" to "%s"' % (self.crnt_event['content']['body'], txt))
                self.info['room'].send_text(self.crnt_event['sender'] + '> ' + txt)

    def handle_functions(self):
        if self.crnt_event['sender'] != self.info['username']:
            msg = self.crnt_msg
            try:
                if msg[0:len(USERNAME) + 1] == USERNAME + ':' and msg[len(USERNAME) + 2] == '-':
                    try:
                        cmd = msg[len(USERNAME) + 3:msg[len(USERNAME) + 3:].index(' ') + len(USERNAME) + 3]
                        arg = msg[msg[len(USERNAME) + 3:].index(' ') + len(USERNAME) + 4:]
                    except ValueError:
                        cmd = msg[len(USERNAME) + 3:]
                        arg = ''
                    print('do command "%s", with arg "%s"' % (cmd, arg))
                    try:
                        self.funcs[cmd](arg)
                    except KeyError:
                        print('function "%s" is not known' % cmd)
                        return
            except IndexError:
                if msg == USERNAME + ': ' or msg == USERNAME + ':':
                    self.list_commands()
                else:
                    print('"%s" is no valid input' % msg)

    def translate(self, arg):
        if arg:
            txt = Translator().translate(text=self.__clean_sting__(arg)).text
            print('translating "%s" to "%s"'%(arg,txt))
            self.info['room'].send_text(txt)
        else:
            print('requesting information on translate function')
            self.info['room'].send_text('arg: str (simple string of one or multiple words)')

    def switch_live_translate(self, arg):
        if arg:
            self.info['translate?'] = arg not in ['FALSE', 'False', 'false', 'F', 'f', 'OFF', 'Off', 'off', '0']
            print('live translate is now %s' % str(self.info['live translate?']))
            self.info['room'].send_text('live translate is now set to "%s".' % str(self.info['live translate?']))
        else:
            print('requesting information on live_translate function')
            self.info['room'].send_text('arg: bool ("T" or "F" or the like)')

    def set_user_language(self, arg):
        if arg:
            try:
                Translator().translate(text='hello', dest=arg)
                self.user_language[self.crnt_sender] = arg
                print('user "%s" set his/her language to %s' % (self.crnt_sender, arg))
                self.info['room'].send_text('user "%s" set his/her language to "%s"' % (self.crnt_sender, arg))
            except:
                print('invalid language code')
                self.info['room'].send_text('"%s" is an invalid language code' % arg)
        else:
            print('requesting information on set_user_language function')
            self.info['room'].send_text('arg: str (country codes like "eng", "de" or "fr")')
#     allow owner to add users live!
