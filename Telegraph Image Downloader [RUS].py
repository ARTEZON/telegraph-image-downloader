# Telegraph Image Downloader
# Автор: ARTEZON (vk.com/artez0n)
#
# Версия 1.2.1
#
# --------------------------------------------------
# -= НАСТРОЙКИ =-
# --------------------------------------------------
# Язык (string)
# Возможные варианты: ENG, RUS, JPN, CHN, KOR и другие
# language = 'RUS'
# --------------------------------------------------
# Где сохранять метаданные (int)
# 0 - Отключено
# 1 - В папке "Загрузки" (по умолчанию)
# 2 - Рядом с изображениями
metadataLocation = 1
# --------------------------------------------------
# Максимальное число одновременных загрузок (int)
# По умолчанию: 10
max_simultaneous_downloads = 10
# --------------------------------------------------
# Максимальное время ожидания загрузки (в секундах) (int)
# По умолчанию: 5
timeout = 5
# --------------------------------------------------

from subprocess import check_call, DEVNULL, STDOUT
from os import system, remove, rename, startfile
from re import search, split, sub
from pathlib import Path as path
from traceback import format_exc
from urllib import request
from sys import executable
from msvcrt import getch
from time import sleep
import threading
try:
    import requests
    from bs4 import BeautifulSoup as bs
except ModuleNotFoundError:
    while True:
        system('cls')
        print('Подожди, пока я устанавливаю необходимые библиотеки для работы скрипта...')
        requirements = ['requests', 'beautifulsoup4']
        try:
            for module in requirements:
                check_call([executable, "-m", "pip", "install", module], stdout=DEVNULL, stderr=STDOUT)
            import requests
            from bs4 import BeautifulSoup as bs
            system('cls')
            break
        except:
            print('\nНе удалось загрузить библиотеки. Убедитесь, что компьютер подключен к Интернету.')
            print('\nНажми любую клавишу, чтобы повторить попытку.')
            getch()
        


def getHTML():
    print('''
---===( Telegraph Image Downloader v1.2.1 от ARTEZON )===---

Чтобы скачать картинки из одной статьи,
скопируй ссылку и вставь её в это окно
(ПКМ или CTRL+V) и нажми Enter.
    
Чтобы скачать картинки с нескольких статей сразу,
скопируй и вставь ссылки в текстовый файл "Ссылки"
(каждая ссылка на новой строке, без знаков препинания).
После этого сохрани файл. Когда всё готово, нажми Enter.

[!] Ссылки должны начинаться с https://telegra.ph/... или https://teletype.in/...
''')
    htmlList = []
    while True:
        open("Ссылки.txt", 'a')
        inp = input()
        if inp:
            print('Проверяю ссылку...')
            urls = [inp]
        else:
            open("Ссылки.txt", 'a')
            print('Проверяю ссылки...')
            urls = [line.rstrip('\n') for line in open('Ссылки.txt')]
        i = 0
        if not urls:
            print('[Ошибка] Нет ссылок')
            print('Попробуй ещё раз.')
            continue
        while True:
            if not urls[i]: del urls[i]
            else: i += 1
            if i >= len(urls): break
        for url in urls:
            if 'https://' in url: pass
            elif 'http://' in url: url.replace('http://', 'https://', 1)
            else: url = 'https://' + url
            if 'telegra.ph/' not in url and 'teletype.in/' not in url:
                print('[Ошибка] Неверная ссылка:', url)
                print('Попробуй ещё раз.')
                break
            try:
                html = list(str(bs(request.urlopen(url).read(), features='html.parser')).split('\n'))
                htmlList.append([url, html])
            except:
                print('[Ошибка] Не удалось открыть URL:', url)
                print('[Ошибка] Нет подключения к Интернету, либо сайт не доступен, либо неверная ссылка.')
                print('Попробуй ещё раз.')
                break
        if len(htmlList) == len(urls): return htmlList

def validName(name):
    newchar = '_'
    if len(name) > 128: name = name[:127] + '…'
    name = str(name).replace('\\', newchar)
    name = str(name).replace('/', newchar)
    name = str(name).replace(':', newchar)
    name = str(name).replace('*', newchar)
    name = str(name).replace('?', newchar)
    name = str(name).replace('"', newchar)
    name = str(name).replace('<', newchar)
    name = str(name).replace('>', newchar)
    name = str(name).replace('|', newchar)
    name = name.strip(' ./\\')
    return name


def print_percent(last_percent=-1):
    global this_successful, this_failed, this_skipped, this_count
    global stop
    while not stop:
        percent = int((this_successful + this_skipped) / this_count * 100)
        if not stop and percent != 100:
            if this_failed == 0: print(f'     Скачивание... {percent}%', end='\r', flush=True)
            else: print(f'     Скачивание... {percent}% (есть ошибки)', end='\r', flush=True)
        last_percent = percent
        sleep(0.01)


def download(imgNumber, imgUrl):
    global folderName, imgs, successful, success, errorCode, failed, failedList, skipped, downloading
    global this_successful, this_failed, this_skipped, this_count
    try:
        downloading += 1
        extension = imgUrl.rsplit('.', 1)[-1]
        errorCountSeconds = 0
        timedOutError = False
        try:
            open(f'Загрузки\\{folderName}\\{imgNumber:03d}.{extension}')
            skipped += 1
            this_skipped += 1
            downloading -= 1
            # print(f'     Изображение {imgNumber} из {len(imgs)} пропущено: Файл "{imgNumber:03d}.{extension}" уже существует')
        except FileNotFoundError:
            while True:
                try:
                    imgData = requests.get(imgUrl, timeout=timeout)
                    errorCountSeconds = 0
                except:
                    if errorCountSeconds > 3:
                        timedOutError = True
                        break
                    # if errorCountSeconds == None:
                        # print(f'          [Ошибка] Не удаётся скачать файл "{imgNumber:03d}.{extension}", пробую ещё раз...')
                    sleep(0.5)
                    errorCountSeconds += 1
                    continue
                break
            if timedOutError:
                timedOutError = False
                errorCode = '"Неизвестная ошибка (время ожидания истекло). Попробуй включить VPN и запустить скрипт ещё раз"'
                success = False
            else:
                if imgData.status_code == 200:
                    if b'html' not in imgData.content:
                        open(f'Загрузки\\{folderName}\\{imgNumber:03d}.{extension}', 'wb').write(imgData.content)
                        success = True
                    else:
                        errorCode = '"Получен неверный тип файла от сервера"'
                        success = False
                else:
                    errorCode = imgData.status_code
                    success = False
            
            if success:
                # print(f'     Изображение {imgNumber} из {len(imgs)} загружено')
                successful += 1
                this_successful += 1
                downloading -= 1
            else:
                # print(f'     Изображение {imgNumber} из {len(imgs)} не загружено: Ошибка {errorCode}')
                failed += 1
                this_failed += 1
                failedList.append(imgUrl)
                downloading -= 1
    except: 
        failed += 1
        this_failed += 1
        failedList.append(imgUrl)
        downloading -= 1


def main():
    global folderName, imgs, successful, success, errorCode, failed, failedList, skipped, downloading
    global this_successful, this_failed, this_skipped, this_count
    global stop

    htmlList = getHTML()

    print('Скачиваю изображения...')

    successful = 0
    failed = 0
    skipped = 0
    downloading = 0

    htmlNumber = 0
    for data in htmlList:
        htmlNumber += 1

        this_successful = 0
        this_failed = 0
        this_skipped = 0


        url = data[0]
        html = data[1]

        title = ''
        description = ''

        imgs = []

        failedList = []

        if 'telegra.ph/' in url and url != 'https://telegra.ph/':
            for line in html:
                if '<article' in line:
                    title = search('<article class="tl_article_content" id="_tl_editor"><h1>(.*)<br/></h1>', line).group(1)
                    print(f'\nСтатья {htmlNumber} из {len(htmlList)}: {title}')
                    folderName = validName(title)
                    path('Загрузки/' + folderName).mkdir(parents=True, exist_ok=True)
                    description = search('</h1><address>(.*)<br/></address>', line).group(1)
                    description = sub('<[^>]+>', '', description)
                    data = split('<|>', line)
                    if metadataLocation == 1:
                        metadataPath = f'Загрузки\\{folderName}.txt'
                        try: remove(f'Загрузки\\{folderName} [ОШИБКА].txt')
                        except OSError: pass
                    elif metadataLocation == 2:
                        metadataPath = f'Загрузки\\{folderName}\\[Метаданные].txt'
                        try: remove(f'Загрузки\\{folderName}\\[Метаданные, ОШИБКА].txt')
                        except OSError: pass
                    else: metadataPath = False
                    for item in data:
                        if 'img src=' in item:
                            if 'img src="/' in item:
                                imgs.append('https://telegra.ph' + search('img src="(.*)"', item).group(1))
                            else:
                                imgs.append(search('img src="(.*)"', item).group(1))
                    break
            else:
                print('[Ошибка] Неизвестная ошибка.')
                return
        elif 'teletype.in/' in url:
            for line in html:
                if '<title>' in line:
                    try:
                        title = search('<title>(.*) — Teletype</title>', line).group(1)
                        description = ''
                        break
                    except:
                        print('[Ошибка] Неизвестная ошибка.')
                        return
            for line in html:
                if '<noscript><img' in line:
                    print(f'\nСтатья {htmlNumber} из {len(htmlList)}: {title}')
                    folderName = validName(title)
                    path('Загрузки/' + folderName).mkdir(parents=True, exist_ok=True)
                    data = split('<|>', line)
                    if metadataLocation == 1:
                        metadataPath = f'Загрузки\\{folderName}.txt'
                        try: remove(f'Загрузки\\{folderName} [ОШИБКА].txt')
                        except OSError: pass
                    elif metadataLocation == 2:
                        metadataPath = f'Загрузки\\{folderName}\\[Метаданные].txt'
                        try: remove(f'Загрузки\\{folderName}\\[Метаданные, ОШИБКА].txt')
                        except OSError: pass
                    else: metadataPath = False
                    for item in data:
                        if 'img' in item and 'src=' in item and 'version' not in item:
                            if 'src="/' in item:
                                if 'width' in item:
                                    imgs.append('https://teletype.in' + search('src="(.*)" width', item).group(1))
                                else:
                                    imgs.append('https://teletype.in' + search('src="(.*)"', item).group(1))
                            else:
                                if 'width' in item:
                                    imgs.append(search('src="(.*)" width', item).group(1))
                                else:
                                    imgs.append(search('src="(.*)"', item).group(1))
                    break
            else:
                print('[Ошибка] Неизвестная ошибка.')
                return
        else:
            print('[Ошибка] Неизвестная ошибка.')
            return

        try:
            if metadataPath:
                with open(metadataPath, 'w', encoding='UTF-8') as metadata:
                    metadata.write(f"""В данный момент выполняется скачивание изображений... 
Вы можете следить за процессом скачивания в окне командной строки.


Если программа уже завершена, а это сообщение остаётся прежним, значит программа была завершена некорректно: либо окно было преждевременно закрыто пользователем, либо произошёл критический сбой.

В первом случае просто запусти скрипт ещё раз, а во втором случае нужно отправить разработчику файл "error_log.txt", который находится в папке "Загрузки".""")
        except:
            print('[Ошибка] Неизвестная ошибка.')
            return

        this_count = len(imgs)
        stop = False
        threading.Thread(target=print_percent).start()

        imgNumber = 0
        for imgUrl in imgs:
            imgNumber += 1

            exec(f'img{imgNumber} = threading.Thread(target=download, args=(imgNumber, imgUrl,))')
            exec(f'img{imgNumber}.start()')
            while downloading >= max_simultaneous_downloads: sleep(0.1)

        for n in range(len(imgs)):
            exec(f'img{n + 1}.join()')

        stop = True
        # if this_failed == 0: print('     100%')
        # else: print(f'     {int((this_successful + this_skipped) / this_count * 100)}%')
        print(f'     Загружено {this_successful} изображений, ошибок: {this_failed}, пропущено: {this_skipped}')

        if metadataPath:
            with open(metadataPath, 'w', encoding='UTF-8') as metadata:
                metadata.write(f"""Скачано с помощью Telegram Image Downloader от ARTEZON

Источник: {url}

Название: {title}

Описание: {description}

Число изображений: {len(imgs)}""")

            if failedList:
                with open(metadataPath, 'a', encoding='UTF-8') as metadata:
                    metadata.write('\n\nСледующие изображения не были скачаны:')
                    for i in failedList:
                        metadata.write('\n' + str(i))
                    metadata.write('\nСкачай их вручную или попробуй запустить скрипт ещё раз.')
                if metadataLocation == 1: rename(f'Загрузки\\{folderName}.txt', f'Загрузки\\{folderName} [ОШИБКА].txt')
                elif metadataLocation == 2: rename(f'Загрузки\\{folderName}\\[Метаданные].txt', f'Загрузки\\{folderName}\\[Метаданные, ОШИБКА].txt')

    print(f'\nГотово! Всего загружено {successful} изображений, ошибок: {failed}, пропущено: {skipped}')


system('title Telegraph Image Downloader')
while True:
    try:
        system('cls')
        main()
        print('\nДля продолжения нажми любую клавишу.')
        getch()
    except:
        path('Загрузки').mkdir(exist_ok=True)
        open('Загрузки/error_log.txt', 'w').write(format_exc())
        print('Произошла непредвиденная ошибка. Отправь содержимое файла "Загрузки\\error_log.txt" разработчику.')
        startfile('Загрузки\\error_log.txt')
        getch()