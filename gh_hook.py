import json

from flask import Flask, request
from telegram import ParseMode
from telegram.ext import Updater
from telegram.utils.helpers import escape

from secure import BOT_TOKEN, PROXY  # pylint: disable=E0401

app = Flask(__name__)

bot = Updater(BOT_TOKEN, request_kwargs=PROXY).bot


@app.route('/trigger/<chat_id>', methods=['POST'])
def trigger(chat_id):
    show_author_name = bool(int(request.args.get('show_author_name', '0')))
    multiline_commit = bool(int(request.args.get('multiline_commit', '0')))
    max_commits = int(request.args.get('max_commits', '6'))
    if not chat_id.startswith('-100'):
        chat_id = int(f'-100{chat_id}')
    chat_id = int(chat_id)
    data = json.loads(request.data)
    if 'forced' not in data:
        if 'project' in data:
            service = 'gitlab'
            repo_url = data['project']['homepage']
            repo_name = data['project']['path_with_namespace']
        else:
            service = 'gitea'
            repo_url = data['repository']['html_url']
            repo_name = data['repository']['full_name']
    else:
        service = 'github'
        repo_url = data['repository']['html_url']
        repo_name = data['repository']['full_name']
    if service == 'github' and data['forced']:
        head_sha = data['after']
        ref = f'{escape(repo_name)}:{escape(data["ref"].split("/")[-1])}'
        head = f'<a href="{repo_url}/commit/{head_sha}">{escape(head_sha[:7])}</a>'
        if show_author_name:
            head += f'\n- by {data["pusher"]["name"]}'
        bot.send_message(chat_id=chat_id, text=f'🔨 Force pushed. <b>{ref}</b> is now at {head}',
                         parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    else:
        if len(data['commits']) <= max_commits or max_commits == 0:
            commits = []
            for commit in data['commits']:
                msg = escape(commit['message'])
                if not multiline_commit:
                    msg = msg.split('\n')[0]
                commit_msg = f'<a href="{escape(commit["url"])}">{escape(commit["id"][:7])}</a>: <code>{msg}</code>'
                if show_author_name:
                    commit_msg += f'\n- by {escape(commit["author"]["name"])}'
                commits.append(commit_msg)
            commits = ':\n\n' + '\n'.join(commits)
        else:
            commits = ''
        commits_word = 'commit' if len(data['commits']) == 1 else 'commits'
        ref = f'{escape(repo_name)}:{escape(data["ref"].split("/")[-1])}'
        bot.send_message(chat_id=chat_id,
                         text=f'🔨 {len(data["commits"])} new {commits_word} to <b>{ref}</b>' + commits,
                         parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    return 'OK'


app.run(host='0.0.0.0', port=8009)
