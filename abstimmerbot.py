import subprocess
import random
import yaml
import sys
import time
import logging
import json
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from github import Github
from uuid import uuid4

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
level=logging.INFO)

with open('config.yml', 'r') as cf:
    config = yaml.safe_load(cf)
with open('strings.yml', 'r') as sf:
    phrase = yaml.safe_load(sf)
dfile = 'data.yml'


def read_data():
    with open(dfile, 'r') as df:
        data = yaml.safe_load(df)
    return data

def write_data(data):
    with open(dfile, 'w') as df:
        yaml.safe_dump(data, df)
    return

def get_commandlist(botfather=False):
    answ = ''
    for cmd in commands:
        if botfather:
            answ += '{} - {}\n'.format(cmd['name'], cmd['desc'])
        else:
            answ += '/{} - _{}_\n'.format(cmd['name'], cmd['desc'])
    return answ

def reply(update, text):
    update.message.reply_text(text=text, quote=False, pase_mode='Markdown')









def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=phrase['start'], quote=False)


def setup(bot, update):
    mess = bot.send_message(chat_id=update.message.chat_id, text=' ... ')
    print(mess)
    return


def botsay(bot, update, args):
    answ = ' '.join(args)
    bot.send_message(chat_id=group_id, text=answ, quote=False, parse_mode='Markdown')


def help(bot, update):
    answ = get_commandlist()
    update.message.reply_text(text=answ, quote=False, parse_mode='Markdown')


def new_vote(bot, update, args, user_data, chat_data):
    if len(args) < 1:
        reply(update, 'Ich brauche wenigstens einen Titel (optionen können durch ; getrennt folgen)')
        return
    id = str(uuid4())
    chat_data['active'] = id
    items = ' '.join(args).split(';')
    items = [i.strip() for i in items]
    while '' in items:
        items.remove('')
    title = items[0]
    if len(items) > 1:
        options = items[1:]
    else:
        options = []
    vote = {'title': title, 'options': []}
    for opt in options:
        vote['options'].append({'name': opt, 'y': []})
    if not 'votes' in chat_data:
        #reply(update, phrase['firstvote'])
        chat_data['votes'] = {}
    chat_data['votes'][id] = vote
    answ = '*{}*\n'.format(title)
    buttons = []

    for i, opt in enumerate(options):
        buttons.append([telegram.InlineKeyboardButton(opt, callback_data='vote;'+id+';'+str(i))])
    answer = {'text': answ, 'quote': False, 'parse_mode':'Markdown'}
    keyboard = buttons

    reply_markup = InlineKeyboardMarkup(keyboard)
    if len(buttons) > 0:
        try:
            update.message.reply_text(answ, reply_markup=reply_markup, quote=False, parse_mode='Markdown')
        except Exception as e:
            print(e)
    else:
        update.message.reply_text(answ, quote=False, parse_mode='Markdown')


def update_vote(message, chat_data, voteid):
    vote = chat_data['votes'][voteid]
    answ = '*{}*\n'.format(vote['title'])
    buttons = []
    for i, opt in enumerate(vote['options']):
        btn_name = '[{}] {}'.format(len(opt['y']), opt['name'])
        cb_data = ';'.join(['vote', voteid, str(i)])
        buttons.append([InlineKeyboardButton(btn_name, callback_data=cb_data)])
    keyboard = InlineKeyboardMarkup(buttons)
    message.edit_reply_markup(text='hello', reply_markup=keyboard)





def print_data(bot, update, user_data, chat_data):
    d = 'chat: {}\nuser: {}'.format(chat_data, user_data)
    reply(update, d)


def callback(bot, update, user_data, chat_data):
    query = update.callback_query
    data = query.data.split(';')
    print(data)
    print(chat_data)
    if data[0] == 'vote':  # toggle vote option
        #print(chat_data)
        subscribers = chat_data['votes'][data[1]]['options'][int(data[2])]['y']
        if query.from_user.id in subscribers:
            subscribers.remove(query.from_user.id)
        else:
            subscribers.append(query.from_user.id)
        #update:
        update_vote(query.message, chat_data, data[1])








if __name__ == '__main__':
    data = read_data()
    updater = Updater(token=config['token'])
    dispatcher = updater.dispatcher
    commands = [
    {'name': 'start','func': start, 'desc': 'Wilkommensnachricht', 'args':False},
    {'name': 'help', 'func': help, 'desc': 'Befehlsübersicht', 'args':False},
    {'name': 'vote', 'func': new_vote, 'desc': 'Voting erstellen, name; opt1; opt2; opt3...', 'args':True, 'data':True},
    {'name': 'setup', 'func': setup, 'desc': 'Einstellungen für aktuellen Chat..'},
    {'name': 'printdata', 'func': print_data, 'desc': 'debug static data variables', 'data':True},
    ##{'name': 'keytest', 'func': keytest, 'desc': 'debug keyboard'},

    ]
    callback_handler = telegram.ext.CallbackQueryHandler(callback, pass_chat_data=True, pass_user_data=True)
    dispatcher.add_handler(callback_handler)
    handlers = {}
    for cmd in commands:
        handlers[cmd['name']] = CommandHandler(cmd['name'], cmd['func'],
                                            pass_args=cmd.get('args', False),
                                            pass_user_data=cmd.get('data', False),
                                            pass_chat_data=cmd.get('data', False))
        dispatcher.add_handler(handlers[cmd['name']])
    # hidden cmds
    botsay_handler = CommandHandler('botsay', botsay, pass_args=True)
    dispatcher.add_handler(botsay_handler)
    updater.start_polling()
