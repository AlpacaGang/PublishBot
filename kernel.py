import hashlib
import multiprocessing
import os
import sys
import subprocess
from datetime import datetime
from os.path import expanduser
from time import time

from git import Repo
from telegram import ParseMode, Bot
from telegram.utils.helpers import escape_markdown

os.environ['KBUILD_BUILD_USER'] = 'fedshat'
os.environ['KBUILD_BUILD_HOST'] = 'fedshatci'
os.environ['TZ'] = 'Europe/Moscow'

start_time = time()
TIMESTAMP = datetime.now()

CHAT_ID = -1001115967921
KERNEL_VERSION = f'Alpaca, {TIMESTAMP.strftime("%Y%m%d")}'
DEVICE = 'platina'
DEFCONFIG = 'platina_defconfig'
CROSS_COMPILE = 'aarch64-linux-gnu-'
CROSS_COMPILE_ARM32 = 'arm-linux-gnueabi-'
REPO = 'FedShat/msm-4.4'
NPROC = multiprocessing.cpu_count()

X508_PATH = expanduser('~') + '/certificate.pem'
PK8_PATH = expanduser('~') + '/key.pk8'
ZIPSIGNER_PATH = expanduser('~') + '/zipsigner-4.0.jar'

bot = Bot(os.environ.get('TOKEN'))
repo = Repo('.')
tree_dir = os.getcwd()


def update_tree(p, b):
    os.chdir(p)
    os.system('git fetch --all')
    os.system('git reset --hard ' + b)
    os.chdir(tree_dir)


COMPILER_STRING = subprocess.Popen([f'clang', '--version'], stdout=subprocess.PIPE) \
                      .communicate()[0].decode()[:-1]
COMPILER_STRING = COMPILER_STRING.split('\n')[0]
FILENAME = f'../AlpacaKernel-{os.environ.get("CIRCLE_BUILD_NUM")}-' \
           f'{TIMESTAMP.strftime("%Y%m%d-%H%M")}-{repo.active_branch.commit.hexsha[:8]}.zip'

commit_msg = escape_markdown(
    repo.active_branch.commit.message.split("\n")[0], version=2)
commit = f'`{repo.active_branch.name}:' \
         f'`[{repo.active_branch.commit.hexsha[:8]}]' \
         f'(https://github.com/{REPO}/commit/{repo.active_branch.commit.hexsha})`:`\n' \
         f'`{commit_msg}`'
build_url = escape_markdown(os.getenv("CIRCLE_BUILD_URL"), version=2)
bot.send_message(chat_id=CHAT_ID,
                 text=f'⚙️ *Build [\\#{os.environ.get("CIRCLE_BUILD_NUM")}]({build_url}) for {DEVICE} started:*\n'
                      f'*Compiler:* `{COMPILER_STRING}`\n'
                      f'*Device:* `{DEVICE}`\n'
                      f'*Kernel:* `{KERNEL_VERSION}`\n'
                      f'*Commit:* {commit}',
                 parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)
if os.path.isfile('.config'):
    os.remove('.config')
print('========== Making defconfig ==========')
os.system(f'make O=out ARCH=arm64 {DEFCONFIG}')
print('========== Building kernel ==========')
if not os.system(
        f'make -j{NPROC} O=out ARCH=arm64 CC=clang AR=llvm-ar NM=llvm-nm OBJCOPY=llvm-objcopy OBJDUMP=llvm-objdump STRIP=llvm-strip CROSS_COMPILE={CROSS_COMPILE} CROSS_COMPILE_ARM32={CROSS_COMPILE_ARM32}'):
    print('========== Build succeed ==========')
    os.rename('out/arch/arm64/boot/Image.gz-dtb',
              expanduser('~') + '/build/AK3/Image.gz-dtb')
    os.chdir(expanduser('~') + '/build/AK3')
    os.system(f'zip -r9 {FILENAME} * -x .git {FILENAME}')
    print('========== Signing ==========')
    delta = int(time() - start_time)
    build_time = f'{delta // 60 % 60} minutes {delta % 60} seconds'
    file_hash = hashlib.sha1()
    with open(FILENAME, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            file_hash.update(chunk)
    bot.send_document(chat_id=CHAT_ID, document=open(FILENAME, 'rb'),
                      caption=f'✅ Build [\\#{os.environ.get("CIRCLE_BUILD_NUM")}]({build_url}) for '
                              f'{DEVICE} finished in a {build_time} \\| *SHA1:* `{file_hash.hexdigest()}`',
                      parse_mode=ParseMode.MARKDOWN_V2)
    os.remove(FILENAME)
else:
    print('========== Build failed ==========')
    delta = int(time() - start_time)
    build_time = f'{delta // 60 % 60} minutes {delta % 60} seconds'
    bot.send_message(chat_id=CHAT_ID,
                     text=f'❌ Build [\\#{os.environ.get("CIRCLE_BUILD_NUM")}]({build_url}) for '
                          f'{DEVICE} failed in a {build_time}\\!', parse_mode=ParseMode.MARKDOWN_V2,
                     disable_web_page_preview=True)
    sys.exit(1)
os.chdir(tree_dir)
