import json

from flask import Flask, request
from telegram import ParseMode
from telegram.ext import Updater
from telegram.utils.helpers import escape

from secure import BOT_TOKEN, PROXY  # pylint: disable=E0401

app = Flask(__name__)

bot = Updater(BOT_TOKEN, request_kwargs=PROXY).bot


@app.route('/trigger/<chat_id>/<options>', methods=['POST'])
def trigger(chat_id, options):
    show_author_name = bool(int(options[0]))
    multiline_commit = bool(int(options[1]))
    if not chat_id.startswith('-100'):
        chat_id = int(f'-100{chat_id}')
    chat_id = int(chat_id)
    data = json.loads(request.data)
    gitea = 'forced' not in data
    if not gitea and data['forced']:
        head_sha = data["after"]
        ref = f'{escape(data["repository"]["full_name"])}:{escape(data["ref"].split("/")[-1])}'
        head = f'<a href="{data["repository"]["html_url"]}/commit/{head_sha}">{escape(head_sha[:7])}</a>'
        if show_author_name:
            head += f'\n- by {data["pusher"]["full_name"] if gitea else data["pusher"]["name"]}'
        bot.send_message(chat_id=chat_id, text=f'🔨 Some commits were reset. {ref} is now at {head}',
                         parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    else:
        if len(data['commits']) <= 6:
            commits = []
            for commit in data['commits']:
                msg = escape(commit["message"])
                if not multiline_commit:
                    msg = msg.split('\n')[0]
                commit_msg = f'<a href="{escape(commit["url"])}">{escape(commit["id"][:7])}</a>: <code>{msg}</code>'
                if show_author_name:
                    commit_msg += f'\n- by {commit["author"]["name"]}'
                commits.append(commit_msg)
            commits = ':\n\n' + '\n'.join(commits)
        else:
            commits = ''
        commits_word = 'commit' if len(data['commits']) == 1 else 'commits'
        ref = f'{escape(data["repository"]["full_name"])}:{escape(data["ref"].split("/")[-1])}'
        bot.send_message(chat_id=chat_id,
                         text=f'🔨 {len(data["commits"])} new {commits_word} to <b>{ref}</b>' + commits,
                         parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    return 'OK'


app.run(host='0.0.0.0', port=8009)
