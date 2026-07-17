#!/usr/bin/env /home/solidmasker/.local/share/tg-userbot-venv/bin/python
import os
import sys
import asyncio

# --- working on Python 3.14+ ---
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
# ----------------------------

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler

# Path to config
CONFIG_FILE = os.path.expanduser("~/.config/tg-bot/config.conf")

# Default values
API_ID = None
API_HASH = None
TARGET_CHAT = "me"

# Parsing a Bash config
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                val = val.strip().strip('"').strip("'")
                if key == "API_ID" and val.isdigit():
                    API_ID = int(val)
                elif key == "API_HASH":
                    API_HASH = val
                elif key == "FRIEND_CHAT_ID":
                    TARGET_CHAT = int(val) if val.lstrip('-').isdigit() else val

# If the keys are not found in the config, the code terminates.
if not API_ID or not API_HASH:
    print("\033[1;31mОшибка: API_ID или API_HASH не найдены в config.conf!\033[0m")
    print("Пожалуйста, добавьте их в ~/.config/tg-bot/config.conf")
    sys.exit(1)

os.makedirs(os.path.expanduser("~/.config/tg-bot"), exist_ok=True)
app = Client(
    "my_account",
    api_id=API_ID,
    api_hash=API_HASH,
    workdir=os.path.expanduser("~/.config/tg-bot")
)

# Incoming message processing function
async def my_handler(client, message):
    global TARGET_CHAT
    if message.chat and message.chat.id == TARGET_CHAT:
        sender_name = message.from_user.first_name if message.from_user else "Собеседник"
        text = message.text or "[Вложение/Медиа]"

        sys.stdout.write("\r\033[K")
        print(f"[\033[1;32m{message.date.strftime('%H:%M:%S')}\033[0m] \033[1;34m{sender_name}\033[0m: {text}")
        sys.stdout.write("\033[1;30mОтправить >> \033[0m")
        sys.stdout.flush()

# Asynchronous input and sending
async def input_loop():
    global TARGET_CHAT
    print("\033[1;35m========================================")
    print("    Terminal Userbot v1.0!   ")
    print(f"   Текущий чат: {TARGET_CHAT}")
    print("----------------------------------------")
    print("   Команды управления:")
    print("   * /chat <ID или @username> - сменить собеседника")
    print("   * /me                      - переключить на Избранное")
    print("   * /who                     - показать текущий чат")
    print("   * /mchats                  - показать список главных чатов")
    print("   * exit                     - выход")
    print("========================================\033[0m\n")

    loop_instance = asyncio.get_running_loop()
    while True:
        sys.stdout.write("\033[1;30mОтправить >> \033[0m")
        sys.stdout.flush()
        user_input = await loop_instance.run_in_executor(None, sys.stdin.readline)
        user_input = user_input.strip()

        if not user_input:
            continue

        # Command processing
        if user_input.lower() == 'exit':
            break

        if user_input.startswith('/chat '):
            new_chat = user_input.split(' ', 1)[1].strip()
            if new_chat.lstrip('-').isdigit():
                TARGET_CHAT = int(new_chat)
            else:
                TARGET_CHAT = new_chat

            sys.stdout.write("\033[1A\033[K")
            print(f"\033[1;33m[Система] Чат переключен на: {TARGET_CHAT}\033[0m")
            continue

        if user_input.lower() == '/me':
            TARGET_CHAT = "me"
            sys.stdout.write("\033[1A\033[K")
            print("\033[1;33m[Система] Переключено на Избранное (Saved Messages)\033[0m")
            continue

        if user_input.lower() == '/who':
            sys.stdout.write("\033[1A\033[K")
            print(f"\033[1;33m[Система] Сейчас активен чат: {TARGET_CHAT}\033[0m")
            continue

        if user_input.lower() == '/mchats':
            sys.stdout.write("\033[1A\033[K")
            print("\033[1;33m[Система] Доступные быстрые чаты (нажмите цифру для перехода):\033[0m")
            print("\033[34m[1] Чат 1 - @username1\033[0m")
            print("\033[34m[2] Чат 2 - @username2\033[0m")
            print("\033[34m[3] Чат 3 - @username3\033[0m")
            print("\033[34m[4] Чат 4 - @username4\033[0m")
            continue

        # Quick jump using numbers
        if user_input in ["1", "2", "3", "4"]:
            sys.stdout.write("\033[1A\033[K")

            if user_input == "1":
                TARGET_CHAT = "@username1"
            elif user_input == "2":
                TARGET_CHAT = "@username2"
            elif user_input == "3":
                TARGET_CHAT = "@username3"
            elif user_input == "4":
                TARGET_CHAT = "@username4"

            print(f"\033[1;33m[Система] Быстрое переключение! Текущий чат: {TARGET_CHAT}\033[0m")
            continue

        # Стираем строку ввода перед отправкой
        sys.stdout.write("\033[1A\033[K")
        sys.stdout.flush()

        # Sending content
        try:
            if os.path.isfile(user_input) and user_input.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                await app.send_photo(TARGET_CHAT, photo=user_input)
                print(f"[\033[1;32mОтправлено\033[0m] \033[1;33mЯ\033[0m: \033[36m[Отправил фото: {os.path.basename(user_input)}]\033[0m")
            else:
                await app.send_message(TARGET_CHAT, text=user_input)
                print(f"[\033[1;32mОтправлено\033[0m] \033[1;33mЯ\033[0m: {user_input}")
        except Exception as e:
            print(f"\033[1;31mОшибка отправки в чат '{TARGET_CHAT}':\033[0m {e}")

async def main():
    app.add_handler(MessageHandler(my_handler, filters.incoming))
    async with app:
        await input_loop()

if __name__ == "__main__":
    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n\033[1;31mЧат завершен.\033[0m")
