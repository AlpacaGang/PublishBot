import os

from telegram import Bot

os.environ['KBUILD_BUILD_USER'] = 'fedshat'
os.environ['KBUILD_BUILD_HOST'] = 'fedshatci'
os.environ['TZ'] = 'Europe/Moscow'
os.environ['KERNEL_USE_CCACHE'] = '1'
CHAT_ID = -1001222275544
bot = Bot(os.environ.get('TOKEN'))

if not os.system('bash -c "source build/envsetup.sh; lunch lineage_lavender-userdebug; mka bootimage"'):
    print('========== Build succeed ==========')
    FILENAME = 'out/target/product/lavender/boot.img'
    bot.send_document(chat_id=CHAT_ID, document=open(FILENAME, 'rb'))
