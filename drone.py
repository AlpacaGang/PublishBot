import telegram
import os


def esc(text, quote=False):
    return telegram.utils.helpers.escape(text, quote)


CHAT_ID = os.getenv("CHAT_ID")
if not CHAT_ID.startswith("-100"):
    CHAT_ID = f"-100{CHAT_ID}"

OK = os.getenv("DRONE_BUILD_STATUS") == 'success'

bot = telegram.Bot(token=os.getenv("BOT_TOKEN"))

BUILD_NUMBER = esc(os.getenv("DRONE_BUILD_NUMBER", "<unknown>"))
COMMIT = f'<a href="{esc(os.getenv("DRONE_COMMIT_LINK"))}">'\
               f'{esc(os.getenv("DRONE_COMMIT_SHA")[:7])}</a>'\
               f' by {esc(os.getenv("DRONE_COMMIT_AUTHOR_NAME"))}'
REPO = f'<a href="{esc(os.getenv("DRONE_REPO_LINK"))}">{esc(os.getenv("DRONE_REPO"))}</a>'
if OK:
    bot.send_message(chat_id=CHAT_ID, text=f'✅ Pipeline {BUILD_NUMBER} for '
                                           f'{REPO} (commit {COMMIT}) succeed!',
                     parse_mode='HTML')
else:
    bot.send_message(chat_id=CHAT_ID, text=f'❌ Pipeline {BUILD_NUMBER} for '
                                           f'{REPO} (commit {COMMIT}) failed!',
                     parse_mode='HTML')
