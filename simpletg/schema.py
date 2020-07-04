from typing import Dict


class Argument:
    def __init__(self, required: bool, type: type):
        self.required = bool(required)
        self.type = type


class ParseMode:
    HTML = 'HTML'
    Markdown = 'Markdown'
    MarkdownV2 = 'MarkdownV2'

    def __new__(cls, name):
        name = name.lower()
        if name in ['md', 'markdown']:
            return cls.Markdown
        elif name in ['md2', 'mdv2', 'markdownv2', 'markdown2']:
            return cls.MarkdownV2
        elif name in ['html']:
            return cls.HTML
        raise ValueError(f'unknown parse mode: {name}')


methods: Dict[str, Dict[str, Argument]] = {
    'get_me': {
        'args': {}
    },
    'send_message': {
        'args': {
            #                required type
            'chat_id': Argument(True, int),
            'text': Argument(True, str),
            'parse_mode': Argument(False, ParseMode),
            'disable_web_page_preview': Argument(False, bool),
            'disable_notification': Argument(False, bool),
            'reply_to_message_id': Argument(False, int),
            'reply_markup': Argument(False, dict)
        }
    }
}
