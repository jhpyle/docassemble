from flask import current_app
from flask_wtf.csrf import generate_csrf as base_generate_csrf
from docassemble.webapp.config import (
    DEFAULT_LANGUAGE,
    DEFAULT_LOCALE,
    DEFAULT_DIALECT,
    DEFAULT_VOICE,
    DEFAULT_TIMEZONE,
    DEFAULT_COUNTRY,
    DEBUG,
    DEFAULT_TABLE_CLASS,
    DEFAULT_THEAD_CLASS,
    hostname,
    daconfig,
)
from docassemble.webapp.twilio.helpers import twilio_config
from docassemble.webapp.daredis import r, r_user
from docassemble.webapp.files.savedfile import SavedFile
from ..hooks.impl import hookimpl

@hookimpl
def get_default_language() -> str:
    """Default language"""    
    return DEFAULT_LANGUAGE

@hookimpl
def get_default_locale() -> str:
    """Default locale"""
    return DEFAULT_LOCALE

@hookimpl
def get_default_dialect() -> str:
    """Default locale"""
    return DEFAULT_DIALECT

@hookimpl
def get_default_voice() -> str:
    """Default voice"""
    return DEFAULT_VOICE

@hookimpl
def get_default_timezone() -> str:
    """Default timezone"""
    return DEFAULT_TIMEZONE

@hookimpl
def get_default_country() -> str:
    """Default country"""
    return DEFAULT_COUNTRY

@hookimpl
def get_configuration() -> dict:
    """Get configuration"""
    return daconfig

@hookimpl
def get_hostname() -> str:
    """Get hostname"""
    return hostname

@hookimpl
def get_debug_status() -> bool:
    """Get debug status"""
    return DEBUG

@hookimpl
def get_default_table_class() -> str:
    """Get the default table CSS class"""
    return DEFAULT_TABLE_CLASS

@hookimpl
def get_default_thead_class() -> str:
    """Get the default thead CSS class"""
    return DEFAULT_THEAD_CLASS

@hookimpl
def get_twilio_config():
    """Return the twilio configuration"""
    return twilio_config

@hookimpl
def get_server_redis():
    return r

@hookimpl
def get_server_redis_user():
    return r_user

@hookimpl
def get_saved_file_object():
    return SavedFile

@hookimpl
def generate_csrf(secret_key, token_key):
    return base_generate_csrf(secret_key=secret_key, token_key=token_key)

@hookimpl
def get_button_class_prefix():
    return current_app.config['BUTTON_STYLE']
