#! /usr/bin/env python
import json
import sys
import random
import string
import requests

root = 'http://localhost'
key = 'H3PLMKJKIVATLDPWHJH3AGWEJPFU5GRT'
i = 'docassemble.demo:data/questions/questions.yml'
iterations = 100

while iterations:
    r = requests.get(root + '/api/session/new', params={'key': key, 'i': i})
    if r.status_code != 200:
        sys.exit(r.text)
    info = json.loads(r.text)
    session = info['session']
    secret = info['secret']

    r = requests.get(root + '/api/session/question', params={'key': key, 'i': i, 'secret': secret, 'session': session})
    if r.status_code != 200:
        sys.exit(r.text)
    info = json.loads(r.text)

    print(r.text)

    steps = 0
    while steps < 1000 and info['questionType'] not in ('deadend', 'restart', 'exit', 'leave'):
        variables = {}
        file_variables = {}
        file_uploads = {}
        for field in info.get('fields', []):
            if field.get('datatype', None) in ('html', 'note'):
                continue
            if 'variable_name' not in field:
                if field.get('fieldtype', None) == 'multiple_choice' and 'choices' in field:
                    indexno = random.choice(range(len(field['choices'])))
                    if info['questionText'] == 'What language do you speak?':
                        indexno = 0
                    variables[field['choices'][indexno]['variable_name']] = field['choices'][indexno]['value']
                else:
                    sys.exit("Field not recognized:\n" + repr(field))
            elif 'datatype' not in field and 'fieldtype' not in field and info['questionType'] != 'signature':
                variables[field['variable_name']] = True
            elif field.get('datatype', None) == 'object':
                if not field.get('required', True):
                    continue
                sys.exit("Field not recognized:\n" + repr(field))
            elif field.get('fieldtype', None) == 'multiple_choice' or 'choices' in field:
                indexno = random.choice(range(len(field['choices'])))
                if 'value' not in field['choices'][indexno]:
                    continue
                variables[field['variable_name']] = field['choices'][indexno]['value']
            elif field.get('datatype', None) == 'boolean':
                variables[field['variable_name']] = bool(random.random() > 0.5)
            elif field.get('datatype', None) == 'threestate':
                variables[field['variable_name']] = True if random.random() > 0.66 else (False if random.random() > 0.5 else None)
            elif field.get('datatype', None) in ('text', 'area'):
                variables[field['variable_name']] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
            elif field.get('datatype', None) == 'email':
                variables[field['variable_name']] = ''.join(random.choice(string.ascii_lowercase) for _ in range(5)) + '@' + ''.join(random.choice(string.ascii_lowercase) for _ in range(5)) + random.choice(['.com', '.net', '.org'])
            elif field.get('datatype', None) == 'currency':
                variables[field['variable_name']] = "{0:.2f}".format(random.random() * 100.0)
            elif field.get('datatype', None) == 'date':
                variables[field['variable_name']] = "2015-04-15"
            elif field.get('datatype', None) in ('file', 'files', 'camera', 'user', 'environment'):
                file_var_name = "file" + str(len(file_uploads))
                file_variables[file_var_name] = field['variable_name']
                file_uploads[file_var_name] = open("data/static/art.jpg", "rb")
            elif info['questionType'] == 'signature':
                file_var_name = "file" + str(len(file_uploads))
                file_variables[file_var_name] = field['variable_name']
                file_uploads[file_var_name] = open("data/static/canvas.png", "rb")
            elif field.get('datatype', None) == 'range':
                variables[field['variable_name']] = float(field.get('min', 1)) + int(random.random() * (float(field.get('max', 10)) - float(field.get('min', 1))))
            else:
                sys.exit("Field not recognized:\n" + repr(field))
        if 'question_variable_name' in info:
            variables[info['question_variable_name']] = True
        if len(variables) == 0 and len(file_variables) == 0:
            if 'fields' in info:
                sys.exit("Fields not recognized:\n" + repr(info['fields']))
            sys.exit("Question not recognized:\n" + repr(info))
        print("Session is " + session)
        if len(variables):
            print("Setting variables:\n" + repr(variables))
            data = {'key': key, 'i': i, 'secret': secret, 'session': session, 'variables': json.dumps(variables)}
        if len(file_variables):
            data = {'key': key, 'i': i, 'secret': secret, 'session': session}
        data['question_name'] = info['questionName']
        if 'event_list' in info:
            data['event_list'] = json.dumps(info['event_list'])
        if len(file_uploads):
            print("Setting file variables:\n" + repr(file_variables))
            data['file_variables'] = json.dumps(file_variables)
            r = requests.post(root + '/api/session', data=data, files=file_uploads)
        else:
            r = requests.post(root + '/api/session', data=data)
        if r.status_code != 200:
            sys.exit(r.text)
        print("Got question:\n" + r.text)
        try:
            info = json.loads(r.text)
            assert isinstance(info, dict)
        except:
            sys.exit(r.text)
        steps += 1

    # r = requests.delete(root + '/api/session', params={'key': key, 'i': i, 'session': session})
    # if r.status_code != 204:
    #     sys.exit(r.text)

    iterations -= 1

sys.exit(0)
