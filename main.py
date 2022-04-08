# -*- coding: utf-8 -*-
import telebot
from telebot import types;
import json

BOT = telebot.TeleBot("")

USERS = {}
women = ["Катя", "Полина", "Ксюша"]
man = ['Никита', 'Серёжа', 'Глеб']
NOMINATIONS = {
    "Мисс ФФМиЕН": women,
    "Мисс харизма": women,
    "Самая стильная": women,
    "Мистер ФФМиЕН": man, 
    "Любимец публики": man,
    "Талант года": man
}

VOTES = {}
RESULTS = {}

for nomination, participants in NOMINATIONS.items():
    RESULTS[nomination] = {}
    for participant in participants:
        RESULTS[nomination][participant] = 0
try:
    with open("database.json", "r") as dbfile:
        all_lines = dbfile.readlines()
        joined_lines = "".join(all_lines)
        USERS = json.loads(joined_lines)
except:
    pass

try:
    with open("database2.json", "r") as dbfile:
        all_lines = dbfile.readlines()
        joined_lines = "".join(all_lines)
        GAMES = json.loads(joined_lines)
except:
    pass

@BOT.message_handler(content_types=['text'])
def on_message(message):
    user_id = str(message.from_user.id)
    if message.text == '/start':
        nick = message.from_user.username
        name = message.from_user.first_name
        surname = message.from_user.last_name
        if not user_id in VOTES:
            new_voter(user_id)
        else:
            BOT.send_message(user_id, 'Я же просил, не прокатит')
            return
        if not user_id in USERS :
            USERS[user_id] = {"nick": nick, "name": name, "surname": surname}
            BOT.send_message(user_id, f"Привет!\nПожалуйста, прочитайте все сообщения, которые отправляет бот, чтобы не возникало вопросов\n\nНемного инструкций: нажимая команду 'проголосовать' вы будете поочередно голосовать в одной номинации за одного участника. Голосование за определенного участника в определенной номинации происходит путём нажатия кнопки с именем участника конкурса.\n!!!У вас будет только одна попытка голосования!!!\nПодумайте перед тем, как отдавать свой голос\n\nСписок женских номинаций:\n'Мисс ФФМиЕН'\n'Мисс харизма'\n'Самая стильная на факультете'\n\nСписок мужских номинаций:\n'Мистер ФФМиЕН'\n'Талант года'\n'Любимец публики'\n\nКоманды, чтобы посмотреть участниц и участников, или начать голосование, находятся в /help")
        else:    
            BOT.send_message(user_id, "У этого бота есть несколько команд. Напиши /помогите, чтобы посмотреть их!")
        return
    if message.text == "/help":
        BOT.send_message(user_id, "Данный бот имеет 5 команд:\n\n/start(Регистрация голосующего !!!не используйте повторно!!!\n/help (вывод всех возможных команд)\n/Okay (проголосовать за всех участников во всех номинациях)\n/girls (показать всех участниц)\n/boys (показать всех участников)")
        return
    if message.text == '/Okay':
        if len(VOTES)<60:
            next_vote(user_id)
            return
        else:
            BOT.send_message(user_id, 'Количество людей желающих проголосовать превышает количество зрителей в зале. Просим прощения!')
            return
    if message.text == '/girls':
        sendpic1(user_id)
        return
    if message.text == '/boys':
        sendpic2(user_id)
        return
    BOT.send_message(user_id, "Я не знаю такой команды\nИспользуй /help")


def make_keyboard(user_id, nomination):
    all_participants = set(NOMINATIONS[nomination])
    for vote_record in VOTES[user_id]:
        vote = vote_record["vote"]
        if not vote == None:
            all_participants.discard(vote)
    
    kb = types.InlineKeyboardMarkup();
    for remaining_participant in all_participants:
        button = types.InlineKeyboardButton(text=remaining_participant, callback_data=f"{user_id}_{remaining_participant}_{nomination}")
        kb.add(button)

    return kb

@BOT.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    items = call.data.split("_")
    user_id, participant, nomination = items
    user_votes = VOTES[user_id]
    for vote_dict in user_votes:
        if vote_dict['nomination'] == nomination:
            vote_dict['vote'] = participant
            update_results(nomination, participant)
    BOT.edit_message_reply_markup(user_id, call.message.id, reply_markup=None)
    next_vote(user_id)

def next_vote(user_id):
    user_votes = VOTES[user_id]
    for vote_dict in user_votes:
        if vote_dict['vote'] == None:
            nomination = vote_dict['nomination']
            BOT.send_message(user_id, f'Кого ты выберешь в номицации {nomination}?', reply_markup=make_keyboard(user_id, nomination))
            return
    BOT.send_message(user_id, 'Большое спасибо за участие в голосовании!')


def new_voter(user_id):
   VOTES[user_id] = []
   for nomination in NOMINATIONS.keys():
       VOTES[user_id].append({"nomination": nomination, "vote": None})

def write_json(what, where):
    with open(where, 'w') as file:
        json_line =  json.dumps(what, indent=4, ensure_ascii=False)
        file.write(json_line)

def update_results(nomination, participant):
    RESULTS[nomination][participant] = int(RESULTS[nomination][participant]) + 1 
    write_json(RESULTS, 'results.json')
def sendpic1(user_id):
    kate = open('Kate.jpg', 'rb')
    polina = open('polina.jpg', 'rb')
    ksusha = open('ksusha.jpg', 'rb') 
    BOT.send_message(user_id, 'Тихонова Екатерина')
    BOT.send_photo(user_id, kate)
    BOT.send_message(user_id, 'Чусовитина Полина')
    BOT.send_photo(user_id, polina)
    BOT.send_message(user_id, 'Кувшинова Ксения')
    BOT.send_photo(user_id, ksusha)
    kate.close()
    polina.close()
    ksusha.close()
    BOT.send_message(user_id, 'Чтобы посмотреть участников пропишите /boys\n\nДля начала голосования пропишите /Okay')
def sendpic2(user_id):
    gleb = open('gleb.jpg', 'rb')
    serega = open('serega.jpg', 'rb')
    nikita = open('nikita.jpg', 'rb') 
    BOT.send_message(user_id, 'Бобков Глеб')
    BOT.send_photo(user_id, gleb)
    BOT.send_message(user_id, 'Вакуленко Сергей')
    BOT.send_photo(user_id, serega)
    BOT.send_message(user_id, 'Гамаюнов Никита')
    BOT.send_photo(user_id, nikita)
    gleb.close()
    serega.close()
    nikita.close()
    BOT.send_message(user_id, 'Чтобы посмотреть участниц пропишите /girls\n\nДля начала голосования пропишите /Okay')
BOT.polling(none_stop=True)
