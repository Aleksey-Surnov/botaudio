import os, json, csv
from telebot import types
import telebot
from datetime import datetime, timedelta


class Telegramaudiobot():
    def __init__(self, TOKENBOT, databese, MANAGERID):
        self.tokenbot = TOKENBOT                            # токен бота telegram
        self.bot = telebot.TeleBot(token=self.tokenbot)
        self.vd = databese                                  # название базы данных
        self.managerid = int(MANAGERID)                     # id администратора.

    def start(self, message):
        self.bot.send_message(message.from_user.id, 'Здравствуйте. Я тестовый бот. У меня есть навыки: '
                                                    '\n1. Распознавания лиц на фотографиях.'
                                                    '\n2. Конвертирования аудиосообщений в формат ".wav" c частотой 16kHz.'
                                                    '\nДля распознавания лиц нажмите кнопку "Найти лицо".'
                                                    '\nДля конвертирования аудиосообщений в формат ".wav" нажмите кнопку "Конвертер аудиосообщений".', parse_mode="Markdown")
        self.bot.send_message(message.chat.id, "Сделайте выбор нажав кнопку:", reply_markup=self.main_keybard())
        count = self.vd.verify_status(user_id=message.from_user.id)[0]
        if count >= 1:             # на тот случай если пользователь несколько раз введет "/start".
            self.vd.delete_status(user_id=message.from_user.id)
        self.vd.add_status(user_id=message.from_user.id, status='start')

    def main_keybard(self):         # создаем клавиатуру выбора режимов.
        keyboardmain = types.InlineKeyboardMarkup()
        foto_button = types.InlineKeyboardButton(text="Найти лицо", callback_data="findfase")
        audio_button = types.InlineKeyboardButton(text="Конвертер аудиосообщений", callback_data="audiomessage")
        keyboardmain.add(audio_button)
        keyboardmain.add(foto_button)
        return keyboardmain

    def findfase_reply(self, call): # режим обработчика фотографий.
        self.vd.change_status(status='photo', user_id=call.from_user.id)
        self.bot.send_message(call.message.chat.id, text = 'Пришлите мне фотографию чтобы я мог определить есть ли на ней лицо человека.')

    def audio_reply(self, call):    # режим обработчика аудиосообщений.
        self.vd.change_status(status='audio', user_id=call.from_user.id)
        self.bot.send_message(call.from_user.id, text = 'Пришлите мне аудиосообщение для конвертации в формат ".wav" с частотой дискретизации 16kHz.'
                                                           '\nДля этого нажмите значок микрофона и удерживайте его до тех пор пока будете говорить.'
                                                           '\nКак только закончите запись отпустите значок микрофона.')

    def write_in_bd(self, user_id, format, audio_file, count_user_file, name_audio):
        self.vd.add_audio_message(user_id=user_id, format='wav', audio_file=audio_file,
                                  count_user_file=count_user_file, name_audio=name_audio)

    def go_back(self):               # клавиатура возврата.
        keyboardback = types.InlineKeyboardMarkup(row_width=1)
        back_button = types.InlineKeyboardButton(text="<<- Назад", callback_data="back")
        keyboardback.add(back_button)
        return keyboardback

    def go_reset(self, call):        # возврат в режим начала диалога.
        self.vd.change_status(status='start', user_id=call.from_user.id)
        self.bot.send_message(call.message.chat.id, "Давайте снова."+"\n"+"Сделайте выбор нажав кнопку:", reply_markup=self.main_keybard())

    def valid_user(self, user_id):   # проверка пользователя.
        return self.vd.verify_user(user_id=user_id)

    def valid_status(self, user_id): # запрос состояния (режима) пользователя в БД.
        return self.vd.get_status(user_id=user_id)

    def init_db(self):
        return self.vd.init_db()



















