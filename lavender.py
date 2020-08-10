import os

from telethon.sync import TelegramClient

os.environ['KBUILD_BUILD_USER'] = 'fedshat'
os.environ['KBUILD_BUILD_HOST'] = 'fedshatci'
os.environ['TZ'] = 'Europe/Moscow'
os.environ['KERNEL_USE_CCACHE'] = '1'
CHAT_ID = -1001222275544

bot = TelegramClient('bot', int(os.environ['API_ID']), os.environ['API_HASH']).start(
    bot_token=os.environ['TOKEN'])

if not os.system('bash -c "source build/envsetup.sh; lunch lineage_lavender-userdebug; mka bootimage"'):
    print('========== Build succeed ==========')
    FILENAME = 'out/target/product/lavender/boot.img'
    bot.send_file(CHAT_ID, FILENAME)
