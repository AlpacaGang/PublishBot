import os
from datetime import datetime, timezone, timedelta
from os.path import join

from telegram import ParseMode, Bot

os.environ['TZ'] = 'Europe/Moscow'
TZ = timezone(timedelta(hours=3))
TIMESTAMP = datetime.now(TZ)
CHAT_ID = -1001235981203

tree_dir = os.getcwd()

FILENAME = join(tree_dir, f'../lineage-17.1-{TIMESTAMP.strftime("%Y%m%d")}-UNOFFICIAL-platina.zip')
SIGNED_FILENAME = join(tree_dir, f'../lineage-17.1-{TIMESTAMP.strftime("%Y%m%d")}-UNOFFICIAL-platina-signed.zip')

bot = Bot(os.environ.get('TOKEN'))


def update_and_get_tree(s):
    os.chdir(s)
    os.system(f'git fetch --all')
    os.system(f'git reset --hard origin/staging')
    os.chdir(tree_dir)


update_and_get_tree('device/xiaomi/platina')
update_and_get_tree('device/xiaomi/sdm660-common')
update_and_get_tree('vendor/xiaomi/platina')
update_and_get_tree('vendor/xiaomi/sdm660-common')
update_and_get_tree('kernel/xiaomi/platina')

bot.send_message(chat_id=CHAT_ID,
                 text=f'⚙️ Build started:\n',
                 parse_mode=ParseMode.MARKDOWN_V2,
                 disable_web_page_preview=True)  # TODO: print commits, aka dt commit, common td commit, kernel tree commit, etc

os.system(f'repo sync')


def lineage_exec(cmd):
    return os.system('sh -c "source build/envsetup.sh; breakfast platina; ' + cmd.replace('"', '\\"') + '"')


if not lineage_exec('mka target-files-package otatools'):
    lineage_exec(
        './build/tools/releasetools/sign_target_files_apks -o -d '
        '~/.android-certs $OUT/obj/PACKAGING/target_files_intermediates/*-target_files-*.zip signed-target_files.zip;'
        
        './build/tools/releasetools/ota_from_target_files -k ~/.android-certs/releasekey '
        '--block --backup=true signed-target_files.zip ' + SIGNED_FILENAME)
    # TODO: uploading zip to channel
    # TODO: md5
else:
    build_time = datetime.fromtimestamp(0, tz=TZ) + (datetime.now(TZ) - TIMESTAMP)
    bot.send_message(chat_id=CHAT_ID,
                     text=f'❌ Build failed in a {build_time.strftime("%-M mins %-S secs")}!')

# TODO: messages that sync started, signing zip
