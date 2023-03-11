import os, sys, shutil, subprocess

def get_path(root_dir: str, version: str, lang: str) -> str:
    return f'{root_dir}/TGIDownloader_v{version}_{lang}'

def get_name(lang: str, what: str) -> str:
    if what == 'links':
        if lang == 'EN': return '/Links.txt'
        if lang == 'RU': return '/Ссылки.txt'
    if what == 'downloads':
        if lang == 'EN': return '/Downloads'
        if lang == 'RU': return '/Загрузки'

def make_build_script(input_script: str) -> str:
    input_strings = input_script.split('\n')
    while '# remove-from-build BEGIN' in input_strings:
        remove_begin = input_strings.index('# remove-from-build BEGIN')
        remove_end = input_strings.index('# remove-from-build END')
        input_strings = input_strings[:remove_begin] + input_strings[(remove_end + 1):]
    while '# add-to-build BEGIN' in input_strings:
        add_begin = input_strings.index('# add-to-build BEGIN')
        add_end = input_strings.index('# add-to-build END')
        if add_end - add_begin > 1:
            for i in range(add_begin + 1, add_end):
                if input_strings[i].startswith('# '):
                    input_strings[i] = input_strings[i][2:]
        del input_strings[add_begin]
        del input_strings[add_end - 1]
    return '\n'.join(input_strings)


root_dir = 'Telegraph Image Downloader'
version = open('version.txt').read()
languages = ['EN', 'RU']

os.makedirs('tmp', exist_ok=True)

for lang in languages:
    open(f'tmp/TGIDownloader_{lang}_build.py', 'w', encoding='utf-8').write(make_build_script(open(f'../TGIDownloader_{lang}.py', encoding='utf-8').read()))

subprocess.run([sys.executable, "build.py", "build"], check=True)

for lang in languages:
    print(f'\nProcessing {get_path(root_dir, version, lang)}...')

    license_path = get_path(root_dir, version, lang) + '/frozen_application_license.txt'
    if os.path.isfile(license_path):
        os.remove(license_path)
    os.makedirs(get_path(root_dir, version, lang) + get_name(lang, 'downloads'))
    open(get_path(root_dir, version, lang) + get_name(lang, 'links'), 'w')
    shutil.make_archive(f'{root_dir}/TGIDownloader_v{version}_exe_{lang}', 'zip', root_dir, f'TGIDownloader_v{version}_{lang}')

    os.makedirs('tmp/' + get_path(root_dir, version, lang) + get_name(lang, 'downloads'))
    open('tmp/' + get_path(root_dir, version, lang) + get_name(lang, 'links'), 'w')
    shutil.copy2(f'../TGIDownloader_{lang}.py', 'tmp/' + get_path(root_dir, version, lang) + f'/TGIDownloader_{lang}.py')
    shutil.make_archive(f'{root_dir}/TGIDownloader_v{version}_python_{lang}', 'zip', 'tmp/' + root_dir, f'TGIDownloader_v{version}_{lang}')

    print(f'Finished processing {get_path(root_dir, version, lang)}')
shutil.rmtree('tmp')

os.system('pause')