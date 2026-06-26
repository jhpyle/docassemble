import math
import re
import tempfile
import os
import zipfile
import hashlib
import xml.etree.ElementTree as ET
import xlsxwriter
from flask import request, redirect, flash, Blueprint
from docassemble_flask_user import login_required, roles_required
from docassemble.base.error import DAError
from docassemble.base.functions import package_data_filename, space_to_underscore
from docassemble.base.interview_source import interview_source_from_string
from docassemble.base.language.words import word
from docassemble.base.parse import Interview
from docassemble.webapp.config import DEFAULT_LANGUAGE
from docassemble.webapp.develop.forms import Utilities
from docassemble.webapp.translations import setup_translation
from docassemble.webapp.utils.helpers import custom_send_file, url_for, mako_parts

translation_bp = Blueprint(
    'translation',
    __name__
)

@translation_bp.route('/translation_file', methods=['POST'])
@login_required
@roles_required(['admin', 'developer'])
def translation_file():
    setup_translation()
    form = Utilities(request.form)
    yaml_filename = form.interview.data
    if yaml_filename is None or not re.search(r'\S', yaml_filename):
        flash(word("You must provide an interview filename"), 'error')
        return redirect(url_for('develop.utilities'))
    tr_lang = form.tr_language.data
    if tr_lang is None or not re.search(r'\S', tr_lang):
        flash(word("You must provide a language"), 'error')
        return redirect(url_for('develop.utilities'))
    try:
        interview_source = interview_source_from_string(yaml_filename)
    except DAError:
        flash(word("Invalid interview"), 'error')
        return redirect(url_for('develop.utilities'))
    interview_source.update()
    interview_source.translating = True
    interview = Interview(source=interview_source)
    tr_cache = {}
    if len(interview.translations) > 0:
        for item in interview.translations:
            if item.lower().endswith(".xlsx"):
                the_xlsx_file = package_data_filename(item)
                if not os.path.isfile(the_xlsx_file):
                    continue
                import pandas  # pylint: disable=import-outside-toplevel
                df = pandas.read_excel(the_xlsx_file, na_values=['NaN', '-NaN', '#NA', '#N/A'], keep_default_na=False, usecols='A:H')
                invalid = False
                for column_name in ('interview', 'question_id', 'index_num', 'hash', 'orig_lang', 'tr_lang', 'orig_text', 'tr_text'):
                    if column_name not in df.columns:
                        invalid = True
                        break
                if invalid:
                    continue
                for indexno in df.index:
                    try:
                        assert df['interview'][indexno]
                        assert df['question_id'][indexno]
                        assert df['index_num'][indexno] >= 0
                        assert df['hash'][indexno]
                        assert df['orig_lang'][indexno]
                        assert df['tr_lang'][indexno]
                        assert df['orig_text'][indexno] != ''
                        assert df['tr_text'][indexno] != ''
                        if isinstance(df['orig_text'][indexno], float):
                            assert not math.isnan(df['orig_text'][indexno])
                        if isinstance(df['tr_text'][indexno], float):
                            assert not math.isnan(df['tr_text'][indexno])
                    except:
                        continue
                    the_dict = {'interview': str(df['interview'][indexno]), 'question_id': str(df['question_id'][indexno]), 'index_num': df['index_num'][indexno], 'hash': str(df['hash'][indexno]), 'orig_lang': str(df['orig_lang'][indexno]), 'tr_lang': str(df['tr_lang'][indexno]), 'orig_text': str(df['orig_text'][indexno]), 'tr_text': str(df['tr_text'][indexno])}
                    if df['orig_text'][indexno] not in tr_cache:
                        tr_cache[df['orig_text'][indexno]] = {}
                    if df['orig_lang'][indexno] not in tr_cache[df['orig_text'][indexno]]:
                        tr_cache[df['orig_text'][indexno]][df['orig_lang'][indexno]] = {}
                    tr_cache[df['orig_text'][indexno]][df['orig_lang'][indexno]][df['tr_lang'][indexno]] = the_dict
            elif item.lower().endswith(".xlf") or item.lower().endswith(".xliff"):
                the_xlf_file = package_data_filename(item)
                if not os.path.isfile(the_xlf_file):
                    continue
                tree = ET.parse(the_xlf_file)
                root = tree.getroot()
                indexno = 1
                if root.attrib['version'] == "1.2":
                    for the_file in root.iter('{urn:oasis:names:tc:xliff:document:1.2}file'):
                        source_lang = the_file.attrib.get('source-language', 'en')
                        target_lang = the_file.attrib.get('target-language', 'en')
                        source_filename = the_file.attrib.get('original', yaml_filename)
                        for transunit in the_file.iter('{urn:oasis:names:tc:xliff:document:1.2}trans-unit'):
                            orig_text = ''
                            tr_text = ''
                            for source in transunit.iter('{urn:oasis:names:tc:xliff:document:1.2}source'):
                                if source.text:
                                    orig_text += source.text
                                for mrk in source:
                                    orig_text += mrk.text
                                    if mrk.tail:
                                        orig_text += mrk.tail
                            for target in transunit.iter('{urn:oasis:names:tc:xliff:document:1.2}target'):
                                if target.text:
                                    tr_text += target.text
                                for mrk in target:
                                    tr_text += mrk.text
                                    if mrk.tail:
                                        tr_text += mrk.tail
                            if orig_text == '' or tr_text == '':
                                continue
                            the_dict = {'interview': source_filename, 'question_id': 'Unknown' + str(indexno), 'index_num': transunit.attrib.get('id', str(indexno)), 'hash': hashlib.md5(orig_text.encode('utf-8')).hexdigest(), 'orig_lang': source_lang, 'tr_lang': target_lang, 'orig_text': orig_text, 'tr_text': tr_text}
                            if orig_text not in tr_cache:
                                tr_cache[orig_text] = {}
                            if source_lang not in tr_cache[orig_text]:
                                tr_cache[orig_text][source_lang] = {}
                            tr_cache[orig_text][source_lang][target_lang] = the_dict
                            indexno += 1
                elif root.attrib['version'] == "2.0":
                    source_lang = root.attrib['srcLang']
                    target_lang = root.attrib['trgLang']
                    for the_file in root.iter('{urn:oasis:names:tc:xliff:document:2.0}file'):
                        source_filename = the_file.attrib.get('original', yaml_filename)
                        for unit in the_file.iter('{urn:oasis:names:tc:xliff:document:2.0}unit'):
                            question_id = unit.attrib.get('id', 'Unknown' + str(indexno))
                            for segment in unit.iter('{urn:oasis:names:tc:xliff:document:2.0}segment'):
                                orig_text = ''
                                tr_text = ''
                                for source in transunit.iter('{urn:oasis:names:tc:xliff:document:2.0}source'):
                                    if source.text:
                                        orig_text += source.text
                                    for mrk in source:
                                        orig_text += mrk.text
                                        if mrk.tail:
                                            orig_text += mrk.tail
                                for target in transunit.iter('{urn:oasis:names:tc:xliff:document:2.0}target'):
                                    if target.text:
                                        tr_text += target.text
                                    for mrk in target:
                                        tr_text += mrk.text
                                        if mrk.tail:
                                            tr_text += mrk.tail
                                if orig_text == '' or tr_text == '':
                                    continue
                                the_dict = {'interview': source_filename, 'question_id': question_id, 'index_num': segment.attrib.get('id', str(indexno)), 'hash': hashlib.md5(orig_text.encode('utf-8')).hexdigest(), 'orig_lang': source_lang, 'tr_lang': target_lang, 'orig_text': orig_text, 'tr_text': tr_text}
                                if orig_text not in tr_cache:
                                    tr_cache[orig_text] = {}
                                if source_lang not in tr_cache[orig_text]:
                                    tr_cache[orig_text][source_lang] = {}
                                tr_cache[orig_text][source_lang][target_lang] = the_dict
                                indexno += 1
    if form.filetype.data == 'XLSX':
        temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        xlsx_filename = space_to_underscore(os.path.splitext(os.path.basename(re.sub(r'.*:', '', yaml_filename)))[0]) + "_" + tr_lang + ".xlsx"
        workbook = xlsxwriter.Workbook(temp_file.name)
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': 1})
        text = workbook.add_format()
        text.set_align('top')
        fixedcell = workbook.add_format()
        fixedcell.set_align('top')
        fixedcell.set_text_wrap()
        fixedunlockedcell = workbook.add_format()
        fixedunlockedcell.set_align('top')
        fixedunlockedcell.set_text_wrap()
        # fixedunlockedcell.set_locked(False)
        fixed = workbook.add_format()
        fixedone = workbook.add_format()
        fixedone.set_bold()
        fixedone.set_font_color('green')
        fixedtwo = workbook.add_format()
        fixedtwo.set_bold()
        fixedtwo.set_font_color('blue')
        fixedunlocked = workbook.add_format()
        fixedunlockedone = workbook.add_format()
        fixedunlockedone.set_bold()
        fixedunlockedone.set_font_color('green')
        fixedunlockedtwo = workbook.add_format()
        fixedunlockedtwo.set_bold()
        fixedunlockedtwo.set_font_color('blue')
        wholefixed = workbook.add_format()
        wholefixed.set_align('top')
        wholefixed.set_text_wrap()
        wholefixedone = workbook.add_format()
        wholefixedone.set_bold()
        wholefixedone.set_font_color('green')
        wholefixedone.set_align('top')
        wholefixedone.set_text_wrap()
        wholefixedtwo = workbook.add_format()
        wholefixedtwo.set_bold()
        wholefixedtwo.set_font_color('blue')
        wholefixedtwo.set_align('top')
        wholefixedtwo.set_text_wrap()
        wholefixedunlocked = workbook.add_format()
        wholefixedunlocked.set_align('top')
        wholefixedunlocked.set_text_wrap()
        # wholefixedunlocked.set_locked(False)
        wholefixedunlockedone = workbook.add_format()
        wholefixedunlockedone.set_bold()
        wholefixedunlockedone.set_font_color('green')
        wholefixedunlockedone.set_align('top')
        wholefixedunlockedone.set_text_wrap()
        # wholefixedunlockedone.set_locked(False)
        wholefixedunlockedtwo = workbook.add_format()
        wholefixedunlockedtwo.set_bold()
        wholefixedunlockedtwo.set_font_color('blue')
        wholefixedunlockedtwo.set_align('top')
        wholefixedunlockedtwo.set_text_wrap()
        # wholefixedunlockedtwo.set_locked(False)
        numb = workbook.add_format()
        numb.set_align('top')
        worksheet.write('A1', 'interview', bold)
        worksheet.write('B1', 'question_id', bold)
        worksheet.write('C1', 'index_num', bold)
        worksheet.write('D1', 'hash', bold)
        worksheet.write('E1', 'orig_lang', bold)
        worksheet.write('F1', 'tr_lang', bold)
        worksheet.write('G1', 'orig_text', bold)
        worksheet.write('H1', 'tr_text', bold)
        # options = {
        #     'objects':               False,
        #     'scenarios':             False,
        #     'format_cells':          False,
        #     'format_columns':        False,
        #     'format_rows':           False,
        #     'insert_columns':        False,
        #     'insert_rows':           True,
        #     'insert_hyperlinks':     False,
        #     'delete_columns':        False,
        #     'delete_rows':           True,
        #     'select_locked_cells':   True,
        #     'sort':                  True,
        #     'autofilter':            True,
        #     'pivot_tables':          False,
        #     'select_unlocked_cells': True,
        # }
        # worksheet.protect('', options)
        worksheet.set_column(0, 0, 25)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 12)
        worksheet.set_column(6, 6, 75)
        worksheet.set_column(6, 7, 75)
        row = 1
        seen = []
        for question in interview.all_questions:
            if not hasattr(question, 'translations'):
                continue
            language = question.language
            if language == '*':
                language = question.from_source.get_language()
            if language == '*':
                language = interview.default_language
            if language == tr_lang:
                continue
            indexno = 0
            if hasattr(question, 'id'):
                question_id = question.id
            else:
                question_id = question.name
            for item in question.translations:
                if item in seen:
                    continue
                if item in tr_cache and language in tr_cache[item] and tr_lang in tr_cache[item][language]:
                    tr_text = str(tr_cache[item][language][tr_lang]['tr_text'])
                else:
                    tr_text = ''
                worksheet.write_string(row, 0, question.from_source.get_name(), text)
                worksheet.write_string(row, 1, question_id, text)
                worksheet.write_number(row, 2, indexno, numb)
                worksheet.write_string(row, 3, hashlib.md5(item.encode('utf-8')).hexdigest(), text)
                worksheet.write_string(row, 4, language, text)
                worksheet.write_string(row, 5, tr_lang, text)
                mako = mako_parts(item)
                if len(mako) == 0:
                    worksheet.write_string(row, 6, '', wholefixed)
                elif len(mako) == 1:
                    if mako[0][1] == 0:
                        worksheet.write_string(row, 6, item, wholefixed)
                    elif mako[0][1] == 1:
                        worksheet.write_string(row, 6, item, wholefixedone)
                    elif mako[0][1] == 2:
                        worksheet.write_string(row, 6, item, wholefixedtwo)
                else:
                    parts = [row, 6]
                    for part in mako:
                        if part[1] == 0:
                            parts.extend([fixed, part[0]])
                        elif part[1] == 1:
                            parts.extend([fixedone, part[0]])
                        elif part[1] == 2:
                            parts.extend([fixedtwo, part[0]])
                    parts.append(fixedcell)
                    worksheet.write_rich_string(*parts)
                mako = mako_parts(tr_text)
                if len(mako) == 0:
                    worksheet.write_string(row, 7, '', wholefixedunlocked)
                elif len(mako) == 1:
                    if mako[0][1] == 0:
                        worksheet.write_string(row, 7, tr_text, wholefixedunlocked)
                    elif mako[0][1] == 1:
                        worksheet.write_string(row, 7, tr_text, wholefixedunlockedone)
                    elif mako[0][1] == 2:
                        worksheet.write_string(row, 7, tr_text, wholefixedunlockedtwo)
                else:
                    parts = [row, 7]
                    for part in mako:
                        if part[1] == 0:
                            parts.extend([fixedunlocked, part[0]])
                        elif part[1] == 1:
                            parts.extend([fixedunlockedone, part[0]])
                        elif part[1] == 2:
                            parts.extend([fixedunlockedtwo, part[0]])
                    parts.append(fixedunlockedcell)
                    worksheet.write_rich_string(*parts)
                num_lines = item.count('\n')
                # if num_lines > 25:
                #    num_lines = 25
                if num_lines > 0:
                    worksheet.set_row(row, 15*(num_lines + 1))
                indexno += 1
                row += 1
                seen.append(item)
        for item, cache_item in tr_cache.items():
            if item in seen or language not in cache_item or tr_lang not in cache_item[language]:
                continue
            worksheet.write_string(row, 0, cache_item[language][tr_lang]['interview'], text)
            worksheet.write_string(row, 1, cache_item[language][tr_lang]['question_id'], text)
            worksheet.write_number(row, 2, 1000 + cache_item[language][tr_lang]['index_num'], numb)
            worksheet.write_string(row, 3, cache_item[language][tr_lang]['hash'], text)
            worksheet.write_string(row, 4, cache_item[language][tr_lang]['orig_lang'], text)
            worksheet.write_string(row, 5, cache_item[language][tr_lang]['tr_lang'], text)
            mako = mako_parts(cache_item[language][tr_lang]['orig_text'])
            if len(mako) == 1:
                if mako[0][1] == 0:
                    worksheet.write_string(row, 6, cache_item[language][tr_lang]['orig_text'], wholefixed)
                elif mako[0][1] == 1:
                    worksheet.write_string(row, 6, cache_item[language][tr_lang]['orig_text'], wholefixedone)
                elif mako[0][1] == 2:
                    worksheet.write_string(row, 6, cache_item[language][tr_lang]['orig_text'], wholefixedtwo)
            else:
                parts = [row, 6]
                for part in mako:
                    if part[1] == 0:
                        parts.extend([fixed, part[0]])
                    elif part[1] == 1:
                        parts.extend([fixedone, part[0]])
                    elif part[1] == 2:
                        parts.extend([fixedtwo, part[0]])
                parts.append(fixedcell)
                worksheet.write_rich_string(*parts)
            mako = mako_parts(cache_item[language][tr_lang]['tr_text'])
            if len(mako) == 1:
                if mako[0][1] == 0:
                    worksheet.write_string(row, 7, cache_item[language][tr_lang]['tr_text'], wholefixedunlocked)
                elif mako[0][1] == 1:
                    worksheet.write_string(row, 7, cache_item[language][tr_lang]['tr_text'], wholefixedunlockedone)
                elif mako[0][1] == 2:
                    worksheet.write_string(row, 7, cache_item[language][tr_lang]['tr_text'], wholefixedunlockedtwo)
            else:
                parts = [row, 7]
                for part in mako:
                    if part[1] == 0:
                        parts.extend([fixedunlocked, part[0]])
                    elif part[1] == 1:
                        parts.extend([fixedunlockedone, part[0]])
                    elif part[1] == 2:
                        parts.extend([fixedunlockedtwo, part[0]])
                parts.append(fixedunlockedcell)
                worksheet.write_rich_string(*parts)
            num_lines = cache_item[language][tr_lang]['orig_text'].count('\n')
            if num_lines > 0:
                worksheet.set_row(row, 15*(num_lines + 1))
            row += 1
        workbook.close()
        response = custom_send_file(temp_file.name, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=xlsx_filename)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response
    if form.filetype.data.startswith('XLIFF'):
        seen = set()
        translations = {}
        xliff_files = []
        if form.filetype.data == 'XLIFF 1.2':
            for question in interview.all_questions:
                if not hasattr(question, 'translations'):
                    continue
                language = question.language
                if language == '*':
                    language = interview_source.language
                if language == '*':
                    language = DEFAULT_LANGUAGE
                if language == tr_lang:
                    continue
                question_id = question.name
                lang_combo = (language, tr_lang)
                if lang_combo not in translations:
                    translations[lang_combo] = []
                for item in question.translations:
                    if item in seen:
                        continue
                    if item in tr_cache and language in tr_cache[item] and tr_lang in tr_cache[item][language]:
                        tr_text = str(tr_cache[item][language][tr_lang]['tr_text'])
                    else:
                        tr_text = ''
                    orig_mako = mako_parts(item)
                    tr_mako = mako_parts(tr_text)
                    translations[lang_combo].append([orig_mako, tr_mako])
                    seen.add(item)
            for lang_combo, translation_list in translations.items():
                temp_file = tempfile.NamedTemporaryFile(suffix='.xlf', delete=False)
                if len(translations) > 1:
                    xlf_filename = space_to_underscore(os.path.splitext(os.path.basename(re.sub(r'.*:', '', yaml_filename)))[0]) + "_" + lang_combo[0] + "_" + lang_combo[1] + ".xlf"
                else:
                    xlf_filename = space_to_underscore(os.path.splitext(os.path.basename(re.sub(r'.*:', '', yaml_filename)))[0]) + "_" + lang_combo[1] + ".xlf"
                xliff = ET.Element('xliff')
                xliff.set('xmlns', 'urn:oasis:names:tc:xliff:document:1.2')
                xliff.set('version', '1.2')
                indexno = 1
                the_file = ET.SubElement(xliff, 'file')
                the_file.set('id', 'f1')
                the_file.set('original', yaml_filename)
                the_file.set('xml:space', 'preserve')
                the_file.set('source-language', lang_combo[0])
                the_file.set('target-language', lang_combo[1])
                body = ET.SubElement(the_file, 'body')
                for item in translation_list:
                    transunit = ET.SubElement(body, 'trans-unit')
                    transunit.set('id', str(indexno))
                    transunit.set('xml:space', 'preserve')
                    source = ET.SubElement(transunit, 'source')
                    source.set('xml:space', 'preserve')
                    target = ET.SubElement(transunit, 'target')
                    target.set('xml:space', 'preserve')
                    last_elem = None
                    for (elem, i) in ((source, 0), (target, 1)):
                        if len(item[i]) == 0:
                            elem.text = ''
                        elif len(item[i]) == 1 and item[i][0][1] == 0:
                            elem.text = item[i][0][0]
                        else:
                            for part in item[i]:
                                if part[1] == 0:
                                    if last_elem is None:
                                        if elem.text is None:
                                            elem.text = ''
                                        elem.text += part[0]
                                    else:
                                        if last_elem.tail is None:
                                            last_elem.tail = ''
                                        last_elem.tail += part[0]
                                else:
                                    mrk = ET.SubElement(elem, 'mrk')
                                    mrk.set('xml:space', 'preserve')
                                    mrk.set('mtype', 'protected')
                                    mrk.text = part[0]
                                    last_elem = mrk
                    indexno += 1
                temp_file.write(ET.tostring(xliff))
                temp_file.close()
                xliff_files.append([temp_file, xlf_filename])
        elif form.filetype.data == 'XLIFF 2.0':
            for question in interview.all_questions:
                if not hasattr(question, 'translations'):
                    continue
                language = question.language
                if language == '*':
                    language = interview_source.language
                if language == '*':
                    language = DEFAULT_LANGUAGE
                if language == tr_lang:
                    continue
                question_id = question.name
                lang_combo = (language, tr_lang)
                if lang_combo not in translations:
                    translations[lang_combo] = {}
                filename = question.from_source.get_name()
                if filename not in translations[lang_combo]:
                    translations[lang_combo][filename] = {}
                if question_id not in translations[lang_combo][filename]:
                    translations[lang_combo][filename][question_id] = []
                for item in question.translations:
                    if item in seen:
                        continue
                    if item in tr_cache and language in tr_cache[item] and tr_lang in tr_cache[item][language]:
                        tr_text = str(tr_cache[item][language][tr_lang]['tr_text'])
                    else:
                        tr_text = ''
                    orig_mako = mako_parts(item)
                    tr_mako = mako_parts(tr_text)
                    translations[lang_combo][filename][question_id].append([orig_mako, tr_mako])
                    seen.add(item)
            for lang_combo, translations_by_filename in translations.items():
                temp_file = tempfile.NamedTemporaryFile(suffix='.xlf', delete=False)
                if len(translations) > 1:
                    xlf_filename = space_to_underscore(os.path.splitext(os.path.basename(re.sub(r'.*:', '', yaml_filename)))[0]) + "_" + lang_combo[0] + "_" + lang_combo[1] + ".xlf"
                else:
                    xlf_filename = space_to_underscore(os.path.splitext(os.path.basename(re.sub(r'.*:', '', yaml_filename)))[0]) + "_" + lang_combo[1] + ".xlf"
                xliff = ET.Element('xliff')
                xliff.set('xmlns', 'urn:oasis:names:tc:xliff:document:2.0')
                xliff.set('version', '2.0')
                xliff.set('srcLang', lang_combo[0])
                xliff.set('trgLang', lang_combo[1])
                file_index = 1
                indexno = 1
                for filename, translations_by_question in translations_by_filename.items():
                    the_file = ET.SubElement(xliff, 'file')
                    the_file.set('id', 'f' + str(file_index))
                    the_file.set('original', filename)
                    the_file.set('xml:space', 'preserve')
                    for question_id, translation_list in translations_by_question.items():
                        unit = ET.SubElement(the_file, 'unit')
                        unit.set('id', question_id)
                        for item in translation_list:
                            segment = ET.SubElement(unit, 'segment')
                            segment.set('id', str(indexno))
                            segment.set('xml:space', 'preserve')
                            source = ET.SubElement(segment, 'source')
                            source.set('xml:space', 'preserve')
                            target = ET.SubElement(segment, 'target')
                            target.set('xml:space', 'preserve')
                            last_elem = None
                            for (elem, i) in ((source, 0), (target, 1)):
                                if len(item[i]) == 0:
                                    elem.text = ''
                                elif len(item[i]) == 1 and item[i][0][1] == 0:
                                    elem.text = item[i][0][0]
                                else:
                                    for part in item[i]:
                                        if part[1] == 0:
                                            if last_elem is None:
                                                if elem.text is None:
                                                    elem.text = ''
                                                elem.text += part[0]
                                            else:
                                                if last_elem.tail is None:
                                                    last_elem.tail = ''
                                                last_elem.tail += part[0]
                                        else:
                                            mrk = ET.SubElement(elem, 'mrk')
                                            mrk.set('xml:space', 'preserve')
                                            mrk.set('translate', 'no')
                                            mrk.text = part[0]
                                            last_elem = mrk
                            indexno += 1
                    file_index += 1
                temp_file.write(ET.tostring(xliff))
                temp_file.close()
                xliff_files.append([temp_file, xlf_filename])
        else:
            flash(word("Bad file format"), 'error')
            return redirect(url_for('develop.utilities'))
        if len(xliff_files) == 1:
            response = custom_send_file(xliff_files[0][0].name, mimetype='application/xml', as_attachment=True, download_name=xliff_files[0][1])
        else:
            zip_file = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
            zip_file_name = space_to_underscore(os.path.splitext(os.path.basename(re.sub(r'.*:', '', yaml_filename)))[0]) + "_" + tr_lang + ".zip"
            with zipfile.ZipFile(zip_file, compression=zipfile.ZIP_DEFLATED, mode='w') as zf:
                for item in xliff_files:
                    info = zipfile.ZipInfo(item[1])
                    with open(item[0].name, 'rb') as fp:
                        zf.writestr(info, fp.read())
                zf.close()
            response = custom_send_file(zip_file.name, mimetype='application/xml', as_attachment=True, download_name=zip_file_name)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response
    flash(word("Bad file format"), 'error')
    return redirect(url_for('develop.utilities'))
