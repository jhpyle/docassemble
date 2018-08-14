from docassemble.base.logger import logmessage

import re
import os
import pyPdf
import tempfile
import urllib
import urllib2
import mimetypes
from PIL import Image
import xml.etree.ElementTree as ET
import docassemble.base.functions
from docassemble.webapp.core.models import Uploads
from docassemble.webapp.files import SavedFile, get_ext_and_mimetype
from flask import session, has_request_context, url_for
from flask_login import current_user
from sqlalchemy import or_, and_
import docassemble.base.config

import docassemble.webapp.cloud
cloud = docassemble.webapp.cloud.get_cloud()

def url_if_exists(file_reference):
    parts = file_reference.split(":")
    if len(parts) == 2:
        if cloud:
            m = re.search(r'^docassemble.playground([0-9]+)$', parts[0])
            if m:
                user_id = m.group(1)
                if re.search(r'^data/sources/', parts[1]):
                    section = 'playgroundsources'
                    filename = re.sub(r'^data/sources/', '', parts[1])
                else:
                    section = 'playgroundstatic'
                    filename = re.sub(r'^data/static/', '', parts[1])
                filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', filename)
                key = str(section) + '/' + str(user_id) + '/' + filename
                cloud_key = cloud.get_key(key)
                if cloud_key.does_exist:
                    return cloud_key.generate_url(3600, display_filename=filename)
                return None
        the_path = docassemble.base.functions.static_filename_path(file_reference)
        if the_path is None or not os.path.isfile(the_path):
            return None
        return docassemble.base.config.daconfig.get('root', '/') + 'packagestatic/' + parts[0] + '/' + re.sub(r'^data/static/', '', parts[1])
    return None

def reference_exists(file_reference):
    if cloud:
        parts = file_reference.split(":")
        if len(parts) == 2:
            m = re.search(r'^docassemble.playground([0-9]+)$', parts[0])
            if m:
                user_id = m.group(1)
                if re.search(r'^data/sources/', parts[1]):
                    section = 'playgroundsources'
                    filename = re.sub(r'^data/sources/', '', parts[1])
                else:
                    section = 'playgroundstatic'
                    filename = re.sub(r'^data/static/', '', parts[1])
                filename = re.sub(r'[^A-Za-z0-9\-\_\. ]', '', filename)
                key = str(section) + '/' + str(user_id) + '/' + filename
                cloud_key = cloud.get_key(key)
                if cloud_key.does_exist:
                    return True
                return False
    the_path = docassemble.base.functions.static_filename_path(file_reference)
    if the_path is None or not os.path.isfile(the_path):
        #logmessage("Returning false")
        return False
    #logmessage("Returning true because path is " + str(the_path))
    return True

def get_info_from_file_reference(file_reference, **kwargs):
    #sys.stderr.write('file reference is ' + str(file_reference) + "\n")
    #logmessage('file reference is ' + str(file_reference))
    if 'convert' in kwargs:
        convert = kwargs['convert']
    else:
        convert = None
    if 'privileged' in kwargs:
        privileged = kwargs['privileged']
    else:
        privileged = None
    has_info = False
    if re.search(r'^[0-9]+$', str(file_reference)):
        if 'filename' in kwargs:
            result = get_info_from_file_number(int(file_reference), privileged=privileged, filename=kwargs['filename'])
        else:
            result = get_info_from_file_number(int(file_reference), privileged=privileged)
        if 'fullpath' not in result:
            result['fullpath'] = None
        has_info = True
    elif re.search(r'^https?://', str(file_reference)):
        #logmessage("get_info_from_file_reference: " + str(file_reference) + " is a URL")
        possible_filename = re.sub(r'.*/', '', file_reference)
        if possible_filename == '':
            possible_filename = 'index.html'
        if re.search(r'\.', possible_filename):
            (possible_ext, possible_mimetype) = get_ext_and_mimetype(possible_filename)
            #logmessage("get_info_from_file_reference: starting with " + str(possible_ext) + " and " + str(possible_mimetype))
        else:
            possible_ext = 'txt'
            possible_mimetype = 'text/plain'
        result = dict()
        temp_file = tempfile.NamedTemporaryFile(prefix="datemp", suffix='.' + possible_ext, delete=False)
        req = urllib2.Request(file_reference, headers={'User-Agent' : docassemble.base.config.daconfig.get('user agent', 'Python-urllib/2.7')})
        response = urllib2.urlopen(req)
        temp_file.write(response.read())
        #(local_filename, headers) = urllib.urlretrieve(file_reference)
        result['fullpath'] = temp_file.name
        try:
            #result['mimetype'] = headers.gettype()
            result['mimetype'] = response.headers['Content-Type']
            #logmessage("get_info_from_file_reference: mimetype is " + str(result['mimetype']))
        except Exception as errmess:
            logmessage("get_info_from_file_reference: could not get mimetype from headers")
            result['mimetype'] = possible_mimetype
            result['extension'] = possible_ext
        if 'extension' not in result:
            #logmessage("get_info_from_file_reference: extension not in result")
            result['extension'] = re.sub(r'^\.', '', mimetypes.guess_extension(result['mimetype']))
            #logmessage("get_info_from_file_reference: extension is " + str(result['extension']))
        if re.search(r'\.', possible_filename):
            result['filename'] = possible_filename
        else:
            result['filename'] = possible_filename + '.' + result['extension']
        path_parts = os.path.splitext(result['fullpath'])
        result['path'] = path_parts[0]
        has_info = True
        #logmessage("get_info_from_file_reference: downloaded to " + str(result['fullpath']))
    else:
        #logmessage(str(file_reference) + " is not a URL")
        result = dict()
        question = kwargs.get('question', None)
        folder = kwargs.get('folder', None)
        the_package = None
        parts = file_reference.split(':')
        if len(parts) == 1:
            the_package = None
            if question is not None:
                the_package = question.from_source.package
            if the_package is None:
                the_package = docassemble.base.functions.get_current_package()
            if folder is not None and not re.search(r'/', file_reference):
                file_reference = 'data/' + str(folder) + '/' + file_reference
            if the_package is not None:
                #logmessage("package is " + str(the_package))
                file_reference = the_package + ':' + file_reference
            else:
                #logmessage("package was null")
                file_reference = 'docassemble.base:' + file_reference
        result['fullpath'] = docassemble.base.functions.static_filename_path(file_reference)
    #logmessage("path is " + str(result['fullpath']))
    if result['fullpath'] is not None: #os.path.isfile(result['fullpath'])
        if not has_info:
            result['filename'] = os.path.basename(result['fullpath'])
            ext_type, result['mimetype'] = get_ext_and_mimetype(result['fullpath'])
            path_parts = os.path.splitext(result['fullpath'])
            result['path'] = path_parts[0]
            result['extension'] = path_parts[1].lower()
            result['extension'] = re.sub(r'\.', '', result['extension'])
        #logmessage("Extension is " + result['extension'])
        if convert is not None and result['extension'] in convert:
            #logmessage("Converting...")
            if os.path.isfile(result['path'] + '.' + convert[result['extension']]):
                #logmessage("Found conversion file ")
                result['extension'] = convert[result['extension']]
                result['fullpath'] = result['path'] + '.' + result['extension']
                ext_type, result['mimetype'] = get_ext_and_mimetype(result['fullpath'])
            else:
                logmessage("Did not find file " + result['path'] + '.' + convert[result['extension']])
                return dict()
        #logmessage("Full path is " + result['fullpath'])
        if os.path.isfile(result['fullpath']) and not has_info:
            add_info_about_file(result['fullpath'], result)
    else:
        logmessage("File reference " + str(file_reference) + " DID NOT EXIST.")
    return(result)

def add_info_about_file(filename, result):
    if result['extension'] == 'pdf':
        try:
            reader = pyPdf.PdfFileReader(open(filename))
            result['pages'] = reader.getNumPages()
        except:
            result['pages'] = 1
    elif result['extension'] in ['png', 'jpg', 'gif']:
        im = Image.open(filename)
        result['width'], result['height'] = im.size
    elif result['extension'] == 'svg':
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            viewBox = root.attrib.get('viewBox', None)
            if viewBox is not None:
                dimen = viewBox.split(' ')
                if len(dimen) == 4:
                    result['width'] = float(dimen[2]) - float(dimen[0])
                    result['height'] = float(dimen[3]) - float(dimen[1])
        except:
            raise Exception("problem reading " + str(filename))
            logmessage('add_info_about_file: could not read ' + str(filename))
    return

def get_info_from_file_number(file_number, privileged=False, filename=None):
    if current_user and current_user.is_authenticated and current_user.has_role('admin', 'developer', 'advocate', 'trainer'):
        privileged = True
    else:
        if has_request_context() and 'uid' in session:
            uid = session['uid']
        else:
            uid = docassemble.base.functions.get_uid()
    #logmessage("get_info_from_file_number: privileged is " + str(privileged) + " and uid is " + str(uid))
    result = dict()
    if privileged:
        upload = Uploads.query.filter_by(indexno=file_number).first()
    else:
        upload = Uploads.query.filter(and_(Uploads.indexno == file_number, or_(Uploads.key == uid, Uploads.private == False))).first()
    if upload:
        if filename is None:
            result['filename'] = upload.filename
        else:
            result['filename'] = filename
        result['extension'], result['mimetype'] = get_ext_and_mimetype(result['filename'])
        sf = SavedFile(file_number, extension=result['extension'], fix=True)
        result['path'] = sf.path
        result['fullpath'] = result['path'] + '.' + result['extension']
        result['private'] = upload.private
        result['persistent'] = upload.persistent
        #logmessage("fullpath is " + str(result['fullpath']))
    if 'path' not in result:
        logmessage("get_info_from_file_number: path is not in result for " + str(file_number))
        return result
    final_filename = result['path'] + '.' + result['extension']
    if os.path.isfile(final_filename):
        add_info_about_file(final_filename, result)
    # else:
    #     logmessage("Filename " + final_filename + "did not exist.")
    return(result)

