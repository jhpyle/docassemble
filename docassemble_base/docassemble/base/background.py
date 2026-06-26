from docassemble.base.thread_context import this_thread
from docassemble.base.hooks import get_server_redis, get_celery_app, get_task


class BackgroundResult:

    def __init__(self, result):
        for attr in ('value', 'error_type', 'error_trace', 'error_message', 'variables'):
            if hasattr(result, attr):
                setattr(self, attr, getattr(result, attr))
            else:
                setattr(self, attr, None)


class MyAsyncResult:

    def wait(self):
        if not hasattr(self, '_cached_result'):
            self._cached_result = BackgroundResult(get_task(self.obj).get())
        return True

    def failed(self):
        if not hasattr(self, '_cached_result'):
            self._cached_result = BackgroundResult(get_task(self.obj).get())
        if self._cached_result.error_type is not None:
            return True
        return False

    def ready(self):
        return get_task(self.obj).ready()

    def result(self):
        if not hasattr(self, '_cached_result'):
            self._cached_result = BackgroundResult(get_task(self.obj).get())
        return self._cached_result

    def get(self):
        if not hasattr(self, '_cached_result'):
            self._cached_result = BackgroundResult(get_task(self.obj).get())
        return self._cached_result.value

    def revoke(self, terminate=True):
        return get_task(self.obj).revoke(terminate=terminate)

    def status(self):
        return get_task(self.obj).status

    def state(self):
        return get_task(self.obj).state

    def date_done(self):
        return get_task(self.obj).date_done


def bg_action(action, ui_notification, **kwargs):
    result = MyAsyncResult()
    result.obj = get_celery_app().signature('tasks.background_action', args=[this_thread.current_info['yaml_filename'], this_thread.current_info['user'], this_thread.current_info['session'], this_thread.current_info['secret'], this_thread.current_info['url'], this_thread.current_info['url_root'], {'action': action, 'arguments': kwargs}], kwargs={"extra": ui_notification}).delay()
    if ui_notification is not None:
        worker_key = 'da:worker:uid:' + str(this_thread.current_info['session']) + ':i:' + str(this_thread.current_info['yaml_filename']) + ':userid:' + str(this_thread.current_info['user']['the_user_id'])
        # logmessage("worker_caller: id is " + str(result.obj.id) + " and key is " + worker_key)
        get_server_redis().rpush(worker_key, result.obj.id)
    # logmessage("worker_caller: id is " + str(result.obj.id))
    return result
