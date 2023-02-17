# Telegraph Image Downloader
# Author: ARTEZON
# Github: https://github.com/ARTEZON
#
# Version 1.2.5
#
# --------------------------------------------------
# -= SETTINGS =-
# --------------------------------------------------
# Language (str) # not implemented
# language = 'ENG'
# --------------------------------------------------
# Metadata save location (int)
# 0 - OFF
# 1 - In "Downloads" folder (default)
# 2 - Next to images
metadataLocation = 1
# --------------------------------------------------
# Maximum simultaneous downloads (int)
# Default: 10
max_simultaneous_downloads = 10
# --------------------------------------------------
# Connection timeout (seconds) (int)
# Default: 10
timeout = 10
# --------------------------------------------------
# Maximum retries (seconds) (int)
# Default: 3
retry = 3
# --------------------------------------------------
# Proxy address (str)
# Default: None
proxy = None
# --------------------------------------------------


from subprocess import call, check_call, DEVNULL, STDOUT
from getpass import getpass as wait_for_enter_key
from sys import platform, executable
from pathlib import Path as path
from traceback import format_exc
from html import unescape
from time import sleep
import threading
import mimetypes
import re
import os

try:
    import requests
    from bs4 import BeautifulSoup as bs
except ModuleNotFoundError:
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Please wait while the necessary libraries are being installed...')
        requirements = ['requests', 'beautifulsoup4']
        try:
            for module_index, module in enumerate(requirements):
                print(f'Installing {module} ({module_index + 1} of {len(requirements)})...')
                check_call([executable, "-m", "pip", "install", module], stdout=DEVNULL, stderr=STDOUT)
            import requests
            from bs4 import BeautifulSoup as bs
            os.system('cls' if os.name == 'nt' else 'clear')
            break
        except:
            print('\nFailed to install the libraries. Make sure your PC is connected to the Internet and you have pip installed.')
            print('\nYou can also install the following packages manually:')
            for module in requirements:
                print(f'     {module}')
            print('\nPress Enter to try again.')
            wait_for_enter_key('')


def get_proxy_obj():
    return (
        {
           'http': proxy,
           'https': proxy,
        } if proxy else None
    )


def getHTML():
    print('''
---===( Telegraph Image Downloader v1.2.5 by ARTEZON )===---

To download pictures from one article,
copy the URL and paste it into this window
(right-click or CTRL+V) and press Enter.

To download images from several articles at once,
copy and paste the URLs into the "Links" file
(each link on a new line, no punctuation).
Then save the file. When everything is ready, press Enter.

[!] URLs must start with https://telegra.ph/... or https://teletype.in/...
''')
    htmlList = []
    while True:
        if not os.path.isfile("Links.txt"):
            try:
                open("Links.txt", 'a')
            except:
                print('[Error] Can\'t create the Links.txt file.\nCreate it manually and/or set permissions.\n')
                print('\nPress Enter to try again.')
                wait_for_enter_key('')
                continue
        inp = input()
        if inp:
            print('Checking the URL...')
            urls = [inp.strip()]
        else:
            if not os.path.isfile("Links.txt"):
                try:
                    open("Links.txt", 'a')
                except:
                    print('[Error] Can\'t create the Links.txt file.\nCreate it manually and/or set permissions.\n')
                    print('\nPress Enter to try again.')
                    wait_for_enter_key('')
                    continue
            print('Checking the URLs...')
            try:
                urls = [line.strip('\n').strip() for line in open('Links.txt', encoding='utf-8')]
            except UnicodeDecodeError:
                print('[Error] Can\'t read the Links.txt file because its encoding is not supported.')
                print('Please, save your file in Unicode (UTF-8) and try again.\n')
                print('\nPress Enter to try again.')
                wait_for_enter_key('')
                continue
            except:
                print('[Error] Can\'t open the Links.txt file.\nMake sure you have read permissions.\n')
                print('\nPress Enter to try again.')
                wait_for_enter_key('')
                continue
        i = 0
        if not urls:
            print('[Error] No URLs given')
            print('Please try again.\n')
            continue
        while True:
            if not urls[i]: del urls[i]
            else: i += 1
            if i >= len(urls): break
        for url in urls:
            url = re.sub('.*://', '', url, flags=re.IGNORECASE)
            url = 'https://' + url
            if 'telegra.ph/' not in url and 'teletype.in/' not in url:
                print('[Error] Invalid URL:', url)
                print('Please try again.\n')
                break
            try:
                html = list(str(bs(requests.get(url, proxies=get_proxy_obj()).content.decode(), features='html.parser')).split('\n'))
                htmlList.append([url, html])
            except Exception as e:
                print('[Error] Couldn\'t open this URL:', url)
                print('[Error] No Internet connection, the site is not available or the URL is invalid.')
                print('Please try again.\n')
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
            if this_failed == 0: print(f'     Downloading... {percent}%', end='\r', flush=True)
            else: print(f'     Downloading... {percent}% (error(s) occured)', end='\r', flush=True)
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
                errorCode = 'Connection failed or timed out. If source image site is blocked in your country, set proxy or enable VPN, and run the script again'
                success = False
                raise ValueError()
            extension = guessImageType(temp_imgData.content)
        
        retries = 0
        timedOutError = False
        try:
            open(f'Downloads/{folderName}/{imgNumber:03d}.{extension}')
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
                errorCode = 'Connection failed or timed out. If source image site is blocked in your country, set proxy or enable VPN, and run the script again'
                success = False
            else:
                if imgData.status_code == 200:
                    if b'html' not in imgData.content:
                        try:
                            open(f'Downloads/{folderName}/{imgNumber:03d}.{extension}', 'wb').write(imgData.content)
                        except Exception:
                            errorCode = 'Can\'t save image to \'{}\' file'.format(os.path.abspath(f'Downloads/{folderName}/{imgNumber:03d}.{extension}'))
                        success = True
                    else:
                        errorCode = 'Wrong file type has been received from the server'
                        success = False
                else:
                    errorCode = f'HTTP status code: {imgData.status_code}'
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

    print('Downloading images...')

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

        errorCode = 'Unknown error'
        failedList = []

        if 'telegra.ph/' in url and url != 'https://telegra.ph/':
            for line in html:
                if '<article' in line:
                    regex_title = re.search('<article class="tl_article_content" id="_tl_editor"><h1>(.*)<br/></h1>', line)
                    if isinstance(regex_title, re.Match):
                        title = unescape(regex_title.group(1))
                    else:
                        title = ""
                    print(f'\nArticle {htmlNumber} of {len(htmlList)}: {title}')
                    folderName = validName(title)
                    regex_description = re.search('</h1><address>(.*)<br/></address>', line)
                    if isinstance(regex_description, re.Match):
                        description = unescape(re.sub('<[^>]+>', '', regex_description.group(1)))
                    else:
                        description = ""
                    data = re.split('<|>', line)
                    if metadataLocation == 1:
                        metadataPath = f'Downloads/{folderName}.txt'
                        metadataPathError = f'Downloads/{folderName} [ERROR].txt'
                        if os.path.isfile(metadataPathError):
                            try: os.remove(metadataPathError)
                            except OSError: pass
                    elif metadataLocation == 2:
                        metadataPath = f'Downloads/{folderName}/[Metadata].txt'
                        metadataPathError = f'Downloads/{folderName}/[Metadata] [ERROR].txt'
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
                print(f'\nArticle {htmlNumber} of {len(htmlList)}: This article doesn\'t exist')
                print('     No images!')
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
                        print(f'\nArticle {htmlNumber} of {len(htmlList)}: This article doesn\'t exist')
                        print('     No images!')
                        break
            if teletype_article_found:
                for line in html:
                    if '<noscript><img' in line:
                        print(f'\nArticle {htmlNumber} of {len(htmlList)}: {title}')
                        folderName = validName(title)
                        data = re.split('<|>', line)
                        if metadataLocation == 1:
                            metadataPath = f'Downloads/{folderName}.txt'
                            metadataPathError = f'Downloads/{folderName} [ERROR].txt'
                            if os.path.isfile(metadataPathError):
                                try: os.remove(metadataPathError)
                                except OSError: pass
                        elif metadataLocation == 2:
                            metadataPath = f'Downloads/{folderName}/[Metadata].txt'
                            metadataPathError = f'Downloads/{folderName}/[Metadata] [ERROR].txt'
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
                    print(f'\nArticle {htmlNumber} of {len(htmlList)}: The article does not exist or does not contain images')
                    print('     No images!')
                    continue
        else:
            print(f'\nArticle {htmlNumber} of {len(htmlList)}: This link is not a valid article link')
            print('     No images!')
            continue

        if (len(imgs)) > 0:
            try:
                path('Downloads/' + folderName).mkdir(parents=True, exist_ok=True)
            except Exception:
                print('Can\'t create/open \'{}\' directory'.format(os.path.abspath('Downloads/' + folderName)))

            try:
                if metadataPath:
                    with open(metadataPath, 'w', encoding='utf-8') as metadata:
                        metadata.write(f"""The images are now being downloaded...
You can check download progress in the command line window.


If the program isn't running, but this message remains the same, then the program was not finished correctly: either the window was prematurely closed by user, or a critical error occurred.

In the first case, just run the script again. Otherwise, you should send the "error_log.txt" file, which is located in the "Downloads" folder, to the developer.""")
            except:
                print('[Error] Can\'t write metadata.')
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
            
            print(f'     {this_successful} images were downloaded, {this_failed} failed, {this_skipped} skipped.')

            try:
                if metadataPath:
                    with open(metadataPath, 'w', encoding='utf-8') as metadata:
                        metadata.write(f"""Downloaded using Telegraph Image Downloader by ARTEZON

Source: {url}

Title: {title}

Description: {description}

Number of images: {len(imgs)}""")
            except:
                print('[Error] Can\'t write metadata.')
                return

                if failedList:
                    print("     Last error: " + errorCode)
                    try:
                        if metadataPath:
                            with open(metadataPath, 'a', encoding='utf-8') as metadata:
                                metadata.write('\n\nThe following images have not been downloaded:')
                                for i in failedList:
                                    metadata.write('\n' + str(i))
                                metadata.write('\nDownload them manually or try running the script again.')
                            os.rename(metadataPath, metadataPathError)
                    except:
                        print('[Error] Can\'t write metadata.')
                        return
        else:
            print('     No images!')

    print(f'\nAll done! Total {successful} images were downloaded, {failed} failed, {skipped} skipped.')


if platform == 'win32':
    os.system('title Telegraph Image Downloader')
    if os.getcwd().lower() == os.path.join('C:', os.sep, 'Windows', 'system32').lower():
        print('Please run the program from another directory.')
        print('\nPress Enter to exit.')
        wait_for_enter_key('')
        os._exit(0)
while True:
    try:
        os.system('cls' if platform == 'win32' else 'clear')
        main()
        print('\nPress Enter to continue.')
        wait_for_enter_key('')
    except (KeyboardInterrupt, EOFError):
        print('\nProgram was terminated by user.')
        os._exit(0)
    except:
        path('Downloads').mkdir(exist_ok=True)
        open('Downloads/error_log.txt', 'w', encoding='utf-8').write(format_exc())
        if os.path.isfile('Downloads/error_log.txt'):
            if platform == 'win32':
                print('An unexpected error has occurred. Send the contents of the file "Downloads\\error_log.txt" to the developer.')
                os.startfile(os.path.abspath('Downloads/error_log.txt'))
            else:
                print('An unexpected error has occurred. Send the contents of the file "Downloads/error_log.txt" to the developer.')
                opener = 'open' if platform == 'darwin' else 'xdg-open'
                call([opener, 'Downloads/error_log.txt'])
        wait_for_enter_key('')