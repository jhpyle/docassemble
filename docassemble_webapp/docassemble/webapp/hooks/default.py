# pylint: disable=unused-argument
from typing import Any
from .impl import hookimpl

@hookimpl(trylast=True)
def get_default_language() -> str:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_default_dialect() -> str:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_default_locale() -> str:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_default_voice() -> str:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_default_timezone() -> str:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_default_country() -> str:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_configuration() -> dict:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_hostname() -> str:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_debug_status() -> bool:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def save_numbered_file(filename, orig_path, yaml_file_name, uid) -> tuple:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def send_mail(the_message, config) -> None:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def absolute_filename(the_file) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def write_record(key, data) -> int:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def read_records(key) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def delete_record(key, the_id) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def generate_csrf(secret_key, token_key) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def url_for(endpoint, kwargs) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_new_file_number(user_code, file_name, yaml_file_name) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_ext_and_mimetype(filename) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def file_finder(file_reference, question, folder, package, filename, return_nonexistent, uids) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def file_number_finder(file_number, filename, uids, privileged) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def server_sql_get(key, secret) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def server_sql_defined(key) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def server_sql_set(key, val, encrypted, secret, the_user_id) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def server_sql_delete(key) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def server_sql_keys(prefix) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def alchemy_url(db_config) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def connect_args(db_config) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_default_table_class() -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_default_thead_class() -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def to_text(html_doc) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def url_finder(file_reference, kwargs) -> Any:
    """Find a URL for a file reference; kwargs is a dict of keyword arguments"""
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def navigation_bar(nav, interview, wrapper, inner_div_class, inner_div_extra, show_links, hide_inactive_subs, a_class, show_nesting, include_arrows, always_open, return_dict) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def chat_partners_available(session_id, yaml_filename, the_user_id, mode, partner_roles) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_chat_log(yaml_filename, session_id, secret, utc, timezone) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def sms_body(phone_number, body, config) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def send_fax(fax_number, the_file, config, country) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_sms_session(phone_number, config) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def initiate_sms_session(phone_number, yaml_filename, uid, secret, encrypted, user_id, email, new, config) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def terminate_sms_session(phone_number, config) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def applock(action, application, maxtime) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_twilio_config() -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_server_redis() -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_server_redis_user() -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_user_object(user_id) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def user_id_dict() -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def retrieve_email(email_id) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def retrieve_emails(kwargs) -> Any:
    """Retrieve emails; kwargs is a dict of keyword arguments"""
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_short_code(kwargs) -> Any:
    """Get short code; kwargs is a dict of keyword arguments"""
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def make_png_for_pdf(doc, prefix, page) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def ocr_google_in_background(image_file, raw_result, user_code) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def task_ready(task_id) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def wait_for_task(task_id, timeout) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def user_interviews(user_id, secret, exclude_invalid, action, filename, session, tag, include_dict, delete_shared, admin, start_id, temp_user_id, query, minimal) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def server_interview_menu(absolute_urls, start_new, tag) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def server_get_user_list(include_inactive, start_id) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def server_get_user_info(user_id, email, case_sensitive, admin) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def server_set_user_info(kwargs) -> Any:
    """Set user info; kwargs is a dict of keyword arguments"""
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def make_user_inactive(user_id, email) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def server_get_secret(username, password, case_sensitive) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def server_get_session_variables(yaml_filename, session_id, secret, simplify, use_lock) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def server_go_back_in_session(yaml_filename, session_id, secret, return_question, use_lock, encode) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def server_create_session(yaml_filename, secret, url_args, referer, req) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def server_set_session_variables(yaml_filename, session_id, variables, secret, return_question, literal_variables, del_variables, question_name, event_list, advance_progress_meter, post_setting, use_lock, encode, process_objects) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_privileges_list(admin) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def add_privilege(privilege) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def remove_privilege(privilege) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def add_user_privilege(user_id, privilege) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def remove_user_privilege(user_id, privilege) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_permissions_of_privilege(privilege, privileged) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def server_create_user(email, password, privileges, info) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def file_set_attributes(file_number, private, persistent, session, filename) -> Any:
    """Set attributes on a stored file"""
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def file_user_access(file_number, allow_user_id, allow_email, disallow_user_id, disallow_email, disallow_all) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def file_privilege_access(file_number, allow, disallow, disallow_all) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def fg_make_png_for_pdf(doc, prefix, page) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def fg_make_png_for_pdf_path(path, prefix, page) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def fg_make_pdf_for_word_path(path, extension) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def server_get_question_data(yaml_filename, session_id, secret, use_lock, user_dict, steps, is_encrypted, old_user_dict, save, post_setting, advance_progress_meter, action, encode) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def fix_pickle_obj(data) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_main_page_parts() -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_saved_file_class() -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def path_from_reference(file_reference) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_button_class_prefix() -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def write_answer_json(user_code, filename, data, tags, persistent) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def read_answer_json(user_code, filename, tags, all_tags) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def delete_answer_json(user_code, filename, tags, delete_all, delete_persistent) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def variables_snapshot_connection() -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def variables_snapshot_connect() -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_referer() -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def stash_data(data, expire) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def retrieve_stashed_data(key, secret, delete, refresh) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def secure_filename_spaces_ok(filename) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def secure_filename_unicode_ok(the_filename) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def secure_filename(filename) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def transform_json_variables(obj) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_login_url(kwargs) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def server_run_action_in_session(kwargs) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def server_invite_user(email_address, privilege, send) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_url() -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def release_lock(user_code, filename) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def register_db(db_name) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def create_objects_in_db(db_name) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_cloud() -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def cloud_custom(provider, config) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def google_api() -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_mail_class() -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_celery_app() -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def get_task(obj) -> Any:
    raise NotImplementedError("Not implemented")

@hookimpl(trylast=True)
def chord(arg) -> Any:
    raise NotImplementedError("Not implemented")

# @hookimpl(trylast=True)
# def fix_ml_files(playground_number, current_project) -> Any:
#     return None

# @hookimpl(trylast=True)
# def write_ml_source(playground, playground_number, current_project, filename, finalize) -> Any:
#     return None

# @hookimpl(trylast=True)
# def ensure_training_loaded(interview) -> Any:
#     return None

# @hookimpl(trylast=True)
# def manage_chat_logs(mode: int, kwargs: dict) -> None:
#     return None

# @hookimpl(trylast=True)
# def manage_global_objects(mode: int, kwargs: dict) -> None:
#     return None

# @hookimpl(trylast=True)
# def manage_email_server_objects(mode: int, kwargs: dict) -> None:
#     return None

# @hookimpl(trylast=True)
# def manage_tts_objects(mode: int, kwargs: dict) -> None:
#     return None

@hookimpl(trylast=True)
def get_chat_log_internal(chat_mode, yaml_filename, session_id, user_id, temp_user_id, secret, self_user_id, self_temp_id) -> list:
    return []

@hookimpl(trylast=True)
def get_ml_info(varname, default_package, default_file) -> Any:
    raise NotImplementedError("Not implemented")
