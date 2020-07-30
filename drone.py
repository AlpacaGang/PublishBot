import os
import sys

import simpletg as stg


def esc(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


CHAT_ID = os.getenv("CHAT_ID")
if not CHAT_ID.startswith("-100"):
    CHAT_ID = f"-100{CHAT_ID}"

OK = os.getenv("DRONE_BUILD_STATUS") == 'success'

bot = stg.TelegramAPI(token=os.getenv("BOT_TOKEN"))

DRONE_LINK = 'https://drone.vanutp.dev/'
BUILD_NUMBER = esc(os.getenv("DRONE_BUILD_NUMBER"))
BUILD_LINK = f'<a href="{esc(DRONE_LINK)}{esc(os.getenv("DRONE_REPO"))}/{BUILD_NUMBER}">#{BUILD_NUMBER}</a>'
COMMIT = f'<a href="{esc(os.getenv("DRONE_COMMIT_LINK"))}">'\
    f'{esc(os.getenv("DRONE_COMMIT_SHA")[:7])}</a>'\
    f' by {esc(os.getenv("DRONE_COMMIT_AUTHOR_NAME"))}'
REPO = f'<a href="{esc(os.getenv("DRONE_REPO_LINK"))}">{esc(os.getenv("DRONE_REPO"))}</a>'

if '--start' in sys.argv:
    bot.sendMessage(chat_id=CHAT_ID, text=f'⚙️ Pipeline {BUILD_LINK} for {REPO}'
                                          f' (commit {COMMIT}) started.',
                    parse_mode='HTML', disable_web_page_preview=True)
elif OK:
    bot.sendMessage(chat_id=CHAT_ID, text=f'✅ Pipeline {BUILD_LINK} for '
                                          f'{REPO} (commit {COMMIT}) succeed!',
                    parse_mode='HTML', disable_web_page_preview=True)
else:
    bot.sendMessage(chat_id=CHAT_ID, text=f'❌ Pipeline {BUILD_LINK} for '
                                          f'{REPO} (commit {COMMIT}) failed!',
                    parse_mode='HTML', disable_web_page_preview=True)
