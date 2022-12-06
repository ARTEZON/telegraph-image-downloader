# Telegraph Image Downloader
# Author: ARTEZON
# Github: https://github.com/ARTEZON
#
# Version 1.2.2
#
# --------------------------------------------------
# -= SETTINGS =-
# --------------------------------------------------
# Language (string)
# Possible options: ENG, RUS, JPN, CHN, KOR and others
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
# Maximum download timeout (seconds) (int)
# Default: 5
timeout = 5
# --------------------------------------------------

from subprocess import check_call, DEVNULL, STDOUT
from os import system, remove, rename, startfile, _exit
from re import search, split, sub
from pathlib import Path as path
from traceback import format_exc
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
        print('Please wait while the necessary libraries are installing...')
        requirements = ['requests', 'beautifulsoup4']
        try:
            for module in requirements:
                check_call([executable, "-m", "pip", "install", module], stdout=DEVNULL, stderr=STDOUT)
            import requests
            from bs4 import BeautifulSoup as bs
            system('cls')
            break
        except:
            print('\nFailed to install the libraries. Make sure your PC is connected to the Internet.')
            print('\nPress any key to try again.')
            getch()
        


def getHTML():
    print('''
---===( Telegraph Image Downloader v1.2.2 by ARTEZON )===---

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
        open("Links.txt", 'a')
        inp = input()
        if inp:
            print('Checking the URL...')
            urls = [inp]
        else:
            open("Links.txt", 'a')
            print('Checking the URLs...')
            urls = [line.rstrip('\n') for line in open('Links.txt', encoding='UTF-8')]
        i = 0
        if not urls:
            print('[Error] No URLs given')
            print('Please try again.')
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
                print('[Error] Invalid URL:', url)
                print('Please try again.')
                break
            try:
                html = list(str(bs(requests.get(url).text, features='html.parser')).split('\n'))
                htmlList.append([url, html])
            except:
                print('[Error] Couldn\'t open this URL:', url)
                print('[Error] No Internet connection, the site is not available or the URL is invalid.')
                print('Please try again.')
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
        percent = int((this_successful + this_skipped) / this_count * 100) if this_count != 0 else 100
        if not stop and percent != 100:
            if this_failed == 0: print(f'     Downloading... {percent}%', end='\r', flush=True)
            else: print(f'     Downloading... {percent}% (error(s) occured)', end='\r', flush=True)
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
            open(f'Downloads\\{folderName}\\{imgNumber:03d}.{extension}')
            skipped += 1
            this_skipped += 1
            downloading -= 1

        except FileNotFoundError:
            while True:
                try:
                    imgData = requests.get(imgUrl, timeout=timeout)
                    errorCountSeconds = 0
                except:
                    if errorCountSeconds > 3:
                        timedOutError = True
                        break
                    
                    
                    sleep(0.5)
                    errorCountSeconds += 1
                    continue
                break
            if timedOutError:
                timedOutError = False
                errorCode = '"Unknown error (Timed out). Please try to enable VPN and run the script again"'
                success = False
            else:
                if imgData.status_code == 200:
                    if b'html' not in imgData.content:
                        open(f'Downloads\\{folderName}\\{imgNumber:03d}.{extension}', 'wb').write(imgData.content)
                        success = True
                    else:
                        errorCode = '"Wrong file type has been received from the server"'
                        success = False
                else:
                    errorCode = imgData.status_code
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

        failedList = []

        if 'telegra.ph/' in url and url != 'https://telegra.ph/':
            for line in html:
                if '<article' in line:
                    title = search('<article class="tl_article_content" id="_tl_editor"><h1>(.*)<br/></h1>', line).group(1)
                    print(f'\nArticle {htmlNumber} of {len(htmlList)}: {title}')
                    folderName = validName(title)
                    path('Downloads/' + folderName).mkdir(parents=True, exist_ok=True)
                    description = search('</h1><address>(.*)<br/></address>', line).group(1)
                    description = sub('<[^>]+>', '', description)
                    data = split('<|>', line)
                    if metadataLocation == 1:
                        metadataPath = f'Downloads\\{folderName}.txt'
                        try: remove(f'Downloads\\{folderName} [ERROR].txt')
                        except OSError: pass
                    elif metadataLocation == 2:
                        metadataPath = f'Downloads\\{folderName}\\[Metadata].txt'
                        try: remove(f'Downloads\\{folderName}\\[Metadata, ERROR].txt')
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
                print('[Error] Unknown error.')
                return
        elif 'teletype.in/' in url:
            for line in html:
                if '<title>' in line:
                    try:
                        title = search('<title>(.*) — Teletype</title>', line).group(1)
                        description = ''
                        break
                    except:
                        print('[Error] Unknown error.')
                        return
            for line in html:
                if '<noscript><img' in line:
                    print(f'\nArticle {htmlNumber} of {len(htmlList)}: {title}')
                    folderName = validName(title)
                    path('Downloads/' + folderName).mkdir(parents=True, exist_ok=True)
                    data = split('<|>', line)
                    if metadataLocation == 1:
                        metadataPath = f'Downloads\\{folderName}.txt'
                        try: remove(f'Downloads\\{folderName} [ERROR].txt')
                        except OSError: pass
                    elif metadataLocation == 2:
                        metadataPath = f'Downloads\\{folderName}\\[Metadata].txt'
                        try: remove(f'Downloads\\{folderName}\\[Metadata, ERROR].txt')
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
                print('[Error] Unknown error.')
                return
        else:
            print('[Error] Unknown error.')
            return

        try:
            if metadataPath:
                with open(metadataPath, 'w', encoding='UTF-8') as metadata:
                    metadata.write(f"""Images are currently downloading...
You can check the download progress in the command line window.


If the program isn't running, but this message remains the same, then the program was not finished correctly: either the window was prematurely closed by user, or a critical error occurred.

In the first case, just run the script again. Otherwise, you should send the "error_log.txt" file, which is located in the "Downloads" folder, to the developer.""")
        except:
            print('[Error] Unknown error.')
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
        
        
        print(f'     {this_successful} images were downloaded, {this_failed} failed, {this_skipped} skipped.')

        if metadataPath:
            with open(metadataPath, 'w', encoding='UTF-8') as metadata:
                metadata.write(f"""Downloaded using Telegraph Image Downloader by ARTEZON

Source: {url}

Title: {title}

Description: {description}

Number of images: {len(imgs)}""")

            if failedList:
                with open(metadataPath, 'a', encoding='UTF-8') as metadata:
                    metadata.write('\n\nThe following images have not been downloaded:')
                    for i in failedList:
                        metadata.write('\n' + str(i))
                    metadata.write('\nDownload them manually or try running the script again.')
                if metadataLocation == 1: rename(f'Downloads\\{folderName}.txt', f'Downloads\\{folderName} [ERROR].txt')
                elif metadataLocation == 2: rename(f'Downloads\\{folderName}\\[Metadata].txt', f'Downloads\\{folderName}\\[Metadata, ERROR].txt')

    print(f'\nAll done! Total {successful} images were downloaded, {failed} failed, {skipped} skipped.')


system('title Telegraph Image Downloader')
while True:
    try:
        system('cls')
        main()
        print('\nPress any key to continue.')
        getch()
    except KeyboardInterrupt:
        print('Program was terminated by user.')
        _exit(0)
    except:
        path('Downloads').mkdir(exist_ok=True)
        open('Downloads/error_log.txt', 'w', encoding='UTF-8').write(format_exc())
        print('An unexpected error has occurred. Send the contents of the file "Downloads\\error_log.txt" to the developer.')
        startfile('Downloads\\error_log.txt')
        getch()