import requests as rq
import simpletg.schema as schema
from simpletg.schema import ParseMode  # noqa: F401
API_URL = 'https://api.telegram.org/bot{}/{}'


class TelegramError(Exception):
    pass


class TelegramAPI:
    def __init__(self, token):
        self.token = token

    def _check_args(self, method, *args, **kwargs):
        used = {}
        sargs = schema.methods[method]['args']
        for pa, sa in zip(args, sargs):
            if sa in kwargs:
                raise TypeError(f'{method} got multiple values for {sa}')
            kwargs[sa] = pa
        for k, v in kwargs.items():
            kwargs[k] = sargs[k].type(v)
            used[k] = True
        for a in sargs:
            if sargs[a].required and not used.get(a):
                raise TypeError(f'{method} missing required argument {a}')
        return kwargs

    def __call__(self, method, *args, **kwargs):
        if method not in schema.methods:
            raise ValueError(f'unknown method: {method}')
        data = self._check_args(method, *args, **kwargs)
        res = rq.post(API_URL.format(self.token, method), data=data).json()
        if not res['ok']:
            raise TelegramError(res['description'])
        else:
            return res['result']

    def get_me(self):
        return self('get_me')

    def __getattr__(self, item):
        if item not in schema.methods:
            raise ValueError(f'unknown method: {item}')
        return (lambda *args, **kwargs: self(item, *args, **kwargs))
