import hashlib
import os
import sys
from datetime import datetime
from glob import glob
from os.path import join
from time import time

from git import Repo
from telegram.utils.helpers import escape_markdown
from telethon.sync import TelegramClient
from telethon.tl.custom import Message

os.environ['TZ'] = 'Europe/Moscow'
start_time = time()
TIMESTAMP = datetime.now()
CHAT_ID = -1001235981203
DEVICE = 'platina'

if '-i' in sys.argv:
    os.system('repo init -u git://github.com/LineageOS/android.git -b lineage-17.1')
    os.system('git clone https://github.com/PlatinaDevsSDM660/android_device_xiaomi_sdm660-common'
              '-b lineage-17.x device/xiaomi/sdm660-common')
    os.system('git clone https: // github.com/PlatinaDevsSDM660/android_device_xiaomi_platina'
              '-b lineage-17.x device/xiaomi/platina')
    os.system('git clone https://github.com/PlatinaDevsSDM660/android_device_xiaomi_sdm660-common'
              '-b lineage-17.x vendor/xiaomi/sdm660-common')
    os.system(
        'git clone https://gitlab.com/sdm660-platina/vendor_xiaomi_platina vendor/xiaomi/platina')
    os.system(
        'git clone https://github.com/FedorShatokhin2005/msm-4.4 kernel/xiaomi/platina')
    os.system('git clone https://github.com/arter97/arm64-gcc.git compiler')

tree_dir = os.getcwd()

FILENAME = join(
    tree_dir, f'../lineage-17.1-{TIMESTAMP.strftime("%Y%m%d-%H%M")}-UNOFFICIAL-platina-unsigned.zip')
SIGNED_FILENAME = join(
    tree_dir, f'../lineage-17.1-{TIMESTAMP.strftime("%Y%m%d-%H%M")}-UNOFFICIAL-platina.zip')

bot = TelegramClient('bot', int(os.environ['API_ID']), os.environ['API_HASH']).start(
    bot_token=os.environ['TOKEN'])


def update_and_get_tree(s, branch):
    os.chdir(s)
    os.system('git fetch --all')
    os.system('git reset --hard ' + branch)
    repo = Repo('.')

    commit_msg = escape_markdown(
        repo.active_branch.commit.message.split("\n")[0])
    res = f'`{repo.active_branch.name}:' \
          f'`{repo.active_branch.commit.hexsha[:7]}\n' \
          f'`{commit_msg}`'
    os.chdir(tree_dir)
    return res


bot.send_message(CHAT_ID, '⚙️ Build started...\n')
bot.send_message(CHAT_ID, '⚙️ Syncing main tree...\n')
os.system('repo sync --force-sync')

bot.send_message(CHAT_ID, '⚙️ Syncing device trees...\n')
bot.send_message(CHAT_ID, f'⚙️ **Device tree commit:** {update_and_get_tree("device/xiaomi/platina", "origin/lineage-17.x")}\n'  # pylint: disable=line-too-long
                 f'  **Common device tree commit:** '
                 f'{update_and_get_tree("device/xiaomi/sdm660-common", "origin/lineage-17.x")}\n'
                 f'  **Vendor tree commit:** {update_and_get_tree("vendor/xiaomi/platina", "origin/master")}\n'
                 f'  **Common vendor tree commit:** '
                 f'{update_and_get_tree("vendor/xiaomi/sdm660-common", "origin/lineage-17.x")}\n'
                 f'  **Kernel commit:** '
                 f'{update_and_get_tree("kernel/xiaomi/platina", "origin/kernel.lnx.4.4.r38-rel")}')

update_and_get_tree('compiler', '811a3bc6b40ad924cd1a24a481b6ac5d9227ff7e')


def lineage_exec(cmd):
    return os.system(f'bash -c "source build/envsetup.sh; breakfast {DEVICE}; ' + cmd.replace('"', '\\"') + '"')


bot.send_message(CHAT_ID, '⚙️ Building...\n')
if not lineage_exec('mka bacon'):
    # bot.send_message(CHAT_ID, '⚙️ Signing...\n')
    # target_files = glob(f'out/target/product/{DEVICE}/obj/PACKAGING/'
    #                     f'target_files_intermediates/*-target_files-*.zip')[0]
    # lineage_exec(
    #     './build/tools/releasetools/sign_target_files_apks -o -d '
    #     f'~/.android-certs {target_files} signed-target_files.zip;'
    #
    #     './build/tools/releasetools/ota_from_target_files -k ~/.android-certs/releasekey '
    #     '--block --backup=true signed-target_files.zip ' + SIGNED_FILENAME)
    build = glob(
        f'out/target/product/{DEVICE}/lineage-17.1-{TIMESTAMP.strftime("%Y%m%d")}-UNOFFICIAL-{DEVICE}.zip')[0]
    os.rename(build, FILENAME)
    delta = int(time() - start_time)
    build_time = f'{delta // 60 // 60} hours {delta // 60 % 60} minutes {delta % 60} seconds'
    bot.send_message(CHAT_ID, f'✅ Build succeed in a {build_time}!')
    uploading_msg: Message = bot.send_message(
        CHAT_ID, '⚙ Uploading, please wait...')
    msg: Message = bot.send_file(
        CHAT_ID, FILENAME, caption='MD5: `Loading...`', parse_mode='md')
    uploading_msg.delete()
    file_hash = hashlib.md5()
    with open(FILENAME, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            file_hash.update(chunk)
    msg.edit(f'MD5: `{file_hash.hexdigest()}`', parse_mode='md')
else:
    delta = int(time() - start_time)
    build_time = f'{delta // 60 // 60} hours {delta // 60 % 60} minutes {delta % 60} seconds'
    bot.send_message(CHAT_ID, f'❌ Build failed in a {build_time}!')
