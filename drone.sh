#!/bin/bash
send_message() {
    curl \
    --data-urlencode "text=$1" \
    --data-urlencode "parse_mode=HTML" \
    --data-urlencode "chat_id=$CHAT_ID" \
    --data-urlencode "disable_web_page_preview=true" \
    -X POST \
    https://api.telegram.org/bot$BOT_TOKEN/sendMessage;
}

escape_html () {
    local s
    s=${1//&/&amp;}
    s=${s//</&lt;}
    s=${s//>/&gt;}
    echo -n $s
}

GITEA="https://git.vanutp.dev"
GITHUB="https://github.com"
if [[ $DRONE_GIT_HTTP_URL == $GITEA* ]]; then
    DRONE_LINK="https://drone.vanutp.dev"
elif [[ $DRONE_GIT_HTTP_URL == $GITHUB* ]]; then
    DRONE_LINK="https://drone_gitea.vanutp.dev"
else
    equals="============"
    echo -e "$equals\nUnknown Git hosting ($GITEA and $GITHUB are only supported)\n$equals"
    exit 1
fi
BUILD_NUMBER=$(escape_html $DRONE_BUILD_NUMBER)
BUILD_LINK="<a href=\"$(escape_html $DRONE_LINK/$DRONE_REPO/$BUILD_NUMBER)\">#$BUILD_NUMBER</a>"
COMMIT="<a href=\"$(escape_html $DRONE_COMMIT_LINK)\">${DRONE_COMMIT_SHA::7}</a> by $(escape_html $DRONE_COMMIT_AUTHOR_NAME)"
REPO="<a href=\"$(escape_html $DRONE_REPO_LINK)\">$(escape_html $DRONE_REPO)</a>"

if [[ $1 == "--start" ]]; then
    send_message "⚙️ Pipeline $BUILD_LINK for $REPO (commit $COMMIT) started."
elif [[ $DRONE_BUILD_STATUS == "success" ]]; then
    send_message "✅ Pipeline $BUILD_LINK for $REPO (commit $COMMIT) succeed!"
else
    send_message "❌ Pipeline $BUILD_LINK for $REPO (commit $COMMIT) failed!"
fi
