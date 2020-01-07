import json

from flask import Flask, request
from telegram import ParseMode
from telegram.ext import Updater
from telegram.utils.helpers import escape

from secure import BOT_TOKEN, PROXY

app = Flask(__name__)

bot = Updater(BOT_TOKEN, request_kwargs=PROXY).bot


@app.route('/trigger/<user>/<repo>/<chat_id>', methods=['POST'])
def trigger(user, repo, chat_id):
    if not chat_id.startswith('-100'):
        chat_id = int(f'-100{chat_id}')
    chat_id = int(chat_id)
    data = json.loads(request.data)
    commits = []
    for commit in data['commits']:
        commits.append(
            f'<a href="{commit["url"]}">{commit["id"][:7]}</a>: {escape(commit["message"])} by {escape(commit["author"]["name"])}')
    bot.send_message(chat_id=chat_id,
                     text=f'🔨 {len(commits)} new commits to {escape(repo)}:\n\n' + escape("\n".join(commits)),
                     parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    return 'OK'


app.run(host='0.0.0.0', port=8009)
