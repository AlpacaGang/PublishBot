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
                     text=f'⚙️ Local build for platina started...',
                     parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    open('/home/fedshat/time', 'w').write(str(round(time.time())))
elif '--after' in sys.argv:
    build_time = int(time.time()) - int(open('/home/fedshat/time', 'r').read())
    m, s = divmod(build_time, 60)
    h, m = divmod(m, 60)
    build_time_str = f'{s} sec'
    if m > 0:
        build_time_str = f'{m} min ' + build_time_str
        if h > 0:
            build_time_str = f'{h} hrs ' + build_time_str

    files_found = glob.glob(product_filename)

    if len(files_found) > 0:
        bot.send_message(chat_id=chat_id,
                         text=f'✅ Local build for platina succeed in a {build_time_str}!',
                         parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        bot.send_document(chat_id=chat_id, document=open(files_found[0], 'rb'))
    else:
        bot.send_message(chat_id=chat_id,
                         text=f'❌ Local build for platina failed in a {build_time_str}!',
                         parse_mode=ParseMode.HTML, disable_web_page_preview=True)
