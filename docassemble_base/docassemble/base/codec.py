import codecs
import re


equals_byte = bytes('=', 'utf-8')

# functions
def myb64quote(text):
    return re.sub(r'[\n=]', '', codecs.encode(text.encode('utf-8'), 'base64').decode())


def myb64unquote(text):
    return codecs.decode(repad_byte(bytearray(text, encoding='utf-8')), 'base64').decode('utf-8')

def repad(text):
    return text + ('=' * ((4 - len(text) % 4) % 4))


def repad_byte(text):
    return text + (equals_byte * ((4 - len(text) % 4) % 4))

# parse

def myb64quote(text):
    """Single-quote-wrapped myb64quote"""
    return "'" + re.sub(r'[\n=]', '', codecs.encode(text.encode('utf8'), 'base64').decode()) + "'"


def safeid(text):
    """myb64quote"""
    return re.sub(r'[\n=]', '', codecs.encode(text.encode('utf8'), 'base64').decode())


def from_safeid(text):
    """myb64unquote"""
    return codecs.decode(repad(bytearray(text, encoding='utf-8')), 'base64').decode('utf8')


def repad(text):
    """repad_byte"""
    return text + (equals_byte * ((4 - len(text) % 4) % 4))

# standardformatter

def myb64doublequote(text):
    """Double-quote-wrapped myb64quote"""
    return '"' + re.sub(r'[\n=]', '', codecs.encode(text.encode('utf8'), 'base64').decode()) + '"'


def myb64quote(text):
    """Single-quote-wrapped myb64quote"""
    return "'" + re.sub(r'[\n=]', '', codecs.encode(text.encode('utf8'), 'base64').decode()) + "'"

def repad(text):
    """repad_byte"""
    return text + (equals_byte * ((4 - len(text) % 4) % 4))

def safeid(text):
    """my64quote"""
    return re.sub(r'[\n=]', '', codecs.encode(text.encode('utf8'), 'base64').decode())


def from_safeid(text):
    """my64unquote"""
    return codecs.decode(repad(bytearray(text, encoding='utf-8')), 'base64').decode('utf8')

# util

def myb64quote(text):
    """myb64quote"""
    return re.sub(r'[\n=]', '', codecs.encode(text.encode('utf8'), 'base64').decode())

def safeid(text):
    """myb64quote"""
    return re.sub(r'[\n=]', '', codecs.encode(text.encode('utf-8'), 'base64').decode())

# utils.helpers

def myb64unquote(the_string):
    return codecs.decode(repad(bytearray(the_string, encoding='utf-8')), 'base64').decode('utf-8')


def safeid(text):
    return re.sub(r'[\n=]', '', codecs.encode(text.encode('utf-8'), 'base64').decode())


def from_safeid(text):
    return codecs.decode(repad(bytearray(text, encoding='utf-8')), 'base64').decode('utf-8')


def repad(text):
    return text + (equals_byte * ((4 - len(text) % 4) % 4))
