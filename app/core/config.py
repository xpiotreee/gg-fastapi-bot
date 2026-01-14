import os
from dotenv import load_dotenv
from pygg.user import Gender

load_dotenv()

class Settings:
    def __init__(self):
        self.REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
        self.REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
        self.REDIS_DB = int(os.getenv('REDIS_DB', 0))

        # Default Bot Credentials (Optional)
        self.DEFAULT_UIN = os.getenv('GG_UIN')
        self.DEFAULT_PASSWORD = os.getenv('GG_PASSWORD')
        if self.DEFAULT_UIN:
            self.DEFAULT_UIN = int(self.DEFAULT_UIN)

        # Default Roulette Settings
        gender_val = os.getenv('GG_GENDER')
        self.DEFAULT_GENDER = int(gender_val) if gender_val is not None else Gender.MAN
        self.MIN_AGE = int(os.getenv('MIN_AGE', 20))
        self.MAX_AGE = int(os.getenv('MAX_AGE', 60))

settings = Settings()
