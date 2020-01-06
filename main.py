import glob
import os
import sys

from telegram import Bot, ParseMode

bot = Bot(os.environ.get('token'))
chat_id = int(os.environ.get('chat_id'))
product_filename = os.environ.get('product_filename')
if '--before' in sys.argv:
    bot.send_message(chat_id=chat_id,
                     text=f'⚙️ Build <a href="{os.environ.get("TRAVIS_BUILD_WEB_URL")}">'
                          f'#{os.environ.get("TRAVIS_BUILD_NUMBER")}</a> started...',
                     parse_mode=ParseMode.HTML)
elif '--after' in sys.argv:
    if os.environ.get('TRAVIS_TEST_RESULT') == 0:
        bot.send_message(chat_id=chat_id,
                         text=f'✅ Build <a href="{os.environ.get("TRAVIS_BUILD_WEB_URL")}">'
                              f'#{os.environ.get("TRAVIS_BUILD_NUMBER")}</a> succeed!',
                         parse_mode=ParseMode.HTML)
        bot.send_document(chat_id=chat_id, document=open(glob.glob(product_filename)[0], 'rb'))
    else:
        bot.send_message(chat_id=chat_id,
                         text=f'❌ Build <a href="{os.environ.get("TRAVIS_BUILD_WEB_URL")}">'
                              f'#{os.environ.get("TRAVIS_BUILD_NUMBER")}</a> failed!',
                         parse_mode=ParseMode.HTML)
