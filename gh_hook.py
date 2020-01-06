import json

from flask import Flask, request
from telegram import Bot

from secure import BOT_TOKEN

app = Flask(__name__)

bot = Bot(BOT_TOKEN)


@app.route('/trigger/<user>/<repo>/<int:chat_id>', methods=['POST'])
def trigger(user, repo, chat_id):
    data = json.loads(request.data)
    commits = []
    for commit in data['commits']:
        commits.append(
            f'<a href="{commit["url"]}">{commit["sha"][:7]}</a>: {commit["message"]} by {commit["author"]["name"]}')
    bot.send_message(chat_id=chat_id, text=f'🔨 {len(commits)} new commits to {repo}:\n\n' + "\n".join(commits))


app.run(host='0.0.0.0', port=8009)
