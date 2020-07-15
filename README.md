# botaudio
Простой тестовый telegram бот для DSP Labs для telegram. Программа преобразует аудиосообщение от пользователя в формат ".wav" с частотой дискретизации 16кГц и распознает лица на фотографиях.

## Конфигурация и запуск:
- получить token бота в telegram от @BotFather
- заполнить файл /config/config.json следющим образом:
    - **MANAGERID**: ваш id в сети telegram.
    - **TOKENBOT**: token бота в telegram.
- Перед запуском программы установите зависимости командой в консоли `pip install -r requirements.txt`
- ВАЖНО: для правильной работы бота необходимо отдельно поставить **ffmpeg**. Он необходим для правильной работы pydub.
    - **Linux Ubuntu**: `apt-get install ffmpeg libavcodec-extra`
    - **Windows**: просто скачайте ffmpeg lib, распакуйте и добавьте `\ffmpeg\bin(В папке 3 файла ffmpeg.exe, ffplay.exe, ffprobe.exe)` в папку вашего проекта. 
    - Обязательно проверьте пути! Подробнее о установке на все ОС читайте здесь https://github.com/jiaaro/pydub

