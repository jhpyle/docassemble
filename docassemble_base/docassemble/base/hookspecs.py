# mypy: disable-error-code="empty-body"
# pylint: disable=unused-argument

from typing import Any
import pluggy

hookspec = pluggy.HookspecMarker("docassemble")

@hookspec(firstresult=True)
def get_default_language() -> str:
    """Default language"""

@hookspec(firstresult=True)
def get_default_dialect() -> str:
    """Default dialect"""

@hookspec(firstresult=True)
def get_default_locale() -> str:
    """Default locale"""

@hookspec(firstresult=True)
def get_default_voice() -> str:
    """Default voice"""

@hookspec(firstresult=True)
def get_default_timezone() -> str:
    """Return the default timezone string for the server.

    Returns the server's local timezone unless a default timezone is configured
    in the docassemble configuration.

    Returns:
        str: A timezone string such as ``'America/New_York'``.
    """

@hookspec(firstresult=True)
def get_default_country() -> str:
    """Default country"""

@hookspec(firstresult=True)
def get_configuration() -> dict:
    """Get configuration"""

@hookspec(firstresult=True)
def get_hostname() -> str:
    """Get hostname"""

@hookspec(firstresult=True)
def get_debug_status() -> bool:
    """Get debug status"""

@hookspec(firstresult=True)
def save_numbered_file(filename, orig_path, yaml_file_name, uid) -> tuple:
    """Save numbered file"""

@hookspec(firstresult=True)
def send_mail(the_message, config) -> None:
    """Send email"""

@hookspec(firstresult=True)
def absolute_filename(the_file) -> Any:
    """Get SavedFile or None for a file path"""

@hookspec(firstresult=True)
def write_record(key, data) -> int:
    """Store data in the SQL database under the given key.

    Args:
        key (str): A string key to associate with the record.
        data: The data to store. Must be pickleable.

    Returns:
        int: The unique integer ID of the saved record.
    """

@hookspec(firstresult=True)
def read_records(key) -> Any:
    """Return all records stored under the given key.

    Args:
        key (str): The string key used when calling ``write_record()``.

    Returns:
        dict: A dictionary mapping unique integer record IDs to the stored data.
    """

@hookspec(firstresult=True)
def delete_record(key, the_id) -> Any:
    """Delete a record from the SQL database by key and ID.

    Args:
        key (str): The string key associated with the record.
        the_id (int): The unique integer ID of the record to delete.
    """

@hookspec(firstresult=True)
def generate_csrf(secret_key, token_key) -> Any:
    """Generate CSRF token"""

@hookspec(firstresult=True)
def url_for(endpoint, kwargs) -> Any:
    """Wrapper for flask url_for function; kwargs is a dict of keyword arguments"""

@hookspec(firstresult=True)
def get_new_file_number(user_code, file_name, yaml_file_name) -> Any:
    """Returns file number for a file"""

@hookspec(firstresult=True)
def get_ext_and_mimetype(filename) -> Any:
    """Returns file extension and mimetype"""

@hookspec(firstresult=True)
def file_finder(file_reference, question, folder, package, filename, return_nonexistent, uids) -> Any:
    """General-purpose retriever of a file by its reference"""

@hookspec(firstresult=True)
def file_number_finder(file_number, filename, uids, privileged) -> Any:
    """Returns information about a file based on its number"""

@hookspec(firstresult=True)
def server_sql_get(key, secret) -> Any:
    pass

@hookspec(firstresult=True)
def server_sql_defined(key) -> Any:
    pass

@hookspec(firstresult=True)
def server_sql_set(key, val, encrypted, secret, the_user_id) -> Any:
    pass

@hookspec(firstresult=True)
def server_sql_delete(key) -> Any:
    pass

@hookspec(firstresult=True)
def server_sql_keys(prefix) -> Any:
    pass

@hookspec(firstresult=True)
def alchemy_url(db_config) -> Any:
    pass

@hookspec(firstresult=True)
def connect_args(db_config) -> Any:
    pass

@hookspec(firstresult=True)
def get_default_table_class() -> Any:
    pass

@hookspec(firstresult=True)
def get_default_thead_class() -> Any:
    pass

@hookspec(firstresult=True)
def to_text(html_doc) -> Any:
    pass

@hookspec(firstresult=True)
def url_finder(file_reference, kwargs) -> Any:
    """Find a URL for a file reference; kwargs is a dict of keyword arguments"""

@hookspec(firstresult=True)
def navigation_bar(nav, interview, wrapper, inner_div_class, inner_div_extra, show_links, hide_inactive_subs, a_class, show_nesting, include_arrows, always_open, return_dict) -> Any:
    pass

@hookspec(firstresult=True)
def chat_partners_available(session_id, yaml_filename, the_user_id, mode, partner_roles) -> Any:
    pass

@hookspec(firstresult=True)
def get_chat_log(yaml_filename, session_id, secret, utc, timezone) -> Any:
    pass

@hookspec(firstresult=True)
def sms_body(phone_number, body, config) -> Any:
    pass

@hookspec(firstresult=True)
def send_fax(fax_number, the_file, config, country) -> Any:
    pass

@hookspec(firstresult=True)
def get_sms_session(phone_number, config) -> Any:
    pass

@hookspec(firstresult=True)
def initiate_sms_session(phone_number, yaml_filename, uid, secret, encrypted, user_id, email, new, config) -> Any:
    pass

@hookspec(firstresult=True)
def terminate_sms_session(phone_number, config) -> Any:
    pass

@hookspec(firstresult=True)
def applock(action, application, maxtime) -> Any:
    pass

@hookspec(firstresult=True)
def get_twilio_config() -> Any:
    pass

@hookspec(firstresult=True)
def get_server_redis() -> Any:
    pass

@hookspec(firstresult=True)
def get_server_redis_user() -> Any:
    pass

@hookspec(firstresult=True)
def get_user_object(user_id) -> Any:
    pass

@hookspec(firstresult=True)
def user_id_dict() -> Any:
    pass

@hookspec(firstresult=True)
def retrieve_email(email_id) -> Any:
    pass

@hookspec(firstresult=True)
def retrieve_emails(kwargs) -> Any:
    """Retrieve emails; kwargs is a dict of keyword arguments"""

@hookspec(firstresult=True)
def get_short_code(kwargs) -> Any:
    """Get short code; kwargs is a dict of keyword arguments"""

@hookspec(firstresult=True)
def make_png_for_pdf(doc, prefix, page) -> Any:
    pass

@hookspec(firstresult=True)
def ocr_google_in_background(image_file, raw_result, user_code) -> Any:
    pass

@hookspec(firstresult=True)
def task_ready(task_id) -> Any:
    pass

@hookspec(firstresult=True)
def wait_for_task(task_id, timeout) -> Any:
    pass

@hookspec(firstresult=True)
def user_interviews(user_id, secret, exclude_invalid, action, filename, session, tag, include_dict, delete_shared, admin, start_id, temp_user_id, query, minimal) -> Any:
    pass

@hookspec(firstresult=True)
def server_interview_menu(absolute_urls, start_new, tag) -> Any:
    pass

@hookspec(firstresult=True)
def server_get_user_list(include_inactive, start_id) -> Any:
    pass

@hookspec(firstresult=True)
def server_get_user_info(user_id, email, case_sensitive, admin) -> Any:
    pass

@hookspec(firstresult=True)
def server_set_user_info(kwargs) -> Any:
    """Set user info; kwargs is a dict of keyword arguments"""

@hookspec(firstresult=True)
def make_user_inactive(user_id, email) -> Any:
    pass

@hookspec(firstresult=True)
def server_get_secret(username, password, case_sensitive) -> Any:
    pass

@hookspec(firstresult=True)
def server_get_session_variables(yaml_filename, session_id, secret, simplify, use_lock) -> Any:
    pass

@hookspec(firstresult=True)
def server_go_back_in_session(yaml_filename, session_id, secret, return_question, use_lock, encode) -> Any:
    pass

@hookspec(firstresult=True)
def server_create_session(yaml_filename, secret, url_args, referer, req) -> Any:
    pass

@hookspec(firstresult=True)
def server_set_session_variables(yaml_filename, session_id, variables, secret, return_question, literal_variables, del_variables, question_name, event_list, advance_progress_meter, post_setting, use_lock, encode, process_objects) -> Any:
    pass

@hookspec(firstresult=True)
def get_privileges_list(admin) -> Any:
    pass

@hookspec(firstresult=True)
def add_privilege(privilege) -> Any:
    pass

@hookspec(firstresult=True)
def remove_privilege(privilege) -> Any:
    pass

@hookspec(firstresult=True)
def add_user_privilege(user_id, privilege) -> Any:
    pass

@hookspec(firstresult=True)
def remove_user_privilege(user_id, privilege) -> Any:
    pass

@hookspec(firstresult=True)
def get_permissions_of_privilege(privilege, privileged) -> Any:
    pass

@hookspec(firstresult=True)
def server_create_user(email, password, privileges, info) -> Any:
    pass

@hookspec(firstresult=True)
def file_set_attributes(file_number, private, persistent, session, filename) -> Any:
    """Set attributes on a stored file"""

@hookspec(firstresult=True)
def file_user_access(file_number, allow_user_id, allow_email, disallow_user_id, disallow_email, disallow_all) -> Any:
    pass

@hookspec(firstresult=True)
def file_privilege_access(file_number, allow, disallow, disallow_all) -> Any:
    pass

@hookspec(firstresult=True)
def fg_make_png_for_pdf(doc, prefix, page) -> Any:
    pass

@hookspec(firstresult=True)
def fg_make_png_for_pdf_path(path, prefix, page) -> Any:
    pass

@hookspec(firstresult=True)
def fg_make_pdf_for_word_path(path, extension) -> Any:
    pass

@hookspec(firstresult=True)
def server_get_question_data(yaml_filename, session_id, secret, use_lock, user_dict, steps, is_encrypted, old_user_dict, save, post_setting, advance_progress_meter, action, encode) -> Any:
    pass

@hookspec(firstresult=True)
def fix_pickle_obj(data) -> Any:
    pass

@hookspec(firstresult=True)
def get_main_page_parts() -> Any:
    pass

@hookspec(firstresult=True)
def get_saved_file_class() -> Any:
    pass

@hookspec(firstresult=True)
def path_from_reference(file_reference) -> Any:
    pass

@hookspec(firstresult=True)
def get_button_class_prefix() -> Any:
    pass

@hookspec(firstresult=True)
def write_answer_json(user_code, filename, data, tags, persistent) -> Any:
    pass

@hookspec(firstresult=True)
def read_answer_json(user_code, filename, tags, all_tags) -> Any:
    pass

@hookspec(firstresult=True)
def delete_answer_json(user_code, filename, tags, delete_all, delete_persistent) -> Any:
    pass

@hookspec(firstresult=True)
def variables_snapshot_connection() -> Any:
    pass

@hookspec(firstresult=True)
def variables_snapshot_connect() -> Any:
    pass

@hookspec(firstresult=True)
def get_referer() -> Any:
    pass

@hookspec(firstresult=True)
def stash_data(data, expire) -> Any:
    pass

@hookspec(firstresult=True)
def retrieve_stashed_data(key, secret, delete, refresh) -> Any:
    pass

@hookspec(firstresult=True)
def secure_filename_spaces_ok(filename) -> Any:
    pass

@hookspec(firstresult=True)
def secure_filename_unicode_ok(the_filename) -> Any:
    pass

@hookspec(firstresult=True)
def secure_filename(filename) -> Any:
    pass

@hookspec(firstresult=True)
def transform_json_variables(obj) -> Any:
    pass

@hookspec(firstresult=True)
def get_login_url(kwargs) -> Any:
    """Get login URL; kwargs is a dict of keyword arguments"""

@hookspec(firstresult=True)
def server_run_action_in_session(kwargs) -> Any:
    """Run action in session; kwargs is a dict of keyword arguments"""

@hookspec(firstresult=True)
def server_invite_user(email_address, privilege, send) -> Any:
    pass

@hookspec(firstresult=True)
def get_url() -> Any:
    pass

@hookspec(firstresult=True)
def release_lock(user_code, filename) -> Any:
    pass

@hookspec(firstresult=True)
def register_db(db_name) -> Any:
    pass

@hookspec(firstresult=True)
def create_objects_in_db(db_name) -> Any:
    pass

@hookspec(firstresult=True)
def get_cloud() -> Any:
    pass

@hookspec(firstresult=True)
def cloud_custom(provider, config) -> Any:
    pass

@hookspec(firstresult=True)
def google_api() -> Any:
    pass

@hookspec(firstresult=True)
def get_mail_class() -> Any:
    pass

@hookspec(firstresult=True)
def get_celery_app() -> Any:
    pass

@hookspec(firstresult=True)
def get_task(obj) -> Any:
    pass

@hookspec(firstresult=True)
def chord(arg) -> Any:
    pass

@hookspec(firstresult=True)
def fix_ml_files(playground_number, current_project) -> Any:
    pass

@hookspec(firstresult=True)
def write_ml_source(playground, playground_number, current_project, filename, finalize) -> Any:
    pass

@hookspec(firstresult=True)
def ensure_training_loaded(interview) -> Any:
    pass

@hookspec(firstresult=True)
def manage_chat_logs(mode: int, kwargs: dict) -> None:
    pass

@hookspec(firstresult=True)
def manage_global_objects(mode: int, kwargs: dict) -> None:
    pass

@hookspec(firstresult=True)
def manage_email_server_objects(mode: int, kwargs: dict) -> None:
    pass

@hookspec(firstresult=True)
def manage_tts_objects(mode: int, kwargs: dict) -> None:
    pass

@hookspec(firstresult=True)
def get_chat_log_internal(chat_mode, yaml_filename, session_id, user_id, temp_user_id, secret, self_user_id, self_temp_id) -> Any:
    pass

@hookspec(firstresult=True)
def get_ml_info(varname, default_package, default_file) -> Any:
    pass

@hookspec(firstresult=True)
def devel_login() -> Any:
    pass
