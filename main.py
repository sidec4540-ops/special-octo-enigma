import time
import sys
import os
import logging.config
import colorama
from colorama import Fore, Style
from Utils.logger import LOGGER_CONFIG
import Utils.cardinal_tools
from cardinal import Cardinal
from locales.localizer import Localizer
from configparser import ConfigParser
import requests

VERSION = "0.1.17.6"

Utils.cardinal_tools.set_console_title(f"FunPay Cardinal v{VERSION}")

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(__file__))

folders = ["configs", "logs", "storage", "storage/cache", "storage/plugins", "storage/products", "plugins"]
for i in folders:
    if not os.path.exists(i):
        os.makedirs(i)

colorama.init()
logging.config.dictConfig(LOGGER_CONFIG)
logging.raiseExceptions = False
logger = logging.getLogger("main")

print(f"{Fore.RED}{Style.BRIGHT}v{VERSION}{Style.RESET_ALL}\n")
print(f"{Fore.MAGENTA}{Style.BRIGHT}By Woopertail, @sidor0912{Style.RESET_ALL}")

# ==================== ЗАГРУЗКА КЛЮЧЕЙ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ====================
GOLDEN_KEY = os.getenv("FUNPAY_TOKEN", "")
TG_TOKEN = os.getenv("TG_BOT_TOKEN", "")
TG_USER_ID = os.getenv("TG_USER_ID", "")

if not GOLDEN_KEY:
    print("ОШИБКА: Переменная FUNPAY_TOKEN не установлена!")
    print("Добавьте её в Railway -> Variables")
    sys.exit(1)

if not TG_TOKEN:
    print("ОШИБКА: Переменная TG_BOT_TOKEN не установлена!")
    print("Добавьте её в Railway -> Variables")
    sys.exit(1)

if not TG_USER_ID:
    print("ОШИБКА: Переменная TG_USER_ID не установлена!")
    print("Добавьте её в Railway -> Variables")
    sys.exit(1)

print(f"Golden key загружен из переменной окружения")
print(f"Telegram токен загружен из переменной окружения")
print(f"Telegram user_id: {TG_USER_ID}")

# ==================== КОНФИГ ====================
MAIN_CFG = ConfigParser(delimiters=(":",), interpolation=None)
MAIN_CFG.optionxform = str

MAIN_CFG["FunPay"] = {
    "golden_key": GOLDEN_KEY,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "autoRaise": "0",
    "autoResponse": "0",
    "autoDelivery": "0",
    "multiDelivery": "0",
    "autoRestore": "0",
    "autoDisable": "0",
    "oldMsgGetMode": "0",
    "locale": "ru"
}

MAIN_CFG["Telegram"] = {
    "enabled": "1",
    "token": TG_TOKEN,
    "user_id": TG_USER_ID,
    "secretKeyHash": "MyPassword123",
    "blockLogin": "0",
    "proxy": ""
}

MAIN_CFG["Proxy"] = {
    "enable": "0",
    "proxy": "",
    "check": "0"
}

MAIN_CFG["Other"] = {
    "watermark": "🐦",
    "requestsDelay": "4",
    "language": "ru"
}

MAIN_CFG["BlockList"] = {
    "blockDelivery": "0",
    "blockResponse": "0",
    "blockNewMessageNotification": "0",
    "blockNewOrderNotification": "0",
    "blockCommandNotification": "0"
}

MAIN_CFG["NewMessageView"] = {
    "includeMyMessages": "1",
    "includeFPMessages": "1",
    "includeBotMessages": "0",
    "notifyOnlyMyMessages": "0",
    "notifyOnlyFPMessages": "0",
    "notifyOnlyBotMessages": "0",
    "showImageName": "1"
}

MAIN_CFG["Greetings"] = {
    "ignoreSystemMessages": "0",
    "onlyNewChats": "0",
    "sendGreetings": "0",
    "greetingsText": "Привет, $chat_name!",
    "greetingsCooldown": "2"
}

MAIN_CFG["OrderConfirm"] = {
    "watermark": "1",
    "sendReply": "0",
    "replyText": "$username, спасибо за подтверждение заказа $order_id!"
}

MAIN_CFG["ReviewReply"] = {
    "star1Reply": "0",
    "star2Reply": "0",
    "star3Reply": "0",
    "star4Reply": "0",
    "star5Reply": "0",
    "star1ReplyText": "",
    "star2ReplyText": "",
    "star3ReplyText": "",
    "star4ReplyText": "",
    "star5ReplyText": ""
}

# Пустые объекты для автоответов
AR_CFG = ConfigParser(delimiters=(":",), interpolation=None)
AR_CFG.optionxform = str
AD_CFG = ConfigParser(delimiters=(":",), interpolation=None)
AD_CFG.optionxform = str
RAW_AR_CFG = {}

# ==================== ПРИНУДИТЕЛЬНЫЙ СБРОС ВЕБХУКА ====================
try:
    r = requests.get(f"https://api.telegram.org/bot{TG_TOKEN}/deleteWebhook")
    if r.status_code == 200:
        print("Webhook удалён, бот будет работать в режиме Long Polling")
    else:
        print(f"Не удалось удалить вебхук: {r.text}")
except Exception as e:
    print(f"Ошибка при удалении вебхука: {e}")

localizer = Localizer("ru")
_ = localizer.translate

logger.info("Запуск бота...")
print("Бот запускается...")

try:
    bot_instance = Cardinal(MAIN_CFG, AD_CFG, AR_CFG, RAW_AR_CFG, VERSION).init()
    # Принудительно запускаем цикл получения сообщений (Long Polling)
    bot_instance.run()
except KeyboardInterrupt:
    logger.info("Завершаю программу...")
    sys.exit()
except Exception as e:
    logger.critical(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()
    time.sleep(5)
    sys.exit() 
