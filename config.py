import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMINS = list(map(int, os.getenv("ADMINS", "").split(',')))
    BOT_NAME = "EarnBot"
    MIN_WITHDRAW = 500
    REFERRAL_BONUS = 10
    REFERRAL_REWARD = 0.5
    DB_URL = "sqlite+aiosqlite:///database.db"
    CRYPTO_WALLET = os.getenv("CRYPTO_WALLET", "")
    PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN", "")
    SUPPORT_CHAT = "@your_support_chat"
    NEWS_CHANNEL = "@your_news_channel"

config = Config()
