import glob
import multiprocessing
import os
import shutil
import sys
import time
from datetime import datetime, timezone, timedelta
from zipfile import ZipFile

from git import Repo
from telegram import Bot, ParseMode


os.environ['KBUILD_BUILD_USER'] = 'fedshat'
os.environ['KBUILD_BUILD_HOST'] = 'fedshatci'
os.environ['TZ'] = 'Europe/Moscow'
TZ = timezone(timedelta(hours=3))
os.environ['KERNEL_USE_CCACHE'] = '1'

TIMESTAMP = datetime.now(TZ)

CHAT_ID = -1001115967921
FILENAME = f'AlpacaKernel-v5-GCC-9.x-LTO-{TIMESTAMP.strftime("%y%m%d-%H%M")}.zip'
COMPILER_STRING = 'GCC 9.x'
KERNEL_VERSION = 'Alpaca, v5, LTO'
DEVICE = 'platina'
DEFCONFIG = 'platina_defconfig'
CROSS_COMPILE = '~/build/tools/arm64-gcc/bin/aarch64-elf-'
NPROC = multiprocessing.cpu_count()

bot = Bot(os.environ.get('TOKEN'))
repo = Repo('.')

bot.send_message(chat_id=CHAT_ID,
                 text=f'⚙️ Build for {DEVICE} started:\n'
                      f'Compiler: `{COMPILER_STRING}`\n'
                      f'Device: `{DEVICE}`\n'
                      f'Kernel: `{KERNEL_VERSION}\n'
                      f'Commit: `{repo.active_branch.name}:{repo.active_branch.commit.hexsha[:7]}:{repo.active_branch.commit.message}`\n'
                      f'Commit: `',
                 parse_mode=ParseMode.HTML, disable_web_page_preview=True)

os.remove('.config')
print('========== Making defconfig ==========')
os.system(f'make O=out ARCH=arm64 {DEFCONFIG}')

print('========== Building kernel ==========')
if os.system(f'make -j{NPROC} O=out ARCH=arm64 CROSS_COMPILE={CROSS_COMPILE}'):
    print('========== Build succeed ==========')
    shutil.move('out/arch/arm64/boot/Image.gz-dtb', '~/build/AK3/Image.gz-dtb')
    os.chdir('~/build/AK3')
    with ZipFile(FILENAME, 'w') as _zip:
        for folder_name, dirs, filenames in os.walk('.'):
            if folder_name.startswith('.git'):
                continue
            for curr_filename in filenames:
                _zip.write(os.path.join(folder_name, curr_filename))
    build_time = datetime.fromtimestamp(0, tz=TZ) + (datetime.now(TZ) - TIMESTAMP)
    bot.send_message(chat_id=CHAT_ID,
                     text=f'✅ Build for {DEVICE} with {COMPILER_STRING} failed in a {build_time.strftime("%M mins %S secs")}!')
    bot.send_document(chat_id=CHAT_ID, document=open(FILENAME, 'rb'))
    os.remove(FILENAME)
else:
    print('========== Build failed ==========')
    build_time = datetime.fromtimestamp(0, tz=TZ) + (datetime.now(TZ) - TIMESTAMP)
    bot.send_message(chat_id=CHAT_ID,
                     text=f'❌ Build for {DEVICE} with {COMPILER_STRING} failed in a {build_time.strftime("%M mins %S secs")}!')
os.chdir('~/build/kernel_xiaomi_platina')