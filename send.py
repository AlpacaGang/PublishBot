import glob
import os

from telegram import Bot, ParseMode

bot = Bot(os.environ.get('token'))
if os.environ.get('TRAVIS_TEST_RESULT') == 0:
    bot.send_message(chat_id=-1001115967921,
                     text=f'✅ Build <a href="{os.environ.get("TRAVIS_BUILD_WEB_URL")}">'
                          f'#{os.environ.get("TRAVIS_BUILD_NUMBER")}</a> succeed!',
                     parse_mode=ParseMode.HTML)
    bot.send_document(chat_id=-1001115967921, document=open(glob.glob('HMP-kernel-*.zip')[0], 'rb'))
else:
    bot.send_message(chat_id=-1001115967921,
                     text=f'❌ Build <a href="{os.environ.get("TRAVIS_BUILD_WEB_URL")}">'
                          f'#{os.environ.get("TRAVIS_BUILD_NUMBER")}</a> failed!',
                     parse_mode=ParseMode.HTML)
