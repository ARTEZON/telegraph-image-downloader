from cx_Freeze import setup, Executable

version = open('version.txt').read()

setup(name='Telegraph Image Downloader',
    version = version,
    description = 'Download images from telegra.ph',
    author='ARTEZON',
    options = {'build_exe': {
        'packages': ['queue'],
        'excludes': [],
        'zip_include_packages': '*',
        'zip_exclude_packages': '',
        'build_exe': f'Telegraph Image Downloader/TGIDownloader_v{version}_EN'}},
    executables = [Executable('tmp/TGIDownloader_EN_build.py', base='console', target_name = 'TGIDownloader_EN', icon='icon.ico')])

setup(name='Telegraph Image Downloader',
    version = version,
    description = 'Скачивание изображений с telegra.ph',
    author='ARTEZON',
    options = {'build_exe': {
        'packages': ['queue'],
        'excludes': [],
        'zip_include_packages': '*',
        'zip_exclude_packages': '',
        'build_exe': f'Telegraph Image Downloader/TGIDownloader_v{version}_RU'}},
    executables = [Executable('tmp/TGIDownloader_RU_build.py', base='console', target_name = 'TGIDownloader_RU', icon='icon.ico')])