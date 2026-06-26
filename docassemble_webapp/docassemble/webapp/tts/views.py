import subprocess
import os
from flask import Blueprint, request
from sqlalchemy import select, and_
from docassemble.webapp.config import (
    daconfig,
    audio_mimetype_table,
    voicerss_config,
    VOICERSS_ENABLED,
)
from docassemble.webapp.extensions import db
from docassemble.webapp.files.file_number import get_new_file_number
from docassemble.webapp.files.savedfile import SavedFile
from docassemble.webapp.sessions import get_session
from docassemble.webapp.utils.encryption import decrypt_phrase, unpack_phrase
from docassemble.webapp.utils.helpers import custom_send_file
from docassemble.webapp.utils.logger import logmessage
from .models import SpeakList

tts_bp = Blueprint(
    'tts',
    __name__
)

@tts_bp.route('/speakfile', methods=['GET'])
def speak_file():
    audio_file = None
    filename = request.args.get('i', None)
    if filename is None:
        return ('You must pass the filename (i) to read it out loud', 400)
    session_info = get_session(filename)
    if session_info is None:
        return ("You must include a session to read a screen out loud", 400)
    key = session_info['uid']
    # encrypted = session_info['encrypted']
    question = request.args.get('question', None)
    question_type = request.args.get('type', None)
    file_format = request.args.get('format', None)
    the_language = request.args.get('language', None)
    the_dialect = request.args.get('dialect', None)
    the_voice = request.args.get('voice', '')
    if the_voice == '':
        the_voice = None
    the_hash = request.args.get('digest', None)
    secret = request.cookies.get('secret', None)
    if secret is not None:
        secret = str(secret)
    if file_format not in ('mp3', 'ogg') or not (filename and key and question and question_type and file_format and the_language and the_dialect):
        logmessage("speak_file: could not serve speak file because invalid or missing data was provided: filename " + str(filename) + " and key " + str(key) + " and question number " + str(question) + " and question type " + str(question_type) + " and language " + str(the_language) + " and dialect " + str(the_dialect))
        return ('File not found', 404)
    params = {'filename': filename, 'key': key, 'question': question, 'digest': the_hash, 'type': question_type, 'language': the_language, 'dialect': the_dialect}
    if the_voice:
        params['voice'] = the_voice
    entry = db.session.execute(select(SpeakList).filter_by(**params)).scalar()
    if not entry:
        logmessage("speak_file: could not serve speak file because no entry could be found in speaklist for filename " + str(filename) + " and key " + str(key) + " and question number " + str(question) + " and question type " + str(question_type) + " and language " + str(the_language) + " and dialect " + str(the_dialect) + " and voice " + str(the_voice))
        return ('File not found', 404)
    if not entry.upload:
        existing_entry = db.session.execute(select(SpeakList).where(and_(SpeakList.phrase == entry.phrase, SpeakList.language == entry.language, SpeakList.dialect == entry.dialect, SpeakList.voice == entry.voice, SpeakList.upload != None, SpeakList.encrypted == entry.encrypted))).scalar()  # noqa: E711 # pylint: disable=singleton-comparison
        if existing_entry:
            logmessage("speak_file: found existing entry: " + str(existing_entry.id) + ".  Setting to " + str(existing_entry.upload))
            entry.upload = existing_entry.upload
        else:
            if not VOICERSS_ENABLED:
                logmessage("speak_file: could not serve speak file because voicerss not enabled")
                return ('File not found', 404)
            new_file_number = get_new_file_number(key, 'speak.mp3', filename)
            # phrase = codecs.decode(entry.phrase, 'base64')
            if entry.encrypted:
                phrase = decrypt_phrase(entry.phrase, secret)
            else:
                phrase = unpack_phrase(entry.phrase)
            url = voicerss_config.get('url', "https://api.voicerss.org/")
            # logmessage("Retrieving " + url)
            audio_file = SavedFile(new_file_number, extension='mp3', fix=True, should_not_exist=True)
            voicerss_parameters = {'f': voicerss_config.get('format', '16khz_16bit_stereo'), 'key': voicerss_config['key'], 'src': phrase, 'hl': str(entry.language) + '-' + str(entry.dialect)}
            if the_voice is not None:
                voicerss_parameters['v'] = the_voice
            audio_file.fetch_url_post(url, voicerss_parameters)
            if audio_file.size_in_bytes() > 100:
                call_array = [daconfig.get('pacpl', 'pacpl'), '-t', 'ogg', audio_file.path + '.mp3']
                logmessage("speak_file: calling " + " ".join(call_array))
                result = subprocess.run(call_array, check=False).returncode
                if result != 0:
                    logmessage("speak_file: failed to convert downloaded mp3 (" + audio_file.path + '.mp3' + ") to ogg")
                    return ('File not found', 404)
                entry.upload = new_file_number
                audio_file.finalize()
                db.session.commit()
            else:
                logmessage("speak_file: download from voicerss (" + url + ") failed")
                return ('File not found', 404)
    if not entry.upload:
        logmessage("speak_file: upload file number was not set")
        return ('File not found', 404)
    if not audio_file:
        audio_file = SavedFile(entry.upload, extension='mp3', fix=True)
    the_path = audio_file.path + '.' + file_format
    if not os.path.isfile(the_path):
        logmessage("speak_file: could not serve speak file because file (" + the_path + ") not found")
        return ('File not found', 404)
    response = custom_send_file(the_path, mimetype=audio_mimetype_table[file_format])
    return response
