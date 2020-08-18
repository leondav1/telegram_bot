import urllib

import cv2
import telebot

try:
    import config
except ImportError:
    exit('Do cp config.py.default config.py and set token!')


bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}👋\n'
                                      f'Отправьте фото, либо графический файл в чат '
                                      f'и я скажу вам, есть лицо на фото или нет.'
                                      f'Конечно, я пока не идеальный, поэтому могу немножко ошибаться))')


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет')
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAMLXypkoZmlRuZnrV7YfHL38PJP3L0AAqMJAAJ5XOIJdgKQ_ca2-QwaBA')
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'Пока, пока')
    else:
        bot.send_message(message.chat.id, 'Пока я не могу ответить на это сообщение')


@bot.message_handler(content_types=["document"])
def handle_docs_audio(message):
    if not message.document.thumb:
        bot.send_message(message.chat.id, 'К сожалению, я пока не умею обрабатывать файл такого формата')
        return
    document_id = message.document.file_id
    file_info = bot.get_file(document_id)
    urllib.request.urlretrieve(f'http://api.telegram.org/file/bot{config.TOKEN}/{file_info.file_path}', file_info.file_path)
    face_cascade_funk(file_info, message)


def view_image(image, name_of_window):
    """
    Функция для отображения изображений в окнах windows
    """
    cv2.namedWindow(name_of_window, cv2.WINDOW_NORMAL)
    cv2.imshow(name_of_window, image)
    cv2.waitKey()
    cv2.destroyAllWindows()


@bot.message_handler(content_types=['photo'])
def send_photo(message):
    photos = message.photo[-1]
    photo_id = photos.file_id
    file_info = bot.get_file(photo_id)
    urllib.request.urlretrieve(f'http://api.telegram.org/file/bot{config.TOKEN}/{file_info.file_path}', file_info.file_path)
    face_cascade_funk(file_info, message)


def face_cascade_funk(file_info, message):
    """
    Функция распознаёт лица на фото, рисует квадраты вокруг лиц
    и отправляет фото обратно в чат
    """
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    image = cv2.imread(file_info.file_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=11,
        minSize=(10, 10),
    )
    # Рисуем квадраты вокруг лиц
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 10)
    new_image_path = file_info.file_path.replace('photos', 'photos_results')
    cv2.imwrite(new_image_path, image)
    file = open(new_image_path, 'rb')
    if len(faces):
        bot.send_photo(message.chat.id, file)
        bot.send_message(message.chat.id, f'Количество распознанных лиц на фото: {len(faces)}')
    else:
        bot.send_message(message.chat.id, 'На фото лиц необнаружено')
    file.close()
    # view_image(image, 'Detected face')


@bot.message_handler(content_types=['sticker'])
def send_sticker(message):
    print(message.sticker)


bot.polling(none_stop=True, timeout=123)
