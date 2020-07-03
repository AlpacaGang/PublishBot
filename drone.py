import telegram
import argparse
import os

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
COMMIT = f'[{os.getenv("DRONE_COMMIT_LINK")}]'\
               f'({os.getenv("DRONE_COMMIT_SHA", "0000000")[:7]})'\
               f' by {os.getenv("DRONE_COMMIT_AUTHOR", "anonymous")}'
REPO = f'[{os.getenv("DRONE_REPO_LINK")}]({os.getenv("DRONE_REPO")})'
if args.ok:
    bot.send_message(chat_id=CHAT_ID, text=f'✅ Pipeline {BUILD_NUMBER} for '
                                           f'{REPO} (commit {COMMIT}) succeed!',
                     parse_mode='MarkdownV2')
else:
    bot.send_message(chat_id=CHAT_ID, text=f'❌ Pipeline {BUILD_NUMBER} for '
                                           f'{REPO} (commit {COMMIT}) failed!',
                     parse_mode='MarkdownV2')
