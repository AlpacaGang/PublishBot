from git import Repo
from telegram import ParseMode, Bot
from telegram.utils.helpers import escape_markdown

from datetime import datetime, timezone, timedelta

os.environ['TZ'] = 'Europe/Moscow'
TZ = timezone(timedelta(hours=3))
TIMESTAMP = datetime.now(TZ)
CHAT_ID = -1001235981203  

FILENAME = f'../lineage-17.1-{TIMESTAMP.strftime("%Y%m%d")}-UNOFFICIAL-platina.zip'
SIGNED_FILENAME =  f'../lineage-17.1-{TIMESTAMP.strftime("%Y%m%d")}-UNOFFICIAL-platina-signed.zip'

bot = Bot(os.environ.get('TOKEN'))

bot.send_message(chat_id = CHAT_ID,
                 text = f'⚙️ Build started:\n'
                 parse_mode = ParseMode.MARKDOWN_V2, disable_web_page_preview = True) # TODO: print commits, aka dt commit, common td commit, kernel tree commit, etc

os.system(f'repo sync')

def update_tree(s):
    os.chdir(s)
    os.system(f'git fetch --all')
    os.system(f'git reset --hard origin/staging')
    os.chdir('../../../')

update_tree('device/xiaomi/platina')
update_tree('device/xiaomi/sdm660-common')
update_tree('vendor/xiaomi/platina')
update_tree('vendor/xiaomi/sdm660-common')
update_tree('kernel/xiaomi/platina')

os.system(f'breakfast platina')
if not os.system(f'mka target-files-package otatools'):
    os.system(f'./build/tools/releasetools/sign_target_files_apks -o -d ~/.android-certs $OUT/obj/PACKAGING/target_files_intermediates/*-target_files-*.zip signed-target_files.zip')
    os.system(f'./build/tools/releasetools/ota_from_target_files -k ~/.android-certs/releasekey --block --backup=true signed-target_files.zip {SIGNED_FILNAME}') 
    # TODO: uploading zip to channel
    # TODO: md5
else:
    build_time = datetime.fromtimestamp(0, tz = TZ) + (datetime.now(TZ) - TIMESTAMP)
    bot.send_message(chat_id = CHAT_ID,
                     text=f'❌ Build failed in a {build_time.strftime("%-M mins %-S secs")}!')

# TODO: messages that sync started, signing zip 
