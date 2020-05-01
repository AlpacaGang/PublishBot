import hashlib
import multiprocessing
import os
from datetime import datetime, timezone, timedelta
from os.path import expanduser

from git import Repo
from telegram import ParseMode, Bot
from telegram.utils.helpers import escape_markdown

os.environ['KBUILD_BUILD_USER'] = 'fedshat'
os.environ['KBUILD_BUILD_HOST'] = 'fedshatci'
os.environ['TZ'] = 'Europe/Moscow'
TZ = timezone(timedelta(hours=3))
os.environ['KERNEL_USE_CCACHE'] = '1'

TIMESTAMP = datetime.now(TZ)

CHAT_ID = -1001115967921
FILENAME = f'../AlpacaKernel-v5-GCC-9.x-LTO-{TIMESTAMP.strftime("%y%m%d-%H%M")}.zip'
COMPILER_STRING = 'GCC 9.x'
KERNEL_VERSION = 'Alpaca, v5, LTO'
DEVICE = 'platina'
DEFCONFIG = 'platina_defconfig'
CROSS_COMPILE = expanduser('~') + '/build/tools/arm64-gcc/bin/aarch64-elf-'
REPO = 'AlpacaGang/kernel_xiaomi_platina'
NPROC = multiprocessing.cpu_count()

bot = Bot(os.environ.get('TOKEN'))
repo = Repo('.')

commit_msg = escape_markdown(repo.active_branch.commit.message.split("\n")[0], version=2)
commit = f'`{repo.active_branch.name}:' \
         f'`[{repo.active_branch.commit.hexsha[:7]}](https://github.com/{REPO}/commit/{repo.active_branch.commit.hexsha})\n' \
         f'`{commit_msg}`'
bot.send_message(chat_id=CHAT_ID,
                 text=f'⚙️ Build for {DEVICE} started:\n'
                      f'Compiler: `{COMPILER_STRING}`\n'
                      f'Device: `{DEVICE}`\n'
                      f'Kernel: `{KERNEL_VERSION}`\n'
                      f'Commit: {commit}',
                 parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)
if os.path.isfile('.config'):
    os.remove('.config')
print('========== Making defconfig ==========')
os.system(f'make O=out ARCH=arm64 {DEFCONFIG}')

print('========== Building kernel ==========')
if not os.system(f'make -j{NPROC} O=out ARCH=arm64 CROSS_COMPILE={CROSS_COMPILE}'):
    print('========== Build succeed ==========')
    os.rename('out/arch/arm64/boot/Image.gz-dtb', expanduser('~') + '/build/AK3/Image.gz-dtb')
    os.chdir(expanduser('~') + '/build/AK3')
    os.system(f'zip -r9 {FILENAME} * -x .git {FILENAME}')
    build_time = datetime.fromtimestamp(0, tz=TZ) + (datetime.now(TZ) - TIMESTAMP)
    hash_md5 = hashlib.md5()
    with open(FILENAME, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    bot.send_document(chat_id=CHAT_ID, document=open(FILENAME, 'rb'),
                      caption=f'✅ Build for {DEVICE} finished in a '
                              f'{build_time.strftime("%-M mins %-S secs")} \\| MD5: `{hash_md5.hexdigest()}`',
                      parse_mode=ParseMode.MARKDOWN_V2)
    os.remove(FILENAME)
else:
    print('========== Build failed ==========')
    build_time = datetime.fromtimestamp(0, tz=TZ) + (datetime.now(TZ) - TIMESTAMP)
    bot.send_message(chat_id=CHAT_ID,
                     text=f'❌ Build for {DEVICE} failed in a {build_time.strftime("%-M mins %-S secs")}!')
os.chdir(expanduser('~') + '/build/kernel_xiaomi_platina')
