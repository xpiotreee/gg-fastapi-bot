import os
from dotenv import load_dotenv
from pygg.user import Gender

load_dotenv()


uin = int(os.getenv('GG_UIN'))
password = os.getenv('GG_PASSWORD')

gender_val = os.getenv('GG_GENDER')
gender = int(gender_val) if gender_val is not None else Gender.MAN

min_age = int(os.getenv('MIN_AGE', 20))
max_age = int(os.getenv('MAX_AGE', 60))