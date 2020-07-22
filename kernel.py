import hashlib
import multiprocessing
import os
from datetime import datetime
from os.path import expanduser
from time import time

from git import Repo
from telegram import ParseMode, Bot
from telegram.utils.helpers import escape_markdown

os.environ['KBUILD_BUILD_USER'] = 'fedshat'
os.environ['KBUILD_BUILD_HOST'] = 'fedshatci'
os.environ['TZ'] = 'Europe/Moscow'
os.environ['KERNEL_USE_CCACHE'] = '1'

start_time = time()
TIMESTAMP = datetime.now()

CHAT_ID = -1001115967921
FILENAME = f'../platina-Kernel-{TIMESTAMP.strftime("%Y%m%d-%H%M")}-unsigned.zip'
COMPILER_STRING = 'GCC 10.x'
KERNEL_VERSION = ''
DEVICE = 'platina'
DEFCONFIG = 'platina_defconfig'
CROSS_COMPILE = expanduser('~') + '/build/tools/arm64-gcc/bin/aarch64-elf-'
REPO = 'FedorShatokhin2005/msm-4.4'
NPROC = multiprocessing.cpu_count()

X508_PATH = expanduser('~') + '/certificate.pem'
PK8_PATH = expanduser('~') + '/key.pk8'
ZIPSIGNER_PATH = expanduser('~') + '/zipsigner-3.0.jar'

bot = Bot(os.environ.get('TOKEN'))
repo = Repo('.')
tree_dir = os.getcwd()


def update_tree(p, b):
    os.chdir(p)
    os.system('git fetch --all')
    os.system('git reset --hard ' + b)
    os.chdir(tree_dir)


update_tree('.', 'origin/kernel.lnx.4.4.r38-rel')
update_tree('../AK3', 'origin/master')
update_tree('../tools/arm64-gcc', '811a3bc6b40ad924cd1a24a481b6ac5d9227ff7e')

SIGNED_FILENAME = f'../platina-Kernel-{TIMESTAMP.strftime("%Y%m%d-%H%M")}-{repo.active_branch.commit.hexsha[:8]}.zip'

commit_msg = escape_markdown(
    repo.active_branch.commit.message.split("\n")[0], version=2)
commit = f'`{repo.active_branch.name}:' \
         f'`[{repo.active_branch.commit.hexsha[:8]}](https://github.com/{REPO}/commit/{repo.active_branch.commit.hexsha})`:`\n' \
         f'`{commit_msg}`'
bot.send_message(chat_id=CHAT_ID,
                 text=f'⚙️ *Build for {DEVICE} started:*\n'
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
if not os.system(f'make -j{NPROC} O=out ARCH=arm64 CROSS_COMPILE={CROSS_COMPILE}'):
    print('========== Build succeed ==========')
    os.rename('out/arch/arm64/boot/Image.gz-dtb',
              expanduser('~') + '/build/AK3/Image.gz-dtb')
    os.chdir(expanduser('~') + '/build/AK3')
    os.system(f'zip -r9 {FILENAME} * -x .git {FILENAME}')
    print('========== Signing ==========')
    os.system(
        f'java -jar {ZIPSIGNER_PATH} {X508_PATH} {PK8_PATH} {FILENAME} {SIGNED_FILENAME}')
    delta = int(time() - start_time)
    build_time = f'{delta // 60 % 60} minutes {delta % 60} seconds'
    hash = hashlib.sha1()
    with open(SIGNED_FILENAME, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash.update(chunk)
    bot.send_document(chat_id=CHAT_ID, document=open(SIGNED_FILENAME, 'rb'),
                      caption=f'✅ Build for {DEVICE} finished in a '
                              f'{build_time} \\| *SHA1:* `{hash.hexdigest()}`',
                      parse_mode=ParseMode.MARKDOWN_V2)
    os.system(f'scp {SIGNED_FILENAME} fedshat@{os.environ.get("IP")}:~/builds')
    os.remove(SIGNED_FILENAME)
    os.remove(FILENAME)
else:
    print('========== Build failed ==========')
    delta = int(time() - start_time)
    build_time = f'{delta // 60 % 60} minutes {delta % 60} seconds'
    bot.send_message(chat_id=CHAT_ID,
                     text=f'❌ Build for {DEVICE} failed in a {build_time}!')
os.chdir(tree_dir)
