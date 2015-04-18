import os


# *****************************
# Environment specific settings
# *****************************

APP_NAME = "AppName"

# The settings below can (and should) be over-ruled by OS environment variable settings

# Flask settings                     # Generated with: import os; os.urandom(24)
SECRET_KEY = os.getenv('SECRET_KEY', '\xb9\x8d\xb5\xc2\xc4Q\xe7\x8ej\xe0\x05\xf3\xa3kp\x99l\xe7\xf2i\x00\xb1-\xcd')
# PLEASE USE A DIFFERENT KEY FOR PRODUCTION ENVIRONMENTS!
                                                    
# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.sqlite')

# Flask-Mail settings
MAIL_USERNAME =           os.getenv('MAIL_USERNAME',        'email@example.com')
MAIL_PASSWORD =           os.getenv('MAIL_PASSWORD',        'password')
MAIL_DEFAULT_SENDER =     os.getenv('MAIL_DEFAULT_SENDER',  APP_NAME + ' <noreply@example.com>')
MAIL_SERVER =             os.getenv('MAIL_SERVER',          'smtp.gmail.com')
MAIL_PORT =           int(os.getenv('MAIL_PORT',            '465'))
MAIL_USE_SSL =        int(os.getenv('MAIL_USE_SSL',         '1'))  # Use '1' for True and '0' for False
MAIL_USE_TLS =        int(os.getenv('MAIL_USE_TLS',         '0'))  # Use '1' for True and '0' for False

ADMINS = []
admin1 = os.getenv('ADMIN1', '"Admin One" <admin1@gmail.com>')
admin2 = os.getenv('ADMIN2', '')
admin3 = os.getenv('ADMIN3', '')
admin4 = os.getenv('ADMIN4', '')
if admin1: ADMINS.append(admin1)
if admin2: ADMINS.append(admin2)
if admin3: ADMINS.append(admin3)
if admin4: ADMINS.append(admin4)


# ***********************************
# Settings common to all environments
# ***********************************

# Application settings
APP_SYSTEM_ERROR_SUBJECT_LINE = APP_NAME + " system error"

# Flask settings
CSRF_ENABLED = True

# Flask-User settings
USER_APP_NAME = APP_NAME
USER_AFTER_LOGIN_ENDPOINT = 'member_page'
USER_AFTER_LOGOUT_ENDPOINT = 'home_page'

