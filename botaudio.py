import os, json, time
import sys
from subprocess import check_call
from pydub import AudioSegment
from pydub.utils import mediainfo
from DBmodul import dbbot
from Faceaudiobot import faceaudiobot
from Facefind import facefind


def init_conf():
    with open(os.path.abspath('config/config.json')) as f:
        return json.load(f)


def init_telegrambot(vd=dbbot.DbHelper(os.path.abspath('DBmodul/audiodb.db'))):
    return faceaudiobot.Telegramaudiobot(TOKENBOT=init_conf()['DEFAULT']['TOKENBOT'],
                                         databese=vd,
                                         MANAGERID=init_conf()['DEFAULT']['MANAGERID'])


def run_bot():
    audioface = init_telegrambot()
    audioface.init_db()                            # инициализируем базу данных.
    files = os.listdir(os.path.abspath('./model')) # получаем список файлов(моделей) для проверки изображений.
    myxml = sorted(tuple(filter(lambda x: x.endswith('.xml'), files)), reverse=True)
    status_user = ('start', 'photo', 'audio')      # состояния пользователя.

    try:
        from subprocess import DEVNULL
    except ImportError:
        DEVNULL = open(os.devnull, 'r+b', 0)

    check_call(["python", "-c", "import sys; sys.stdin.readline()"], stdin=DEVNULL)

    # обработчик начала диалога.
    @audioface.bot.message_handler(commands=['start'])
    def go_start(message):
        return audioface.start(message=message)

    # переходим в режим распознования лиц.
    @audioface.bot.callback_query_handler(func=lambda call: call.data.startswith("findfase"))
    def go_findface(call):
        return audioface.findfase_reply(call=call)

    # переходим в режим аудиосообщений.
    @audioface.bot.callback_query_handler(func=lambda call: call.data.startswith("audiomessage"))
    def go_audio(call):
        return audioface.audio_reply(call=call)

    # нажимаем кнопку "Назад" и возращаемся в режим начала диалога.
    @audioface.bot.callback_query_handler(func=lambda call: call.data.startswith("back"))
    def get_reset(call):
        return audioface.go_reset(call=call)

    # распознаем изображение, при наличии лица сохраняем на диск.
    @audioface.bot.message_handler(content_types=['photo'], func=lambda message: audioface.valid_status(user_id=message.from_user.id)[0] == 'photo')
    def find_face_photo(message):
        photo = audioface.bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_photo = audioface.bot.download_file(photo.file_path)
        with open(os.path.abspath('temporaryfile/' + f'{photo.file_path}'), 'wb') as new_foto:
            new_foto.write(downloaded_photo)
        file_photo = os.listdir(os.path.abspath('./temporaryfile/photos'))[0]
        lookforface = facefind.Lookforface(file_name=os.path.abspath('./temporaryfile/photos/' + f'{file_photo}'),
                                           model_name=myxml)
        if lookforface.get_face():
            with open(
                    os.path.abspath('fileimageface/' + 'from_user' + f'{message.from_user.id}' + '_' + f'{file_photo}'),
                    'wb') as new_foto:
                new_foto.write(downloaded_photo)
            audioface.bot.reply_to(message, "Фото сохранил. На изображении есть лицо!")
        else:
            audioface.bot.reply_to(message, "На фото нет лица.")
        os.remove(os.path.abspath('./temporaryfile/photos/' + f'{file_photo}'))
        audioface.bot.send_message(message.chat.id,
                                   'Если хотите продолжить то пришлите еще фотографию.'+'\n'+'Если хотите вернутся к началу нажмите кнопку "Назад".',
                                   reply_markup=audioface.go_back())

    # принимаем аудиосообщение и конвертируем в формат ".wav" с частотой семплирования 16 kHz.
    @audioface.bot.message_handler(content_types=['voice'], func=lambda message: audioface.valid_status(user_id=message.from_user.id)[0] == 'audio')
    def convert_audio(message):
        audio_message = audioface.bot.get_file(message.voice.file_id)
        downloaded_audio = audioface.bot.download_file(audio_message.file_path)
        count_user_file = audioface.valid_user(user_id=message.from_user.id)[0]
        user_id = message.from_user.id
        with open(os.path.abspath('temporaryfile/' + f'{audio_message.file_path}'), 'wb') as new_audio:
            new_audio.write(downloaded_audio)
        sound = AudioSegment.from_ogg(
            os.path.abspath('./temporaryfile/voice/' + os.listdir('./temporaryfile/voice')[0])).set_frame_rate(16000)
        sound.export((os.path.abspath(
            './fileaudio/' + 'from_user' + f'{user_id}' + '_audio_message_' + f'{count_user_file}' + '.wav')),
                     format='wav')
        os.remove(os.path.abspath('temporaryfile/' + f'{audio_message.file_path}'))
        with open(os.path.abspath(
                './fileaudio/' + 'from_user' + f'{user_id}' + '_audio_message_' + f'{count_user_file}' + '.wav'),
                  'rb') as db_audio:
            db_info = db_audio.read()
            audioface.write_in_bd(user_id=user_id, format='wav', audio_file=db_info,
                                  count_user_file=count_user_file, name_audio='audio_message_')
        audioface.bot.reply_to(message,
                               'Аудиосообщение добавил в базу с именем:' + '\n' + 'from_user' + f'{user_id}' + '_audio_message_' + f'{count_user_file}' + '.wav')
        audioface.bot.send_message(message.chat.id,
                                   'Если хотите продолжить, то пришлите еще одно голосовое сообщение.' + '\n' + 'Если хотите вернуться к началу, нажмите кнопку "Назад".',
                                   reply_markup=audioface.go_back())

    # обработчик ситуаций когда пользователь посылает другие данные находясь в режиме приема фотографий.
    @audioface.bot.message_handler(content_types=['voice', 'audio', 'text', 'video', 'sticker', 'location'],
                                   func=lambda message: audioface.valid_status(user_id=message.from_user.id)[0] == 'photo')
    def report_an_error_photo(message):
        audioface.bot.send_message(message.chat.id,
                                   'Я сейчас в режиме распознавания лиц.' + '\n' + 'Для смены режима нажмите кнопку "Назад" или пришлите фотографию чтобы продолжить.',
                                   reply_markup=audioface.go_back())

    # обработчик ситуаций когда пользователь посылает другие данные находясь в режиме приема аудиосообщений.
    @audioface.bot.message_handler(content_types=['photo', 'audio', 'text', 'video', 'sticker', 'location'],
                                   func=lambda message: audioface.valid_status(user_id=message.from_user.id)[0] == 'audio')
    def report_an_error_audio(message):
        audioface.bot.send_message(message.chat.id,
                                   'Я сейчас в режиме преобразования голосовых сообщений.' + '\n' + 'Для смены режима нажмите кнопку "Назад" или пришлите голосовое сообщение чтобы продолжить.',
                                   reply_markup=audioface.go_back())


    audioface.bot.polling(none_stop=True, interval=0)



if __name__=='__main__':

    while True:
        try:
            run_bot()
        except:
            print('я сломался')
            time.sleep(20)
            continue
