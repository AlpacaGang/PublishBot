import glob
import os
import sys
import time

from telegram import Bot, ParseMode

bot = Bot(os.environ.get('token'))
chat_id = int(os.environ.get('chat_id'))
product_filename = os.environ.get('product_filename')
if '--before' in sys.argv:
    bot.send_message(chat_id=chat_id,
                     text=f'⚙️ Build <a href="{os.environ.get("TRAVIS_BUILD_WEB_URL")}">'
                          f'#{os.environ.get("TRAVIS_BUILD_NUMBER")}</a> started...',
                     parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    open('/home/travis/time', 'w').write(str(round(time.time())))
elif '--after' in sys.argv:
    build_time = time.time() - int(open('/home/travis/time', 'r').read())
    m, s = divmod(build_time, 60)
    h, m = divmod(m, 60)
    build_time_str = f'{s} sec'
    if m > 0:
        build_time_str = f'{m} min' + build_time_str
        if h > 0:
            build_time_str = f'{h} hrs ' + build_time_str

    if os.environ.get('TRAVIS_TEST_RESULT') == '0':
        bot.send_message(chat_id=chat_id,
                         text=f'✅ Build <a href="{os.environ.get("TRAVIS_BUILD_WEB_URL")}">'
                              f'#{os.environ.get("TRAVIS_BUILD_NUMBER")}</a> succeed in a {build_time_str}!',
                         parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        bot.send_document(chat_id=chat_id, document=open(glob.glob(product_filename)[0], 'rb'))
    else:
        bot.send_message(chat_id=chat_id,
                         text=f'❌ Build <a href="{os.environ.get("TRAVIS_BUILD_WEB_URL")}">'
                              f'#{os.environ.get("TRAVIS_BUILD_NUMBER")}</a> failed in a {build_time_str}!',
                         parse_mode=ParseMode.HTML, disable_web_page_preview=True)
