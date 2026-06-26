from sqlalchemy import select, delete
from docassemble.webapp.extensions import db
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.main.models import Uploads
from docassemble.webapp.tts.models import SpeakList
from docassemble.webapp.utils.encryption import (
    decrypt_phrase,
    encrypt_phrase,
    pack_phrase,
    unpack_phrase,
)
from docassemble.webapp.utils.logger import logmessage

@hookimpl
def manage_tts_objects(mode, kwargs):
    if mode == 0:
        params = {'filename': kwargs['yaml_filename'], 'key': kwargs['user_code'], 'question': kwargs['interview_status'].question.number, 'digest': kwargs['the_hash'], 'type': kwargs['question_type'], 'language': kwargs['the_language'], 'dialect': kwargs['the_dialect']}
        if kwargs['the_voice']:
            params['voice'] = kwargs['the_voice']
        existing_entry = db.session.execute(select(SpeakList).filter_by(**params).with_for_update()).scalar()
        if existing_entry:
            if existing_entry.encrypted:
                existing_phrase = decrypt_phrase(existing_entry.phrase, kwargs['secret'])
            else:
                existing_phrase = unpack_phrase(existing_entry.phrase)
            if kwargs['phrase'] != existing_phrase:
                logmessage("index: the phrase changed; updating it")
                existing_entry.phrase = kwargs['the_phrase']
                existing_entry.upload = None
                existing_entry.encrypted = kwargs['encrypted']
        else:
            new_entry = SpeakList(filename=kwargs['yaml_filename'], key=kwargs['user_code'], phrase=kwargs['the_phrase'], question=kwargs['interview_status'].question.number, digest=kwargs['the_hash'], type=kwargs['question_type'], language=kwargs['the_language'], dialect=kwargs['the_dialect'], encrypted=kwargs['encrypted'], voice=kwargs['the_voice'])
            db.session.add(new_entry)
        db.session.commit()
    if mode == 1:
        files_to_delete = []
        user_code = kwargs['user_code']
        filename = kwargs['filename']
        for speaklist in db.session.execute(select(SpeakList).filter_by(key=user_code, filename=filename)).scalars():
            if speaklist.upload is not None:
                files_to_delete.append(speaklist.upload)
        db.session.execute(delete(SpeakList).filter_by(key=user_code, filename=filename))
        db.session.commit()
        for upload in db.session.execute(select(Uploads).filter_by(key=user_code, yamlfile=filename, persistent=False)).scalars():
            files_to_delete.append(upload.indexno)
        db.session.execute(delete(Uploads).filter_by(key=user_code, yamlfile=filename, persistent=False))
        db.session.commit()
    if mode == 2:
        user_code = kwargs['user_code']
        filename = kwargs['filename']
        secret = kwargs['secret']
        for record in db.session.execute(select(SpeakList).filter_by(key=user_code, filename=filename, encrypted=True).with_for_update()).scalars():
            phrase = decrypt_phrase(record.phrase, secret)
            record.phrase = pack_phrase(phrase)
            record.encrypted = False
        db.session.commit()
    if mode == 3:
        user_code = kwargs['user_code']
        filename = kwargs['filename']
        secret = kwargs['secret']
        for record in db.session.execute(select(SpeakList).filter_by(key=user_code, filename=filename, encrypted=False).with_for_update()).scalars():
            phrase = unpack_phrase(record.phrase)
            record.phrase = encrypt_phrase(phrase, secret)
            record.encrypted = True
        db.session.commit()
    if mode == 4:
        user_code = kwargs['user_code']
        filename = kwargs['filename']
        oldsecret = kwargs['oldsecret']
        newsecret = kwargs['newsecret']
        for record in db.session.execute(select(SpeakList).filter_by(key=user_code, filename=filename, encrypted=True).with_for_update()).scalars():
            try:
                phrase = decrypt_phrase(record.phrase, oldsecret)
                record.phrase = encrypt_phrase(phrase, newsecret)
            except:
                pass
        db.session.commit()
