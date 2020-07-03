import telegram
import argparse
import os


def esc(text, quote=False):
    return telegram.utils.helpers.escape(text, quote)


CHAT_ID = os.getenv("CHAT_ID")
if not CHAT_ID.startswith("-100"):
    CHAT_ID = f"-100{CHAT_ID}"


def parse_args():
    parser = argparse.ArgumentParser()
    status = parser.add_mutually_exclusive_group(required=True)
    status.add_argument('--success', dest='ok', action='store_true')
    status.add_argument('--failure', dest='ok', action='store_false')
    return parser.parse_args()


bot = telegram.Bot(token=os.getenv("BOT_TOKEN"))
args = parse_args()

BUILD_NUMBER = os.getenv("DRONE_BUILD_NUMBER", "<unknown>")
COMMIT = f'<a href="{esc(os.getenv("DRONE_COMMIT_LINK"))}">'\
               f'{esc(os.getenv("DRONE_COMMIT_SHA", "0000000")[:7])}</a>'\
               f' by {esc(os.getenv("DRONE_COMMIT_AUTHOR", "anonymous"))}'
REPO = f'<a href="{esc(os.getenv("DRONE_REPO_LINK"))}">{esc(os.getenv("DRONE_REPO"))}</a>'
if args.ok:
    print(f'✅ Pipeline {esc(BUILD_NUMBER)} for {REPO} (commit {COMMIT}) succeed!')
    bot.send_message(chat_id=CHAT_ID, text=f'✅ Pipeline {esc(BUILD_NUMBER)} for '
                                           f'{REPO} (commit {COMMIT}) succeed!',
                     parse_mode='HTML')
else:
    bot.send_message(chat_id=CHAT_ID, text=f'❌ Pipeline {esc(BUILD_NUMBER)} for '
                                           f'{REPO} (commit {COMMIT}) failed!',
                     parse_mode='HTML')
