import mimetypes
import json
import pickle
import re
import tempfile
from urllib.parse import unquote as urllibunquote
import dateutil
import twilio
from flask import request, Response, Blueprint, session
from PIL import Image
from docassemble.base.error import DAException, DAError
from docassemble.base.generate_key import random_string
from docassemble.base.interview_cache import get_interview
from docassemble.base.language.control import set_language
from docassemble.base.language.words import word
from docassemble.base.parse import (
    InterviewStatus,
    ensure_object_exists,
    extension_of_doc_format,
)
from docassemble.base.standardformatter import as_sms, get_choices_with_abb
from docassemble.base.thread_context import global_context, this_thread, copy_of_globals
from docassemble.webapp.config import default_yaml_filename, DEBUG, DEFAULT_LANGUAGE
from docassemble.webapp.daredis import r
from docassemble.webapp.extensions import csrf, db
from docassemble.webapp.files.file_number import get_new_file_number
from docassemble.webapp.files.hooks import save_numbered_file
from docassemble.webapp.files.savedfile import SavedFile
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.utils.fixpickle import fix_pickle_obj
from docassemble.webapp.interview.common import get_unique_name
from docassemble.webapp.interview.helpers import (
    fetch_user_dict,
    fetch_previous_user_dict,
    encrypt_session,
    reset_user_dict,
    decrypt_session,
    save_user_dict,
)
from docassemble.webapp.interview.views import sub_indices
from docassemble.webapp.lock import release_lock, obtain_lock
from docassemble.webapp.sessions import update_session, session_context
from docassemble.webapp.twilio.helpers import twilio_config
from docassemble.webapp.users.models import TempUser
from docassemble.webapp.users.views import load_user
from docassemble.webapp.utils.helpers import process_file, myb64unquote, url_for
from docassemble.webapp.utils.logger import logmessage

sms_bp = Blueprint(
    'sms',
    __name__
)

@sms_bp.route("/sms", methods=['POST'])
@csrf.exempt
def sms():
    # logmessage("Received: " + str(request.form))
    form = request.form
    base_url = url_for('interview.rootindex', _external=True)
    url_root = base_url
    resp = do_sms(form, base_url, url_root)
    return Response(str(resp), mimetype='text/xml')


def do_sms(form, base_url, url_root, config='default', save=True):
    set_language(DEFAULT_LANGUAGE)
    resp = twilio.twiml.messaging_response.MessagingResponse()
    special_messages = []
    if twilio_config is None:
        logmessage("do_sms: ignoring message to sms because Twilio not enabled")
        return resp
    if "AccountSid" not in form or form["AccountSid"] not in twilio_config['account sid']:
        logmessage("do_sms: request to sms did not authenticate")
        return resp
    if "To" not in form:
        logmessage("do_sms: request to sms ignored because phone number not provided")
        return resp
    if form["To"].startswith('whatsapp:'):
        actual_number = re.sub(r'^whatsapp:', '', form["To"])
        if actual_number not in twilio_config['whatsapp number']:
            logmessage("do_sms: request to whatsapp ignored because recipient number " + str(form['To']) + " not in configuration")
            return resp
        tconfig = twilio_config['whatsapp number'][actual_number]
    else:
        if form["To"] not in twilio_config['number']:
            logmessage("do_sms: request to sms ignored because recipient number " + str(form['To']) + " not in configuration")
            return resp
        tconfig = twilio_config['number'][form["To"]]
    if 'sms' not in tconfig or tconfig['sms'] in (False, None, 0):
        logmessage("do_sms: ignoring message to sms because SMS not enabled")
        return resp
    if "From" not in form or not re.search(r'[0-9]', form["From"]):
        logmessage("do_sms: request to sms ignored because unable to determine caller ID")
        return resp
    if "Body" not in form:
        logmessage("do_sms: request to sms ignored because message had no content")
        return resp
    inp = form['Body'].strip()
    # logmessage("do_sms: received >" + inp + "<")
    key = 'da:sms:client:' + form["From"] + ':server:' + tconfig['number']
    action = None
    action_performed = False
    for try_num in (0, 1):  # pylint: disable=unused-variable
        sess_contents = r.get(key)
        if sess_contents is None:
            # logmessage("do_sms: received input '" + str(inp) + "' from new user")
            yaml_filename = tconfig.get('default interview', default_yaml_filename)
            if 'dispatch' in tconfig and isinstance(tconfig['dispatch'], dict):
                if inp.lower() in tconfig['dispatch']:
                    yaml_filename = tconfig['dispatch'][inp.lower()]
                    # logmessage("do_sms: using interview from dispatch: " + str(yaml_filename))
            if yaml_filename is None:
                # logmessage("do_sms: request to sms ignored because no interview could be determined")
                return resp
            if (not DEBUG) and (yaml_filename.startswith('docassemble.base') or yaml_filename.startswith('docassemble.demo')):
                raise DAException("do_sms: not authorized to run interviews in docassemble.base or docassemble.demo")
            secret = random_string(16)
            uid = get_unique_name(yaml_filename, secret)
            new_temp_user = TempUser()
            db.session.add(new_temp_user)
            db.session.commit()
            sess_info = {'yaml_filename': yaml_filename, 'uid': uid, 'secret': secret, 'number': form["From"], 'encrypted': True, 'tempuser': new_temp_user.id, 'user_id': None, 'session_uid': random_string(10)}
            r.set(key, pickle.dumps(sess_info))
            accepting_input = False
        else:
            try:
                sess_info = fix_pickle_obj(sess_contents)
            except:
                logmessage("do_sms: unable to decode session information")
                return resp
            accepting_input = True
        if 'session_uid' not in sess_info:
            sess_info['session_uid'] = random_string(10)
        if inp.lower() in (word('exit'), word('quit')):
            logmessage("do_sms: exiting")
            if save:
                reset_user_dict(sess_info['uid'], sess_info['yaml_filename'], temp_user_id=sess_info['tempuser'])
            r.delete(key)
            return resp
        user = None
        if sess_info['user_id'] is not None:
            user = load_user(sess_info['user_id'])
        if user is None:
            ci = {'user': {'is_anonymous': True, 'is_authenticated': False, 'email': None, 'theid': sess_info['tempuser'], 'the_user_id': 't' + str(sess_info['tempuser']), 'roles': ['user'], 'firstname': 'SMS', 'lastname': 'User', 'nickname': None, 'country': None, 'subdivisionfirst': None, 'subdivisionsecond': None, 'subdivisionthird': None, 'organization': None, 'timezone': None, 'location': None, 'session_uid': sess_info['session_uid'], 'device_id': form["From"]}, 'session': sess_info['uid'], 'secret': sess_info['secret'], 'yaml_filename': sess_info['yaml_filename'], 'interface': 'sms', 'url': base_url, 'url_root': url_root, 'encrypted': sess_info['encrypted'], 'headers': {}, 'clientip': None, 'method': None, 'skip': {}, 'sms_sender': form["From"]}
        else:
            ci = {'user': {'is_anonymous': False, 'is_authenticated': True, 'email': user.email, 'theid': user.id, 'the_user_id': user.id, 'roles': user.roles, 'firstname': user.first_name, 'lastname': user.last_name, 'nickname': user.nickname, 'country': user.country, 'subdivisionfirst': user.subdivisionfirst, 'subdivisionsecond': user.subdivisionsecond, 'subdivisionthird': user.subdivisionthird, 'organization': user.organization, 'timezone': user.timezone, 'location': None, 'session_uid': sess_info['session_uid'], 'device_id': form["From"]}, 'session': sess_info['uid'], 'secret': sess_info['secret'], 'yaml_filename': sess_info['yaml_filename'], 'interface': 'sms', 'url': base_url, 'url_root': url_root, 'encrypted': sess_info['encrypted'], 'headers': {}, 'clientip': None, 'method': None, 'skip': {}}
        if action is not None:
            logmessage("do_sms: setting action to " + str(action))
            ci.update(action)
        this_thread.current_info = ci
        obtain_lock(sess_info['uid'], sess_info['yaml_filename'])
        steps, user_dict, is_encrypted = fetch_user_dict(sess_info['uid'], sess_info['yaml_filename'], secret=sess_info['secret'])
        if user_dict is None:
            r.delete(key)
            continue
        break
    encrypted = sess_info['encrypted']
    while True:
        if user_dict.get('multi_user', False) is True and encrypted is True:
            encrypted = False
            update_session(sess_info['yaml_filename'], encrypted=encrypted, uid=sess_info['uid'])
            is_encrypted = encrypted
            r.set(key, pickle.dumps(sess_info))
            if save:
                decrypt_session(sess_info['secret'], user_code=sess_info['uid'], filename=sess_info['yaml_filename'])
        if user_dict.get('multi_user', False) is False and encrypted is False:
            encrypted = True
            update_session(sess_info['yaml_filename'], encrypted=encrypted, uid=sess_info['uid'])
            is_encrypted = encrypted
            r.set(key, pickle.dumps(sess_info))
            if save:
                encrypt_session(sess_info['secret'], user_code=sess_info['uid'], filename=sess_info['yaml_filename'])
        interview = get_interview(sess_info['yaml_filename'])
        if 'skip' not in user_dict['_internal']:
            user_dict['_internal']['skip'] = {}
        # if 'smsgather' in user_dict['_internal']:
        #     # logmessage("do_sms: need to gather smsgather " + user_dict['_internal']['smsgather'])
        #     sms_variable = user_dict['_internal']['smsgather']
        # else:
        #     sms_variable = None
        # if action is not None:
        #     action_manual = True
        # else:
        #     action_manual = False
        ci['encrypted'] = is_encrypted
        interview_status = InterviewStatus(current_info=ci)
        interview.assemble(user_dict, interview_status)
        logmessage("do_sms: back from assemble 1; had been seeking variable " + str(interview_status.sought))
        logmessage("do_sms: question is " + interview_status.question.name)
        if action is not None:
            logmessage('do_sms: question is now ' + interview_status.question.name + ' because action')
            sess_info['question'] = interview_status.question.name
            r.set(key, pickle.dumps(sess_info))
        elif 'question' in sess_info and sess_info['question'] != interview_status.question.name:
            if inp not in (word('?'), word('back'), word('question'), word('exit')):
                logmessage("do_sms: blanking the input because question changed from " + str(sess_info['question']) + " to " + str(interview_status.question.name))
                sess_info['question'] = interview_status.question.name
                inp = 'question'
                r.set(key, pickle.dumps(sess_info))

        # logmessage("do_sms: inp is " + inp.lower() + " and steps is " + str(steps) + " and can go back is " + str(interview_status.can_go_back))
        m = re.search(r'^(' + word('menu') + '|' + word('link') + ')([0-9]+)', inp.lower())
        if m:
            # logmessage("Got " + inp)
            arguments = {}
            selection_type = m.group(1)
            selection_number = int(m.group(2)) - 1
            links = []
            menu_items = []
            sms_info = as_sms(interview_status, user_dict, links=links, menu_items=menu_items)
            target_url = None
            if selection_type == word('menu') and selection_number < len(menu_items):
                (target_url, label) = menu_items[selection_number]  # pylint: disable=unused-variable
            if selection_type == word('link') and selection_number < len(links):
                (target_url, label) = links[selection_number]  # pylint: disable=unused-variable
            if target_url is not None:
                uri_params = re.sub(r'^[\?]*\?', r'', target_url)
                for statement in re.split(r'&', uri_params):
                    parts = re.split(r'=', statement)
                    arguments[parts[0]] = parts[1]
            if 'action' in arguments:
                # logmessage(myb64unquote(urllibunquote(arguments['action'])))
                action = json.loads(myb64unquote(urllibunquote(arguments['action'])))
                # logmessage("Action is " + str(action))
                action_performed = True
                accepting_input = False
                inp = ''
                continue
            break
        if inp.lower() == word('back'):
            if 'skip' in user_dict['_internal'] and len(user_dict['_internal']['skip']):
                max_entry = -1
                for the_entry in user_dict['_internal']['skip'].keys():
                    max_entry = max(max_entry, the_entry)
                if max_entry in user_dict['_internal']['skip']:
                    del user_dict['_internal']['skip'][max_entry]
                if 'command_cache' in user_dict['_internal'] and max_entry in user_dict['_internal']['command_cache']:
                    del user_dict['_internal']['command_cache'][max_entry]
                save_user_dict(sess_info['uid'], user_dict, sess_info['yaml_filename'], secret=sess_info['secret'], encrypt=encrypted, changed=False, steps=steps)
                accepting_input = False
                inp = ''
                continue
            if steps > 1 and interview_status.can_go_back:
                steps, user_dict, is_encrypted = fetch_previous_user_dict(sess_info['uid'], sess_info['yaml_filename'], secret=sess_info['secret'])
                ci['encrypted'] = is_encrypted
                if 'question' in sess_info:
                    del sess_info['question']
                    r.set(key, pickle.dumps(sess_info))
                accepting_input = False
                inp = ''
                continue
            break
        break
    false_list = [word('no'), word('n'), word('false'), word('f')]
    true_list = [word('yes'), word('y'), word('true'), word('t')]
    inp_lower = inp.lower()
    skip_it = False
    changed = False
    if accepting_input:
        if inp_lower == word('?'):
            sms_info = as_sms(interview_status, user_dict)
            message = ''
            if sms_info['help'] is None:
                message += word('Sorry, no help is available for this question.')
            else:
                message += sms_info['help']
            message += "\n" + word("To read the question again, type question.")
            resp.message(message)
            release_lock(sess_info['uid'], sess_info['yaml_filename'])
            return resp
        if inp_lower == word('question'):
            accepting_input = False
    user_entered_skip = bool(inp_lower == word('skip'))
    if accepting_input:
        saveas = None
        uses_util = False
        uncheck_others = False
        if len(interview_status.question.fields) > 0:
            question = interview_status.question
            if question.question_type == "fields":
                field = None
                next_field = None
                for the_field in interview_status.get_field_list():
                    if hasattr(the_field, 'datatype') and the_field.datatype in ('html', 'note', 'script', 'css'):
                        continue
                    if interview_status.is_empty_mc(the_field):
                        continue
                    if the_field.number in user_dict['_internal']['skip']:
                        continue
                    if field is None:
                        field = the_field
                    elif next_field is None:
                        next_field = the_field
                    else:
                        break
                if field is None:
                    logmessage("do_sms: unclear what field is necessary!")
                    # if 'smsgather' in user_dict['_internal']:
                    #     del user_dict['_internal']['smsgather']
                    field = interview_status.question.fields[0]
                    next_field = None
                saveas = myb64unquote(field.saveas)
            else:
                if hasattr(interview_status.question.fields[0], 'saveas'):
                    saveas = myb64unquote(interview_status.question.fields[0].saveas)
                    logmessage("do_sms: variable to set is " + str(saveas))
                else:
                    saveas = None
                field = interview_status.question.fields[0]
                next_field = None
            if question.question_type == "settrue":
                if inp_lower == word('ok'):
                    data = 'True'
                else:
                    data = None
            elif question.question_type == 'signature':
                filename = 'canvas.png'
                extension = 'png'
                mimetype = 'image/png'
                temp_image_file = tempfile.NamedTemporaryFile(suffix='.' + extension)
                image = Image.new("RGBA", (200, 50))
                image.save(temp_image_file.name, 'PNG')
                (file_number, extension, mimetype) = save_numbered_file(filename, temp_image_file.name, yaml_file_name=sess_info['yaml_filename'], uid=sess_info['uid'])
                saveas_tr = sub_indices(saveas, user_dict)
                if inp_lower == word('x'):
                    the_string = saveas + " = docassemble.base.util.DAFile('" + saveas_tr + "', filename='" + str(filename) + "', number=" + str(file_number) + ", mimetype='" + str(mimetype) + "', extension='" + str(extension) + "')"
                    try:
                        exec('import docassemble.base.util', user_dict)
                        exec(the_string, user_dict)
                        if not changed:
                            steps += 1
                            user_dict['_internal']['steps'] = steps
                            changed = True
                    except BaseException as err_mess:
                        logmessage("do_sms: error: " + str(err_mess))
                        special_messages.append(word("Error") + ": " + str(err_mess))
                    skip_it = True
                    data = repr('')
                else:
                    data = None
            elif hasattr(field, 'datatype') and field.datatype in ("ml", "mlarea"):
                try:
                    exec("import docassemble.base.util", user_dict)
                except BaseException as err_mess:
                    special_messages.append("Error: " + str(err_mess))
                if 'ml_train' in interview_status.extras and field.number in interview_status.extras['ml_train']:
                    if not interview_status.extras['ml_train'][field.number]:
                        use_for_training = 'False'
                    else:
                        use_for_training = 'True'
                else:
                    use_for_training = 'True'
                if 'ml_group' in interview_status.extras and field.number in interview_status.extras['ml_group']:
                    data = 'docassemble.base.util.DAModel(' + repr(saveas) + ', group_id=' + repr(interview_status.extras['ml_group'][field.number]) + ', text=' + repr(inp) + ', store=' + repr(interview.get_ml_store()) + ', use_for_training=' + use_for_training + ')'
                else:
                    data = 'docassemble.base.util.DAModel(' + repr(saveas) + ', text=' + repr(inp) + ', store=' + repr(interview.get_ml_store()) + ', use_for_training=' + use_for_training + ')'
            elif hasattr(field, 'datatype') and field.datatype in ("file", "files", "camera", "user", "environment", "camcorder", "microphone"):
                if user_entered_skip and not interview_status.extras['required'][field.number]:
                    skip_it = True
                    data = repr('')
                elif user_entered_skip:
                    data = None
                    special_messages.append(word("You must attach a file."))
                else:
                    files_to_process = []
                    num_media = int(form.get('NumMedia', '0'))
                    fileindex = 0
                    while True:
                        if field.datatype == "file" and fileindex > 0:
                            break
                        if fileindex >= num_media or 'MediaUrl' + str(fileindex) not in form:
                            break
                        # logmessage("mime type is" + form.get('MediaContentType' + str(fileindex), 'Unknown'))
                        mimetype = form.get('MediaContentType' + str(fileindex), 'image/jpeg')
                        extension = re.sub(r'\.', r'', mimetypes.guess_extension(mimetype))
                        if extension == 'jpe':
                            extension = 'jpg'
                        # original_extension = extension
                        # if extension == 'gif':
                        #     extension == 'png'
                        #     mimetype = 'image/png'
                        filename = 'file' + '.' + extension
                        file_number = get_new_file_number(sess_info['uid'], filename, sess_info['yaml_filename'])
                        saved_file = SavedFile(file_number, extension=extension, fix=True, should_not_exist=True)
                        the_url = form['MediaUrl' + str(fileindex)]
                        # logmessage("Fetching from >" + the_url + "<")
                        saved_file.fetch_url(the_url)
                        process_file(saved_file, saved_file.path, mimetype, extension)
                        files_to_process.append((filename, file_number, mimetype, extension))
                        fileindex += 1
                    if len(files_to_process) > 0:
                        elements = []
                        indexno = 0
                        saveas_tr = sub_indices(saveas, user_dict)
                        for (filename, file_number, mimetype, extension) in files_to_process:
                            elements.append("docassemble.base.util.DAFile(" + repr(saveas_tr + "[" + str(indexno) + "]") + ", filename=" + repr(filename) + ", number=" + str(file_number) + ", mimetype=" + repr(mimetype) + ", extension=" + repr(extension) + ")")
                            indexno += 1
                        the_string = saveas + " = docassemble.base.util.DAFileList(" + repr(saveas_tr) + ", elements=[" + ", ".join(elements) + "])"
                        try:
                            exec('import docassemble.base.util', user_dict)
                            exec(the_string, user_dict)
                            if not changed:
                                steps += 1
                                user_dict['_internal']['steps'] = steps
                                changed = True
                        except BaseException as err_mess:
                            logmessage("do_sms: error: " + str(err_mess))
                            special_messages.append(word("Error") + ": " + str(err_mess))
                        skip_it = True
                        data = repr('')
                    else:
                        data = None
                        if interview_status.extras['required'][field.number]:
                            special_messages.append(word("You must attach a file."))
            elif question.question_type == "yesno" or (hasattr(field, 'datatype') and (hasattr(field, 'datatype') and field.datatype == 'boolean' and (hasattr(field, 'sign') and field.sign > 0))):
                if inp_lower in true_list:
                    data = 'True'
                    if question.question_type == "fields" and hasattr(field, 'uncheckothers') and field.uncheckothers is not False:
                        uncheck_others = field
                elif inp_lower in false_list:
                    data = 'False'
                else:
                    data = None
            elif question.question_type == "yesnomaybe" or (hasattr(field, 'datatype') and (field.datatype == 'threestate' and (hasattr(field, 'sign') and field.sign > 0))):
                if inp_lower in true_list:
                    data = 'True'
                    if question.question_type == "fields" and hasattr(field, 'uncheckothers') and field.uncheckothers is not False:
                        uncheck_others = field
                elif inp_lower in false_list:
                    data = 'False'
                else:
                    data = 'None'
            elif question.question_type == "noyes" or (hasattr(field, 'datatype') and (field.datatype in ('noyes', 'noyeswide') or (field.datatype == 'boolean' and (hasattr(field, 'sign') and field.sign < 0)))):
                if inp_lower in true_list:
                    data = 'False'
                elif inp_lower in false_list:
                    data = 'True'
                    if question.question_type == "fields" and hasattr(field, 'uncheckothers') and field.uncheckothers is not False:
                        uncheck_others = field
                else:
                    data = None
            elif question.question_type in ('noyesmaybe', 'noyesmaybe', 'noyeswidemaybe') or (hasattr(field, 'datatype') and field.datatype == 'threestate' and (hasattr(field, 'sign') and field.sign < 0)):
                if inp_lower in true_list:
                    data = 'False'
                elif inp_lower in false_list:
                    data = 'True'
                    if question.question_type == "fields" and hasattr(field, 'uncheckothers') and field.uncheckothers is not False:
                        uncheck_others = field
                else:
                    data = 'None'
            elif question.question_type == 'multiple_choice' or hasattr(field, 'choicetype') or (hasattr(field, 'datatype') and field.datatype in ('object', 'object_radio', 'multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes')) or (hasattr(field, 'inputtype') and field.inputtype == 'radio'):
                cdata, choice_list = get_choices_with_abb(interview_status, field, user_dict)
                data = None
                if hasattr(field, 'datatype') and field.datatype in ('multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes') and saveas is not None:
                    if 'command_cache' not in user_dict['_internal']:
                        user_dict['_internal']['command_cache'] = {}
                    if field.number not in user_dict['_internal']['command_cache']:
                        user_dict['_internal']['command_cache'][field.number] = []
                    ensure_object_exists(sub_indices(saveas, user_dict), field.datatype, user_dict, commands=user_dict['_internal']['command_cache'][field.number])
                    saveas = saveas + '.gathered'
                    data = 'True'
                if (user_entered_skip or (inp_lower == word('none') and hasattr(field, 'datatype') and field.datatype in ('multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes'))) and ((hasattr(field, 'disableothers') and field.disableothers) or (hasattr(field, 'datatype') and field.datatype in ('multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes')) or not (interview_status.extras['required'][field.number] or (question.question_type == 'multiple_choice' and hasattr(field, 'saveas')))):
                    logmessage("do_sms: skip accepted")
                    # user typed 'skip,' or, where checkboxes, 'none.'  Also:
                    # field is skippable, either because it has disableothers, or it is a checkbox field, or
                    # it is not required.  Multiple choice fields with saveas are considered required.
                    if hasattr(field, 'datatype'):
                        if field.datatype in ('object', 'object_radio'):
                            skip_it = True
                            data = repr('')
                        if field.datatype in ('multiselect', 'object_multiselect', 'checkboxes', 'object_checkboxes'):
                            for choice in choice_list:
                                if choice[1] is None:
                                    continue
                                user_dict['_internal']['command_cache'][field.number].append(choice[1] + ' = False')
                        elif (question.question_type == 'multiple_choice' and hasattr(field, 'saveas')) or hasattr(field, 'choicetype'):
                            if user_entered_skip:
                                skip_it = True
                                data = repr('')
                            else:
                                logmessage("do_sms: setting skip_it to True")
                                skip_it = True
                                data = repr('')
                        elif field.datatype == 'integer':
                            data = '0'
                        elif field.datatype in ('number', 'float', 'currency', 'range'):
                            data = '0.0'
                        else:
                            data = repr('')
                    else:
                        data = repr('')
                else:
                    # There is a real value here
                    if hasattr(field, 'datatype') and field.datatype in ('object_multiselect', 'object_checkboxes'):
                        true_values = set()
                        for selection in re.split(r' *[,;] *', inp_lower):
                            for potential_abb, value in cdata['abblower'].items():
                                if selection and selection.startswith(potential_abb):
                                    for choice in choice_list:
                                        if value == choice[0]:
                                            true_values.add(choice[2])
                        the_saveas = myb64unquote(field.saveas)
                        logmessage("do_sms: the_saveas is " + repr(the_saveas))
                        for choice in choice_list:
                            if choice[2] is None:
                                continue
                            if choice[2] in true_values:
                                logmessage("do_sms: " + choice[2] + " is in true_values")
                                the_string = 'if ' + choice[2] + ' not in ' + the_saveas + '.elements:\n    ' + the_saveas + '.append(' + choice[2] + ')'
                            else:
                                the_string = 'if ' + choice[2] + ' in ' + the_saveas + '.elements:\n    ' + the_saveas + '.remove(' + choice[2] + ')'
                            user_dict['_internal']['command_cache'][field.number].append(the_string)
                    elif hasattr(field, 'datatype') and field.datatype in ('multiselect', 'checkboxes'):
                        true_values = set()
                        for selection in re.split(r' *[,;] *', inp_lower):
                            for potential_abb, value in cdata['abblower'].items():
                                if selection and selection.startswith(potential_abb):
                                    for choice in choice_list:
                                        if value == choice[0]:
                                            true_values.add(choice[1])
                        for choice in choice_list:
                            if choice[1] is None:
                                continue
                            if choice[1] in true_values:
                                the_string = choice[1] + ' = True'
                            else:
                                the_string = choice[1] + ' = False'
                            user_dict['_internal']['command_cache'][field.number].append(the_string)
                    else:
                        # regular multiple choice
                        # logmessage("do_sms: user selected " + inp_lower + " and data is " + str(cdata))
                        for potential_abb, value in cdata['abblower'].items():
                            if inp_lower.startswith(potential_abb):
                                # logmessage("do_sms: user selected " + value)
                                for choice in choice_list:
                                    # logmessage("do_sms: considering " + choice[0])
                                    if value == choice[0]:
                                        # logmessage("do_sms: found a match")
                                        saveas = choice[1]
                                        if hasattr(field, 'datatype') and field.datatype in ('object', 'object_radio'):
                                            data = choice[2]
                                        else:
                                            data = repr(choice[2])
                                        break
                                break
            elif hasattr(field, 'datatype') and field.datatype == 'integer':
                if user_entered_skip and not interview_status.extras['required'][field.number]:
                    data = repr('')
                    skip_it = True
                else:
                    data = re.sub(r'[^0-9\.\-]', '', inp)
                    try:
                        the_value = eval("int(" + repr(data) + ")")
                        data = "int(" + repr(data) + ")"
                    except:
                        special_messages.append('"' + inp + '" ' + word("is not a whole number."))
                        data = None
            elif hasattr(field, 'datatype') and field.datatype in ('date', 'datetime'):
                if user_entered_skip and not interview_status.extras['required'][field.number]:
                    data = repr('')
                    skip_it = True
                else:
                    try:
                        dateutil.parser.parse(inp)
                        data = "docassemble.base.util.as_datetime(" + repr(inp) + ")"
                        uses_util = True
                    except BaseException as the_err:
                        logmessage("do_sms: date validation error was " + str(the_err))
                        if field.datatype == 'date':
                            special_messages.append('"' + inp + '" ' + word("is not a valid date."))
                        else:
                            special_messages.append('"' + inp + '" ' + word("is not a valid date and time."))
                        data = None
            elif hasattr(field, 'datatype') and field.datatype == 'time':
                if user_entered_skip and not interview_status.extras['required'][field.number]:
                    data = repr('')
                    skip_it = True
                else:
                    try:
                        dateutil.parser.parse(inp)
                        data = "docassemble.base.util.as_datetime(" + repr(inp) + ").time()"
                        uses_util = True
                    except BaseException as the_err:
                        logmessage("do_sms: time validation error was " + str(the_err))
                        special_messages.append('"' + inp + '" ' + word("is not a valid time."))
                        data = None
            elif hasattr(field, 'datatype') and field.datatype == 'range':
                if user_entered_skip and not interview_status.extras['required'][field.number]:
                    data = repr('')
                    skip_it = True
                else:
                    data = re.sub(r'[^0-9\-\.]', '', inp)
                    try:
                        the_value = eval("float(" + repr(data) + ")", user_dict)
                        if the_value > int(interview_status.extras['max'][field.number]) or the_value < int(interview_status.extras['min'][field.number]):
                            special_messages.append('"' + inp + '" ' + word("is not within the range."))
                            data = None
                    except:
                        data = None
            elif hasattr(field, 'datatype') and field.datatype in ('number', 'float', 'currency'):
                if user_entered_skip and not interview_status.extras['required'][field.number]:
                    data = '0.0'
                    skip_it = True
                else:
                    data = re.sub(r'[^0-9\.\-]', '', inp)
                    try:
                        the_value = eval("float(" + json.dumps(data) + ")", user_dict)
                        data = "float(" + json.dumps(data) + ")"
                    except:
                        special_messages.append('"' + inp + '" ' + word("is not a valid number."))
                        data = None
            else:
                if user_entered_skip:
                    if interview_status.extras['required'][field.number]:
                        data = repr(inp)
                    else:
                        data = repr('')
                        skip_it = True
                else:
                    data = repr(inp)
        else:
            data = None
        if data is None:
            logmessage("do_sms: could not process input: " + inp)
            special_messages.append(word("I do not understand what you mean by") + ' "' + inp + '."')
        else:
            if uses_util:
                exec("import docassemble.base.util", user_dict)
            if uncheck_others:
                for other_field in interview_status.get_field_list():
                    if hasattr(other_field, 'datatype') and other_field.datatype == 'boolean' and other_field is not uncheck_others and 'command_cache' in user_dict['_internal'] and other_field.number in user_dict['_internal']['command_cache']:
                        for command_index in range(len(user_dict['_internal']['command_cache'][other_field.number])):
                            if other_field.sign > 0:
                                user_dict['_internal']['command_cache'][other_field.number][command_index] = re.sub(r'= True$', '= False', user_dict['_internal']['command_cache'][other_field.number][command_index])
                            else:
                                user_dict['_internal']['command_cache'][other_field.number][command_index] = re.sub(r'= False$', '= True', user_dict['_internal']['command_cache'][other_field.number][command_index])
            the_string = saveas + ' = ' + data
            try:
                if not skip_it:
                    if hasattr(field, 'disableothers') and field.disableothers and hasattr(field, 'saveas'):
                        logmessage("do_sms: disabling others")
                        next_field = None
                    if next_field is not None:
                        if 'command_cache' not in user_dict['_internal']:
                            user_dict['_internal']['command_cache'] = {}
                        if field.number not in user_dict['_internal']['command_cache']:
                            user_dict['_internal']['command_cache'][field.number] = []
                        user_dict['_internal']['command_cache'][field.number].append(the_string)
                        logmessage("do_sms: storing in command cache: " + str(the_string))
                    else:
                        for the_field in interview_status.get_field_list():
                            if interview_status.is_empty_mc(the_field):
                                logmessage("do_sms: a field is empty")
                                the_saveas = myb64unquote(the_field.saveas)
                                if 'command_cache' not in user_dict['_internal']:
                                    user_dict['_internal']['command_cache'] = {}
                                if the_field.number not in user_dict['_internal']['command_cache']:
                                    user_dict['_internal']['command_cache'][the_field.number] = []
                                if hasattr(the_field, 'datatype'):
                                    if the_field.datatype in ('object_multiselect', 'object_checkboxes'):
                                        ensure_object_exists(sub_indices(the_saveas, user_dict), the_field.datatype, user_dict, commands=user_dict['_internal']['command_cache'][the_field.number])
                                        user_dict['_internal']['command_cache'][the_field.number].append(the_saveas + '.clear()')
                                        user_dict['_internal']['command_cache'][the_field.number].append(the_saveas + '.gathered = True')
                                    elif the_field.datatype in ('object', 'object_radio'):
                                        try:
                                            eval(the_saveas, user_dict)
                                        except:
                                            user_dict['_internal']['command_cache'][the_field.number].append(the_saveas + ' = None')
                                    elif the_field.datatype in ('multiselect', 'checkboxes'):
                                        ensure_object_exists(sub_indices(the_saveas, user_dict), the_field.datatype, user_dict, commands=user_dict['_internal']['command_cache'][the_field.number])
                                        user_dict['_internal']['command_cache'][the_field.number].append(the_saveas + '.gathered = True')
                                    else:
                                        user_dict['_internal']['command_cache'][the_field.number].append(the_saveas + ' = None')
                                else:
                                    user_dict['_internal']['command_cache'][the_field.number].append(the_saveas + ' = None')
                        if 'command_cache' in user_dict['_internal']:
                            for field_num in sorted(user_dict['_internal']['command_cache'].keys()):
                                for pre_string in user_dict['_internal']['command_cache'][field_num]:
                                    logmessage("do_sms: doing command cache: " + pre_string)
                                    exec(pre_string, user_dict)
                        logmessage("do_sms: doing regular: " + the_string)
                        exec(the_string, user_dict)
                        if not changed:
                            steps += 1
                            user_dict['_internal']['steps'] = steps
                            changed = True
                if next_field is None:
                    if skip_it:
                        # Run the commands that we have been storing up
                        if 'command_cache' in user_dict['_internal']:
                            for field_num in sorted(user_dict['_internal']['command_cache'].keys()):
                                for pre_string in user_dict['_internal']['command_cache'][field_num]:
                                    logmessage("do_sms: doing command cache: " + pre_string)
                                    exec(pre_string, user_dict)
                            if not changed:
                                steps += 1
                                user_dict['_internal']['steps'] = steps
                                changed = True
                    logmessage("do_sms: next_field is None")
                    if 'skip' in user_dict['_internal']:
                        user_dict['_internal']['skip'].clear()
                    if 'command_cache' in user_dict['_internal']:
                        user_dict['_internal']['command_cache'].clear()
                    # if 'sms_variable' in interview_status.current_info:
                    #     del interview_status.current_info['sms_variable']
                else:
                    logmessage("do_sms: next_field is not None")
                    user_dict['_internal']['skip'][field.number] = True
                    # user_dict['_internal']['smsgather'] = interview_status.sought
                # if 'smsgather' in user_dict['_internal'] and user_dict['_internal']['smsgather'] == saveas:
                #     # logmessage("do_sms: deleting " + user_dict['_internal']['smsgather'])
                #     del user_dict['_internal']['smsgather']
            except BaseException as the_err:
                logmessage("do_sms: failure to set variable with " + the_string)
                logmessage("do_sms: error was " + str(the_err))
                release_lock(sess_info['uid'], sess_info['yaml_filename'])
                # if 'uid' in session:
                #    del session['uid']
                return resp
        if changed and next_field is None and question.name not in user_dict['_internal']['answers']:
            logmessage("do_sms: setting internal answers for " + str(question.name))
            question.mark_as_answered(user_dict)
        interview.assemble(user_dict, interview_status)
        logmessage("do_sms: back from assemble 2; had been seeking variable " + str(interview_status.sought))
        logmessage("do_sms: question is now " + str(interview_status.question.name))
        sess_info['question'] = interview_status.question.name
        r.set(key, pickle.dumps(sess_info))
    else:
        logmessage("do_sms: not accepting input.")
    if interview_status.question.question_type in ("restart", "exit", "logout", "exit_logout", "new_session"):
        logmessage("do_sms: exiting because of restart or exit")
        if save:
            obtain_lock(sess_info['uid'], sess_info['yaml_filename'])
            reset_user_dict(sess_info['uid'], sess_info['yaml_filename'], temp_user_id=sess_info['tempuser'])
            release_lock(sess_info['uid'], sess_info['yaml_filename'])
        r.delete(key)
        if interview_status.question.question_type in ('restart', 'new_session'):
            sess_info = {'yaml_filename': sess_info['yaml_filename'], 'uid': get_unique_name(sess_info['yaml_filename'], sess_info['secret']), 'secret': sess_info['secret'], 'number': form["From"], 'encrypted': True, 'tempuser': sess_info['tempuser'], 'user_id': None}
            r.set(key, pickle.dumps(sess_info))
            form = {'To': form['To'], 'From': form['From'], 'AccountSid': form['AccountSid'], 'Body': word('question')}
            return do_sms(form, base_url, url_root, config=config, save=True)
    else:
        if not interview_status.can_go_back:
            user_dict['_internal']['steps_offset'] = steps
        # I had commented this out in do_sms(), but not in index()
        # user_dict['_internal']['answers'] = {}
        # Why do this?
        if (not interview_status.followed_mc) and len(user_dict['_internal']['answers']):
            user_dict['_internal']['answers'].clear()
        # if interview_status.question.name and interview_status.question.name in user_dict['_internal']['answers']:
        #     del user_dict['_internal']['answers'][interview_status.question.name]
        # logmessage("do_sms: " + as_sms(interview_status, user_dict))
        # twilio_client = TwilioRestClient(tconfig['account sid'], tconfig['auth token'])
        # message = twilio_client.messages.create(to=form["From"], from_=form["To"], body=as_sms(interview_status, user_dict))
        logmessage("do_sms: calling as_sms")
        sms_info = as_sms(interview_status, user_dict)
        qoutput = sms_info['question']
        if sms_info['next'] is not None:
            logmessage("do_sms: next variable is " + sms_info['next'])
            if interview_status.sought is None:
                logmessage("do_sms: sought variable is None")
            # user_dict['_internal']['smsgather'] = interview_status.sought
        if (accepting_input or changed or action_performed or sms_info['next'] is not None) and save:
            save_user_dict(sess_info['uid'], user_dict, sess_info['yaml_filename'], secret=sess_info['secret'], encrypt=encrypted, changed=changed, steps=steps)
        for special_message in special_messages:
            qoutput = re.sub(r'XXXXMESSAGE_AREAXXXX', "\n" + special_message + 'XXXXMESSAGE_AREAXXXX', qoutput)
        qoutput = re.sub(r'XXXXMESSAGE_AREAXXXX', '', qoutput)
        if user_dict.get('multi_user', False) is True and encrypted is True:
            encrypted = False
            update_session(sess_info['yaml_filename'], encrypted=encrypted, uid=sess_info['uid'])
            is_encrypted = encrypted
            r.set(key, pickle.dumps(sess_info))
            if save:
                decrypt_session(sess_info['secret'], user_code=sess_info['uid'], filename=sess_info['yaml_filename'])
        if user_dict.get('multi_user', False) is False and encrypted is False:
            encrypted = True
            update_session(sess_info['yaml_filename'], encrypted=encrypted, uid=sess_info['uid'])
            is_encrypted = encrypted
            r.set(key, pickle.dumps(sess_info))
            if save:
                encrypt_session(sess_info['secret'], user_code=sess_info['uid'], filename=sess_info['yaml_filename'])
        if len(interview_status.attachments) > 0:
            if tconfig.get("mms attachments", True):
                with resp.message(qoutput) as m:
                    media_count = 0
                    for attachment in interview_status.attachments:
                        if media_count >= 9:
                            break
                        for doc_format in attachment['formats_to_use']:
                            if media_count >= 9:
                                break
                            if doc_format != 'pdf':
                                continue
                            url = url_for('files.serve_stored_file', _external=True, uid=sess_info['uid'], number=attachment['file'][doc_format], filename=attachment['filename'], extension=extension_of_doc_format.get(doc_format, doc_format))
                            m.media(url)
                            media_count += 1
            else:
                for attachment in interview_status.attachments:
                    for doc_format in attachment['formats_to_use']:
                        if doc_format not in ('pdf', 'rtf', 'docx'):
                            continue
                        qoutput += "\n" + url_for('files.serve_stored_file', _external=True, uid=sess_info['uid'], number=attachment['file'][doc_format], filename=attachment['filename'], extension=extension_of_doc_format.get(doc_format, doc_format))
                resp.message(qoutput)
        else:
            resp.message(qoutput)
    release_lock(sess_info['uid'], sess_info['yaml_filename'])
    return resp


@hookimpl

def sms_body(phone_number, body, config):
    if twilio_config is None:
        raise DAError("sms_body: Twilio not enabled")
    if config not in twilio_config['name']:
        raise DAError("sms_body: specified config value, " + str(config) + ", not in Twilio configuration")
    tconfig = twilio_config['name'][config]
    if 'sms' not in tconfig or tconfig['sms'] in (False, None, 0):
        raise DAError("sms_body: sms feature is not enabled in Twilio configuration")
    if 'account sid' not in tconfig:
        raise DAError("sms_body: account sid not in Twilio configuration")
    if 'number' not in tconfig:
        raise DAError("sms_body: phone number not in Twilio configuration")
    if 'doing_sms' in session:
        raise DAError("Cannot call sms_body from within sms_body")
    form = {'To': tconfig['number'], 'From': phone_number, 'Body': body, 'AccountSid': tconfig['account sid']}
    base_url = url_for('interview.rootindex', _external=True)
    url_root = base_url
    with global_context(copy_of_globals(this_thread)), session_context():
        session['doing_sms'] = True
        resp = do_sms(form, base_url, url_root, save=False)
    if resp is None or len(resp.verbs) == 0 or len(resp.verbs[0].verbs) == 0:
        return None
    return resp.verbs[0].verbs[0].body
