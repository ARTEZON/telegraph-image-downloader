# Telegraph Image Downloader
# Автор: ARTEZON
# Github: https://github.com/ARTEZON
#
# Версия 1.2.5
#
# --------------------------------------------------
# -= НАСТРОЙКИ =-
# --------------------------------------------------
# Язык (str) # не реализовано
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
# Время ожидания подключения (в секундах) (int)
# По умолчанию: 10
timeout = 10
# --------------------------------------------------
# Максимальное число повторных попыток (в секундах) (int)
# По умолчанию: 3
retry = 3
# --------------------------------------------------
# Адрес прокси-сервера (str)
# По умолчанию: None
proxy = None
# --------------------------------------------------


from getpass import getpass as wait_for_enter_key
from sys import platform, executable
from pathlib import Path as path
from traceback import format_exc
from subprocess import run
from html import unescape
from time import sleep
import threading
import mimetypes
import re
import os

# remove-from-build BEGIN
try:
    import requests
    from bs4 import BeautifulSoup as bs
except ModuleNotFoundError:
    from subprocess import DEVNULL, STDOUT
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Пожалуйста, подождите, пока устанавливаются необходимые библиотеки для работы скрипта...')
        requirements = ['requests', 'beautifulsoup4']
        try:
            for module_index, module in enumerate(requirements):
                print(f'Установка {module} ({module_index + 1} of {len(requirements)})...')
                run([executable, "-m", "pip", "install", module], check=True, stdout=DEVNULL, stderr=STDOUT)
            import requests
            from bs4 import BeautifulSoup as bs
            os.system('cls' if os.name == 'nt' else 'clear')
            break
        except:
            print('\nНе удалось загрузить библиотеки. Убедитесь, что компьютер подключен к Интернету и модуль pip установлен.')
            print('\nВы также можете вручную установить следующие пакеты:')
            for module in requirements:
                print(f'     {module}')
            print('\nНажмите Enter, чтобы повторить попытку.')
            wait_for_enter_key('')
# remove-from-build END
# add-to-build BEGIN
# import requests
# from bs4 import BeautifulSoup as bs
# add-to-build END


def get_proxy_obj():
    return (
        {
           'http': proxy,
           'https': proxy,
        } if proxy else None
    )


def getHTML():
    print('''
---===( Telegraph Image Downloader v1.2.5 от ARTEZON )===---

Чтобы скачать картинки из одной статьи,
скопируйте ссылку, вставьте её в это окно
(ПКМ или CTRL+V) и нажмите Enter.

Чтобы скачать картинки с нескольких статей сразу,
скопируйте и вставьте ссылки в текстовый файл "Ссылки"
(каждая ссылка на новой строке, без знаков препинания).
После этого сохраните файл. Когда всё готово, нажмите Enter.

[!] Ссылки должны начинаться с https://telegra.ph/... или https://teletype.in/...
''')
    htmlList = []
    while True:
        if not os.path.isfile("Ссылки.txt"):
            try:
                open("Ссылки.txt", 'a')
            except:
                print('[Ошибка] Не удалось создать файл Ссылки.txt.\nСоздайте его вручную и/или настройте права доступа.\n')
                print('\nНажмите Enter, чтобы повторить попытку.')
                wait_for_enter_key('')
                continue
        inp = input()
        if inp:
            print('Проверяю ссылку...')
            urls = [inp.strip()]
        else:
            if not os.path.isfile("Ссылки.txt"):
                try:
                    open("Ссылки.txt", 'a')
                except:
                    print('[Ошибка] Не удалось создать файл Ссылки.txt.\nСоздайте его вручную и/или настройте права доступа.\n')
                    print('\nНажмите Enter, чтобы повторить попытку.')
                    wait_for_enter_key('')
                    continue
            print('Проверяю ссылки...')
            try:
                urls = [line.strip('\n').strip() for line in open('Ссылки.txt', encoding='utf-8')]
            except UnicodeDecodeError:
                print('[Ошибка] Не удалось прочитать файл Ссылки.txt, так как его кодировка не поддерживается.')
                print('Пожалуйста, сохраните файл в Unicode (UTF-8) и попробуйте снова.\n')
                print('\nНажмите Enter, чтобы повторить попытку.')
                wait_for_enter_key('')
                continue
            except:
                print('[Ошибка] Не удалось открыть файл Ссылки.txt.\nУбедитесь, что у вас есть права на его чтение.\n')
                print('\nНажмите Enter, чтобы повторить попытку.')
                wait_for_enter_key('')
                continue
        i = 0
        if not urls:
            print('[Ошибка] Нет ссылок')
            print('Попробуйте ещё раз.\n')
            continue
        while True:
            if not urls[i]: del urls[i]
            else: i += 1
            if i >= len(urls): break
        for url in urls:
            url = re.sub('.*://', '', url, flags=re.IGNORECASE)
            url = 'https://' + url
            if 'telegra.ph/' not in url and 'teletype.in/' not in url:
                print('[Ошибка] Неверная ссылка:', url)
                print('Попробуйте ещё раз.\n')
                break
            try:
                html = list(str(bs(requests.get(url, proxies=get_proxy_obj()).content.decode(), features='html.parser')).split('\n'))
                htmlList.append([url, html])
            except Exception as e:
                print('[Ошибка] Не удалось открыть URL:', url)
                print('[Ошибка] Нет подключения к Интернету, либо сайт не доступен, либо неверная ссылка.')
                print('Попробуйте ещё раз.\n')
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


def guessImageType(content):
    if content[6:10] in (b'JFIF', b'Exif'):
        return 'jpg'
    if content.startswith(b'\211PNG\r\n\032\n'):
        return 'png'
    if content[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'
    if content[:2] in (b'MM', b'II'):
        return 'tiff'
    if content.startswith(b'BM'):
        return 'bmp'
    if content.startswith(b'RIFF') and h[8:12] == b'WEBP':
        return 'webp'
    return 'unknown'


def printPercentage(last_percent=-1):
    global this_successful, this_failed, this_skipped, this_count
    global stop
    while not stop:
        percent = int((this_successful + this_skipped) / this_count * 100) if this_count != 0 else 100
        if not stop and percent != 100:
            if this_failed == 0: print(f'     Скачивание... {percent}%', end='\r', flush=True)
            else: print(f'     Скачивание... {percent}% (есть ошибки)', end='\r', flush=True)
        last_percent = percent
        sleep(0.01)


def download(imgNumber, imgUrl):
    global folderName, imgs, successful, success, failed, errorCode, failedList, skipped, downloading
    global this_successful, this_failed, this_skipped, this_count
    try:
        downloading += 1
        mimetype = mimetypes.guess_type(imgUrl)[0]
        
        retries = 0
        timedOutError = False
        
        temp_imgData = None
        if mimetype:
            extension = mimetypes.guess_extension(mimetype)[1::]
        else:
            while True:
                try:
                    temp_imgData = requests.get(imgUrl, timeout=timeout, proxies=get_proxy_obj())
                    retries = 0
                except Exception as e:
                    if retries > retry:
                        timedOutError = True
                        break
                    sleep(0.5)
                    retries += 1
                    continue
                break
            if timedOutError:
                timedOutError = False
                errorCode = 'Не удалось установить соединение или время на подключение истекло. Если сайт с исходным изображением заблокирован в вашей стране, настройте прокси или включите VPN, затем запустите скрипт ещё раз'
                success = False
                raise ValueError()
            extension = guessImageType(temp_imgData.content)
        
        retries = 0
        timedOutError = False
        try:
            open(f'Загрузки/{folderName}/{imgNumber:03d}.{extension}')
            skipped += 1
            this_skipped += 1
            downloading -= 1

        except FileNotFoundError:
            while True:
                try:
                    if not temp_imgData: imgData = requests.get(imgUrl, timeout=timeout, proxies=get_proxy_obj())
                    else: imgData = temp_imgData
                    retries = 0
                except:
                    if retries > retry:
                        timedOutError = True
                        break
                    sleep(0.5)
                    retries += 1
                    continue
                break
            if timedOutError:
                timedOutError = False
                errorCode = 'Не удалось установить соединение или время на подключение истекло. Если сайт с исходным изображением заблокирован в вашей стране, настройте прокси или включите VPN, затем запустите скрипт ещё раз'
                success = False
            else:
                if imgData.status_code == 200:
                    if b'html' not in imgData.content:
                        try:
                            open(f'Загрузки/{folderName}/{imgNumber:03d}.{extension}', 'wb').write(imgData.content)
                        except Exception:
                            errorCode = 'Can\'t save image to \'{}\' file'.format(os.path.abspath(f'Downloads/{folderName}/{imgNumber:03d}.{extension}'))
                        success = True
                    else:
                        errorCode = 'Получен неверный тип файла от сервера'
                        success = False
                else:
                    errorCode = f'Код состояния HTTP: {imgData.status_code}'
                    success = False
            
            if success:
                successful += 1
                this_successful += 1
                downloading -= 1
            else:
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

        errorCode = 'Неизвестная ошибка'
        failedList = []

        if 'telegra.ph/' in url and url != 'https://telegra.ph/':
            for line in html:
                if '<article' in line:
                    regex_title = re.search('<article class="tl_article_content" id="_tl_editor"><h1>(.*)<br/></h1>', line)
                    if isinstance(regex_title, re.Match):
                        title = unescape(regex_title.group(1))
                    else:
                        title = ""
                    print(f'\nСтатья {htmlNumber} из {len(htmlList)}: {title}')
                    folderNameFirst = validName(title)
                    folderNameCount = 0
                    folderName = folderNameFirst
                    while os.path.isdir(f'Загрузки/{folderName}'):
                        folderNameCount += 1
                        folderName = f'{folderNameFirst} ({folderNameCount})'
                    regex_description = re.search('</h1><address>(.*)<br/></address>', line)
                    if isinstance(regex_description, re.Match):
                        description = unescape(re.sub('<[^>]+>', '', regex_description.group(1)))
                    else:
                        description = ""
                    data = re.split('<|>', line)
                    if metadataLocation == 1:
                        metadataPath = f'Загрузки/{folderName}.txt'
                        metadataPathError = f'Загрузки/{folderName} [ОШИБКА].txt'
                        if os.path.isfile(metadataPathError):
                            try: os.remove(metadataPathError)
                            except OSError: pass
                    elif metadataLocation == 2:
                        metadataPath = f'Загрузки/{folderName}/[Метаданные].txt'
                        metadataPathError = f'Загрузки/{folderName}/[Метаданные] [ОШИБКА].txt'
                        if os.path.isfile(metadataPathError):
                            try: os.remove(metadataPathError)
                            except OSError: pass
                    else: metadataPath = None
                    for item in data:
                        if 'img src=' in item:
                            try:
                                if 'img src="/' in item:
                                    imgs.append('https://telegra.ph' + re.search('img src="(.*)"', item).group(1))
                                else:
                                    imgs.append(re.search('img src="(.*)"', item).group(1))
                            except Exception: pass
                    break
            else:
                print(f'\nСтатья {htmlNumber} из {len(htmlList)}: Эта статья не существует')
                print('     Нет изображений!')
                continue
        elif 'teletype.in/' in url:
            teletype_article_found = False
            for line in html:
                if '<title>' in line:
                    try:
                        regex_title = re.search('<title>(.*) — Teletype</title>', line)
                        if isinstance(regex_title, re.Match):
                            title = unescape(regex_title.group(1))
                        else:
                            title = ''
                        description = ''
                        teletype_article_found = True
                        break
                    except:
                        print(f'\nСтатья {htmlNumber} из {len(htmlList)}: Эта статья не существует')
                        print('     Нет изображений!')
                        break
            if teletype_article_found:
                for line in html:
                    if '<noscript><img' in line:
                        print(f'\nСтатья {htmlNumber} из {len(htmlList)}: {title}')
                        folderNameFirst = validName(title)
                        folderNameCount = 0
                        folderName = folderNameFirst
                        while os.path.isdir(folderName):
                            folderNameCount += 1
                            folderName = f'{folderNameFirst} ({folderNameCount})'
                        data = re.split('<|>', line)
                        if metadataLocation == 1:
                            metadataPath = f'Загрузки/{folderName}.txt'
                            metadataPathError = f'Загрузки/{folderName} [ОШИБКА].txt'
                            if os.path.isfile(metadataPathError):
                                try: os.remove(metadataPathError)
                                except OSError: pass
                        elif metadataLocation == 2:
                            metadataPath = f'Загрузки/{folderName}/[Метаданные].txt'
                            metadataPathError = f'Загрузки/{folderName}/[Метаданные] [ОШИБКА].txt'
                            if os.path.isfile(metadataPathError):
                                try: os.remove(metadataPathError)
                                except OSError: pass
                        else: metadataPath = None
                        for item in data:
                            if 'img' in item and 'src=' in item and 'version' not in item:
                                try:
                                    if 'src="/' in item:
                                        if 'width' in item:
                                            imgs.append('https://teletype.in' + re.search('src="(.*)" width', item).group(1))
                                        else:
                                            imgs.append('https://teletype.in' + re.search('src="(.*)"', item).group(1))
                                    else:
                                        if 'width' in item:
                                            imgs.append(re.search('src="(.*)" width', item).group(1))
                                        else:
                                            imgs.append(re.search('src="(.*)"', item).group(1))
                                except Exception: pass
                        break
                else:
                    print(f'\nСтатья {htmlNumber} из {len(htmlList)}: Статья не существует или не содержит изображений')
                    print('     Нет изображений!')
                    continue
        else:
            print(f'\nСтатья {htmlNumber} из {len(htmlList)}: Эта ссылка не является ссылкой на статью')
            print('     Нет изображений!')
            continue

        if (len(imgs)) > 0:
            try:
                path('Загрузки/' + folderName).mkdir(parents=True, exist_ok=True)
            except Exception:
                print('Не удалось создать/открыть папку \'{}\''.format(os.path.abspath('Загрузки/' + folderName)))

            try:
                if metadataPath:
                    with open(metadataPath, 'w', encoding='utf-8') as metadata:
                        metadata.write(f"""В данный момент выполняется скачивание изображений...
Вы можете следить за процессом скачивания в окне командной строки.


Если программа уже завершена, а это сообщение остаётся прежним, значит программа была завершена некорректно: либо окно было преждевременно закрыто пользователем, либо произошёл критический сбой.

В первом случае просто запусти скрипт ещё раз, а во втором случае нужно отправить разработчику файл "error_log.txt", который находится в папке "Загрузки".""")
            except:
                print('[Ошибка] Не удалось записать метаданные.')
                return

            this_count = len(imgs)
            stop = False
            threading.Thread(target=printPercentage).start()

            imgNumber = 0
            for imgUrl in imgs:
                imgNumber += 1
                exec(f'img{imgNumber} = threading.Thread(target=download, args=(imgNumber, imgUrl,))')
                exec(f'img{imgNumber}.start()')
                while downloading >= max_simultaneous_downloads: sleep(0.1)

            for n in range(len(imgs)):
                exec(f'img{n + 1}.join()')

            stop = True
            
            print(f'     Загружено {this_successful} изображений, ошибок: {this_failed}, пропущено: {this_skipped}')

            try:
                if metadataPath:
                    with open(metadataPath, 'w', encoding='utf-8') as metadata:
                        metadata.write(f"""Скачано с помощью Telegraph Image Downloader от ARTEZON

Источник: {url}

Название: {title}

Описание: {description}

Число изображений: {len(imgs)}""")
            except:
                print('[Ошибка] Не удалось записать метаданные.')
                return

                if failedList:
                    print("     Последняя ошибка: " + errorCode)
                    try:
                        if metadataPath:
                            with open(metadataPath, 'a', encoding='utf-8') as metadata:
                                metadata.write('\n\nСледующие изображения не были скачаны:')
                                for i in failedList:
                                    metadata.write('\n' + str(i))
                                metadata.write('\nСкачайте их вручную или попробуйте запустить скрипт ещё раз.')
                            os.rename(metadataPath, metadataPathError)
                    except:
                        print('[Ошибка] Не удалось записать метаданные.')
                        return
        else:
            print('     Нет изображений!')

    print(f'\nГотово! Всего загружено {successful} изображений, ошибок: {failed}, пропущено: {skipped}')


if platform == 'win32':
    os.system('title Telegraph Image Downloader')
    if os.getcwd().lower() == os.path.join('C:', os.sep, 'Windows', 'system32').lower():
        print('Пожалуйста, запустите программу из другой директории.')
        print('\nДля продолжения нажмите Enter.')
        wait_for_enter_key('')
        os._exit(0)
while True:
    try:
        os.system('cls' if platform == 'win32' else 'clear')
        main()
        print('\nДля продолжения нажмите Enter.')
        wait_for_enter_key('')
    except (KeyboardInterrupt, EOFError):
        print('\nПрограмма была завершена пользователем.')
        os._exit(0)
    except:
        path('Загрузки').mkdir(exist_ok=True)
        open('Загрузки/error_log.txt', 'w', encoding='utf-8').write(format_exc())
        if os.path.isfile('Загрузки/error_log.txt'):
            if platform == 'win32':
                print('Произошла непредвиденная ошибка. Отправьте содержимое файла "Загрузки\\error_log.txt" разработчику.')
                os.startfile(os.path.abspath('Загрузки/error_log.txt'))
            else:
                print('Произошла непредвиденная ошибка. Отправьте содержимое файла "Загрузки/error_log.txt" разработчику.')
                opener = 'open' if platform == 'darwin' else 'xdg-open'
                run([opener, 'Загрузки/error_log.txt'])
        wait_for_enter_key('')