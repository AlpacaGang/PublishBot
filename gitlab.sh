#!/bin/bash
send_message() {
    curl \
    --data-urlencode "text=$1" \
    --data-urlencode "parse_mode=HTML" \
    --data-urlencode "chat_id=$CHAT_ID" \
    --data-urlencode "disable_web_page_preview=true" \
    -X POST \
    https://api.telegram.org/bot$BOT_TOKEN/sendMessage > /dev/null 2> /dev/null;
}

escape_html () {
    local s
    s=${@//&/&amp;}
    s=${s//</&lt;}
    s=${s//>/&gt;}
    echo -n $s
}

INSTANCE_URL="https://git.vanutp.dev"
REPO_LINK="$INSTANCE_URL/$CI_PROJECT_PATH"
COMMIT_LINK="$REPO_LINK/-/commit/$CI_COMMIT_SHA"
BUILD_LINK="<a href=\"$(escape_html $REPO_LINK/-/pipelines/$CI_PIPELINE_ID)\">#$CI_PIPELINE_ID</a>"
COMMIT="<a href=\"$(escape_html $COMMIT_LINK)\">${CI_COMMIT_SHA::7}</a>"
REPO="<a href=\"$(escape_html $REPO_LINK)\">$(escape_html $CI_PROJECT_PATH)</a>"

if [[ $1 == "--start" ]]; then
    send_message "⚙️ Pipeline $BUILD_LINK for $REPO (commit $COMMIT) started."
elif [[ $1 == "--fail" ]]; then
    send_message "❌ Pipeline $BUILD_LINK for $REPO (commit $COMMIT) failed!"
else
    send_message "✅ Pipeline $BUILD_LINK for $REPO (commit $COMMIT) succeed!"
fi
