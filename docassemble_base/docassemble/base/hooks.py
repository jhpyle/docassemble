# pylint: disable=unused-argument
from typing import Any
from .plugin_manager import pm


def get_default_language() -> str:
    return pm.hook.get_default_language()

def get_default_dialect() -> str:
    return pm.hook.get_default_dialect()

def get_default_locale() -> str:
    return pm.hook.get_default_locale()

def get_default_voice() -> str:
    return pm.hook.get_default_voice()

def get_default_timezone() -> str:
    return pm.hook.get_default_timezone()

def get_default_country() -> str:
    return pm.hook.get_default_country()

def get_configuration() -> dict:
    return pm.hook.get_configuration()

def get_hostname() -> str:
    return pm.hook.get_hostname()

def get_debug_status() -> bool:
    return pm.hook.get_debug_status()

def save_numbered_file(filename, orig_path, yaml_file_name=None, uid=None) -> tuple:
    return pm.hook.save_numbered_file(
        filename=filename,
        orig_path=orig_path,
        yaml_file_name=yaml_file_name,
        uid=uid,
    )

def send_mail(the_message, config='default') -> None:
    return pm.hook.send_mail(the_message=the_message, config=config)

def absolute_filename(the_file) -> Any:
    return pm.hook.absolute_filename(the_file=the_file)

def write_record(key, data) -> int:
    return pm.hook.write_record(key=key, data=data)

def read_records(key) -> Any:
    return pm.hook.read_records(key=key)

def delete_record(key, the_id) -> Any:
    return pm.hook.delete_record(key=key, the_id=the_id)

def generate_csrf(secret_key=None, token_key=None) -> Any:
    return pm.hook.generate_csrf(secret_key=secret_key, token_key=token_key)

def url_for(endpoint, **kwargs) -> Any:
    return pm.hook.url_for(endpoint=endpoint, kwargs=kwargs)

def get_new_file_number(user_code, file_name, yaml_file_name=None) -> Any:
    return pm.hook.get_new_file_number(
        user_code=user_code,
        file_name=file_name,
        yaml_file_name=yaml_file_name,
    )

def get_ext_and_mimetype(filename) -> Any:
    return pm.hook.get_ext_and_mimetype(filename=filename)

def file_finder(file_reference, question=None, folder=None, package=None, filename=None, return_nonexistent=False, uids=None) -> Any:
    return pm.hook.file_finder(
        file_reference=file_reference,
        question=question,
        folder=folder,
        package=package,
        filename=filename,
        return_nonexistent=return_nonexistent,
        uids=uids,
    )

def file_number_finder(file_number, filename=None, uids=None, privileged=False) -> Any:
    return pm.hook.file_number_finder(
        file_number=file_number,
        filename=filename,
        uids=uids,
        privileged=privileged,
    )

def server_sql_get(key, secret=None) -> Any:
    return pm.hook.server_sql_get(key=key, secret=secret)

def server_sql_defined(key) -> Any:
    return pm.hook.server_sql_defined(key=key)

def server_sql_set(key, val, encrypted=True, secret=None, the_user_id=None) -> Any:
    return pm.hook.server_sql_set(
        key=key,
        val=val,
        encrypted=encrypted,
        secret=secret,
        the_user_id=the_user_id,
    )

def server_sql_delete(key) -> Any:
    return pm.hook.server_sql_delete(key=key)

def server_sql_keys(prefix) -> Any:
    return pm.hook.server_sql_keys(prefix=prefix)

def alchemy_url(db_config) -> Any:
    return pm.hook.alchemy_url(db_config=db_config)

def connect_args(db_config) -> Any:
    return pm.hook.connect_args(db_config=db_config)

def get_default_table_class() -> Any:
    return pm.hook.get_default_table_class()

def get_default_thead_class() -> Any:
    return pm.hook.get_default_thead_class()

def to_text(html_doc) -> Any:
    return pm.hook.to_text(html_doc=html_doc)

def url_finder(file_reference, **kwargs) -> Any:
    return pm.hook.url_finder(file_reference=file_reference, kwargs=kwargs)

def navigation_bar(nav, interview, wrapper=True, inner_div_class=None, inner_div_extra=None, show_links=None, hide_inactive_subs=True, a_class=None, show_nesting=True, include_arrows=False, always_open=False, return_dict=None) -> Any:
    return pm.hook.navigation_bar(
        nav=nav,
        interview=interview,
        wrapper=wrapper,
        inner_div_class=inner_div_class,
        inner_div_extra=inner_div_extra,
        show_links=show_links,
        hide_inactive_subs=hide_inactive_subs,
        a_class=a_class,
        show_nesting=show_nesting,
        include_arrows=include_arrows,
        always_open=always_open,
        return_dict=return_dict,
    )

def chat_partners_available(session_id, yaml_filename, the_user_id, mode, partner_roles) -> Any:
    return pm.hook.chat_partners_available(
        session_id=session_id,
        yaml_filename=yaml_filename,
        the_user_id=the_user_id,
        mode=mode,
        partner_roles=partner_roles,
    )

def get_chat_log(yaml_filename, session_id, secret, utc=True, timezone=None) -> Any:
    return pm.hook.get_chat_log(
        yaml_filename=yaml_filename,
        session_id=session_id,
        secret=secret,
        utc=utc,
        timezone=timezone,
    )

def sms_body(phone_number, body='question', config='default') -> Any:
    return pm.hook.sms_body(phone_number=phone_number, body=body, config=config)

def send_fax(fax_number, the_file, config, country=None) -> Any:
    return pm.hook.send_fax(
        fax_number=fax_number,
        the_file=the_file,
        config=config,
        country=country,
    )

def get_sms_session(phone_number, config='default') -> Any:
    return pm.hook.get_sms_session(phone_number=phone_number, config=config)

def initiate_sms_session(phone_number, yaml_filename=None, uid=None, secret=None, encrypted=None, user_id=None, email=None, new=False, config='default') -> Any:
    return pm.hook.initiate_sms_session(
        phone_number=phone_number,
        yaml_filename=yaml_filename,
        uid=uid,
        secret=secret,
        encrypted=encrypted,
        user_id=user_id,
        email=email,
        new=new,
        config=config,
    )

def terminate_sms_session(phone_number, config='default') -> Any:
    return pm.hook.terminate_sms_session(phone_number=phone_number, config=config)

def applock(action, application, maxtime=4) -> Any:
    return pm.hook.applock(action=action, application=application, maxtime=maxtime)

def get_twilio_config() -> Any:
    return pm.hook.get_twilio_config()

def get_server_redis() -> Any:
    return pm.hook.get_server_redis()

def get_server_redis_user() -> Any:
    return pm.hook.get_server_redis_user()

def get_user_object(user_id) -> Any:
    return pm.hook.get_user_object(user_id=user_id)

def user_id_dict() -> Any:
    return pm.hook.user_id_dict()

def retrieve_email(email_id) -> Any:
    return pm.hook.retrieve_email(email_id=email_id)

def retrieve_emails(**kwargs) -> Any:
    return pm.hook.retrieve_emails(kwargs=kwargs)

def get_short_code(**kwargs) -> Any:
    return pm.hook.get_short_code(kwargs)

def make_png_for_pdf(doc, prefix, page=None) -> Any:
    return pm.hook.make_png_for_pdf(doc=doc, prefix=prefix, page=page)

def ocr_google_in_background(image_file, raw_result, user_code) -> Any:
    return pm.hook.ocr_google_in_background(
        image_file=image_file,
        raw_result=raw_result,
        user_code=user_code,
    )

def task_ready(task_id) -> Any:
    return pm.hook.task_ready(task_id=task_id)

def wait_for_task(task_id, timeout=None) -> Any:
    return pm.hook.wait_for_task(task_id=task_id, timeout=timeout)

def user_interviews(user_id=None, secret=None, exclude_invalid=True, action=None, filename=None, session=None, tag=None, include_dict=True, delete_shared=False, admin=False, start_id=None, temp_user_id=None, query=None, minimal=False) -> Any:
    return pm.hook.user_interviews(
        user_id=user_id,
        secret=secret,
        exclude_invalid=exclude_invalid,
        action=action,
        filename=filename,
        session=session,
        tag=tag,
        include_dict=include_dict,
        delete_shared=delete_shared,
        admin=admin,
        start_id=start_id,
        temp_user_id=temp_user_id,
        query=query,
        minimal=minimal,
    )

def server_interview_menu(absolute_urls=False, start_new=False, tag=None) -> Any:
    return pm.hook.server_interview_menu(
        absolute_urls=absolute_urls,
        start_new=start_new,
        tag=tag,
    )

def server_get_user_list(include_inactive=False, start_id=None) -> Any:
    return pm.hook.server_get_user_list(
        include_inactive=include_inactive,
        start_id=start_id,
    )

def server_get_user_info(user_id=None, email=None, case_sensitive=False, admin=False) -> Any:
    return pm.hook.server_get_user_info(
        user_id=user_id,
        email=email,
        case_sensitive=case_sensitive,
        admin=admin,
    )

def server_set_user_info(**kwargs) -> Any:
    return pm.hook.server_set_user_info(kwargs=kwargs)

def make_user_inactive(user_id=None, email=None) -> Any:
    return pm.hook.make_user_inactive(user_id=user_id, email=email)

def server_get_secret(username, password, case_sensitive=False) -> Any:
    return pm.hook.server_get_secret(
        username=username,
        password=password,
        case_sensitive=case_sensitive,
    )

def server_get_session_variables(yaml_filename, session_id, secret=None, simplify=True, use_lock=False) -> Any:
    return pm.hook.server_get_session_variables(
        yaml_filename=yaml_filename,
        session_id=session_id,
        secret=secret,
        simplify=simplify,
        use_lock=use_lock,
    )

def server_go_back_in_session(yaml_filename, session_id, secret=None, return_question=False, use_lock=False, encode=False) -> Any:
    return pm.hook.server_go_back_in_session(
        yaml_filename=yaml_filename,
        session_id=session_id,
        secret=secret,
        return_question=return_question,
        use_lock=use_lock,
        encode=encode,
    )

def server_create_session(yaml_filename, secret, url_args=None, referer=None, req=None) -> Any:
    return pm.hook.server_create_session(
        yaml_filename=yaml_filename,
        secret=secret,
        url_args=url_args,
        referer=referer,
        req=req,
    )

def server_set_session_variables(yaml_filename, session_id, variables, secret=None, return_question=False, literal_variables=None, del_variables=None, question_name=None, event_list=None, advance_progress_meter=False, post_setting=True, use_lock=False, encode=False, process_objects=False) -> Any:
    return pm.hook.server_set_session_variables(
        yaml_filename=yaml_filename,
        session_id=session_id,
        variables=variables,
        secret=secret,
        return_question=return_question,
        literal_variables=literal_variables,
        del_variables=del_variables,
        question_name=question_name,
        event_list=event_list,
        advance_progress_meter=advance_progress_meter,
        post_setting=post_setting,
        use_lock=use_lock,
        encode=encode,
        process_objects=process_objects,
    )

def get_privileges_list(admin=False) -> Any:
    return pm.hook.get_privileges_list(admin=admin)

def add_privilege(privilege) -> Any:
    return pm.hook.add_privilege(privilege=privilege)

def remove_privilege(privilege) -> Any:
    return pm.hook.remove_privilege(privilege=privilege)

def add_user_privilege(user_id, privilege) -> Any:
    return pm.hook.add_user_privilege(user_id=user_id, privilege=privilege)

def remove_user_privilege(user_id, privilege) -> Any:
    return pm.hook.remove_user_privilege(user_id=user_id, privilege=privilege)

def get_permissions_of_privilege(privilege, privileged=False) -> Any:
    return pm.hook.get_permissions_of_privilege(privilege=privilege, privileged=privileged)

def server_create_user(email, password, privileges=None, info=None) -> Any:
    return pm.hook.server_create_user(
        email=email,
        password=password,
        privileges=privileges,
        info=info,
    )

def file_set_attributes(file_number, **kwargs) -> Any:
    return pm.hook.file_set_attributes(
        file_number=file_number,
        private=kwargs.get('private', None),
        persistent=kwargs.get('persistent', None),
        session=kwargs.get('session', None),
        filename=kwargs.get('filename', None),
    )

def file_user_access(file_number, allow_user_id=None, allow_email=None, disallow_user_id=None, disallow_email=None, disallow_all=False) -> Any:
    return pm.hook.file_user_access(
        file_number=file_number,
        allow_user_id=allow_user_id,
        allow_email=allow_email,
        disallow_user_id=disallow_user_id,
        disallow_email=disallow_email,
        disallow_all=disallow_all,
    )

def file_privilege_access(file_number, allow=None, disallow=None, disallow_all=False) -> Any:
    return pm.hook.file_privilege_access(
        file_number=file_number,
        allow=allow,
        disallow=disallow,
        disallow_all=disallow_all,
    )

def fg_make_png_for_pdf(doc, prefix, page=None) -> Any:
    return pm.hook.fg_make_png_for_pdf(doc=doc, prefix=prefix, page=page)

def fg_make_png_for_pdf_path(path, prefix, page=None) -> Any:
    return pm.hook.fg_make_png_for_pdf_path(path=path, prefix=prefix, page=page)

def fg_make_pdf_for_word_path(path, extension) -> Any:
    return pm.hook.fg_make_pdf_for_word_path(path=path, extension=extension)

def server_get_question_data(yaml_filename, session_id, secret, use_lock=True, user_dict=None, steps=None, is_encrypted=None, old_user_dict=None, save=True, post_setting=False, advance_progress_meter=False, action=None, encode=False) -> Any:
    return pm.hook.server_get_question_data(
        yaml_filename=yaml_filename,
        session_id=session_id,
        secret=secret,
        use_lock=use_lock,
        user_dict=user_dict,
        steps=steps,
        is_encrypted=is_encrypted,
        old_user_dict=old_user_dict,
        save=save,
        post_setting=post_setting,
        advance_progress_meter=advance_progress_meter,
        action=action,
        encode=encode,
    )

def fix_pickle_obj(data) -> Any:
    return pm.hook.fix_pickle_obj(data=data)

def get_main_page_parts() -> Any:
    return pm.hook.get_main_page_parts()

def get_saved_file_class() -> Any:
    return pm.hook.get_saved_file_class()

def path_from_reference(file_reference) -> Any:
    return pm.hook.path_from_reference(file_reference=file_reference)

def get_button_class_prefix() -> Any:
    return pm.hook.get_button_class_prefix()

def write_answer_json(user_code, filename, data, tags=None, persistent=False) -> Any:
    return pm.hook.write_answer_json(
        user_code=user_code,
        filename=filename,
        data=data,
        tags=tags,
        persistent=persistent,
    )

def read_answer_json(user_code, filename, tags=None, all_tags=False) -> Any:
    return pm.hook.read_answer_json(
        user_code=user_code,
        filename=filename,
        tags=tags,
        all_tags=all_tags,
    )

def delete_answer_json(user_code, filename, tags=None, delete_all=False, delete_persistent=False) -> Any:
    return pm.hook.delete_answer_json(
        user_code=user_code,
        filename=filename,
        tags=tags,
        delete_all=delete_all,
        delete_persistent=delete_persistent,
    )

def variables_snapshot_connection() -> Any:
    return pm.hook.variables_snapshot_connection()

def variables_snapshot_connect() -> Any:
    return pm.hook.variables_snapshot_connect()

def get_referer() -> Any:
    return pm.hook.get_referer()

def stash_data(data, expire) -> Any:
    return pm.hook.stash_data(data=data, expire=expire)

def retrieve_stashed_data(key, secret, delete=False, refresh=False) -> Any:
    return pm.hook.retrieve_stashed_data(key=key, secret=secret, delete=delete, refresh=refresh)

def secure_filename_spaces_ok(filename) -> Any:
    return pm.hook.secure_filename_spaces_ok(filename=filename)

def secure_filename_unicode_ok(the_filename) -> Any:
    return pm.hook.secure_filename_unicode_ok(the_filename=the_filename)

def secure_filename(filename) -> Any:
    return pm.hook.secure_filename(filename=filename)

def transform_json_variables(obj) -> Any:
    return pm.hook.transform_json_variables(obj=obj)

def get_login_url(**kwargs) -> Any:
    return pm.hook.get_login_url(kwargs=kwargs)

def server_run_action_in_session(**kwargs) -> Any:
    return pm.hook.server_run_action_in_session(kwargs=kwargs)

def server_invite_user(email_address, privilege=None, send=True) -> Any:
    return pm.hook.server_invite_user(
        email_address=email_address,
        privilege=privilege,
        send=send,
    )

def get_url() -> Any:
    return pm.hook.get_url()

def release_lock(user_code, filename) -> Any:
    return pm.hook.release_lock(user_code=user_code, filename=filename)

def register_db(db_name) -> Any:
    return pm.hook.register_db(db_name=db_name)

def create_objects_in_db(db_name) -> Any:
    return pm.hook.create_objects_in_db(db_name=db_name)

def get_cloud() -> Any:
    return pm.hook.get_cloud()

def cloud_custom(provider, config) -> Any:
    return pm.hook.cloud_custom(provider=provider, config=config)

def google_api() -> Any:
    return pm.hook.google_api()

def get_mail_class() -> Any:
    return pm.hook.get_mail_class()

def get_celery_app() -> Any:
    return pm.hook.get_celery_app()

def get_task(obj) -> Any:
    return pm.hook.get_task(obj=obj)

def chord(arg) -> Any:
    return pm.hook.chord(arg=arg)

def fix_ml_files(playground_number, current_project) -> Any:
    return pm.hook.fix_ml_files(playground_number=playground_number, current_project=current_project)

def write_ml_source(playground, playground_number, current_project, filename, finalize=True):
    return pm.hook.write_ml_source(playground=playground, playground_number=playground_number, current_project=current_project, filename=filename, finalize=finalize)

def ensure_training_loaded(interview) -> Any:
    return pm.hook.ensure_training_loaded(interview=interview)

def manage_chat_logs(mode: int, **kwargs) -> None:
    return pm.hook.manage_chat_logs(mode=mode, kwargs=kwargs)

def manage_global_objects(mode: int, **kwargs) -> None:
    return pm.hook.manage_global_objects(mode=mode, kwargs=kwargs)

def manage_email_server_objects(mode: int, **kwargs) -> None:
    return pm.hook.manage_email_server_objects(mode=mode, kwargs=kwargs)

def manage_tts_objects(mode: int, **kwargs) -> None:
    return pm.hook.manage_tts_objects(mode=mode, kwargs=kwargs)

def get_chat_log_internal(chat_mode, yaml_filename, session_id, user_id, temp_user_id, secret, self_user_id, self_temp_id) -> Any:
    return pm.hook.get_chat_log(chat_mode=chat_mode, yaml_filename=yaml_filename, session_id=session_id, user_id=user_id, temp_user_id=temp_user_id, secret=secret, self_user_id=self_user_id, self_temp_id=self_temp_id)

def get_ml_info(varname, default_package, default_file) -> Any:
    return pm.hook.get_ml_info(varname=varname, default_package=default_package, default_file=default_file)
