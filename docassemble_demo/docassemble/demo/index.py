from docassemble.base.util import store_variables_snapshot, DAObject, user_info, start_time, variables_snapshot_connection

__all__ = ['MyIndex']


class MyIndex(DAObject):

    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        if not hasattr(self, 'data'):
            self.data = {}
        if not hasattr(self, 'key'):
            self.key = 'myindex'

    def save(self):
        data = dict(self.data)
        data['session'] = user_info().session
        data['filename'] = user_info().filename
        data['start_time'] = start_time().astimezone()
        store_variables_snapshot(data, key=self.key)

    def set(self, data):
        if not isinstance(data, dict):
            raise Exception("MyIndex.set: data parameter must be a dictionary")
        self.data = data
        self.save()

    def update(self, new_data):
        self.data.update(new_data)
        self.save()

    def report(self, filter_by=None, order_by=None):
        if filter_by is None:
            filter_string = ''
        else:
            filter_string = ' and ' + filter_by
        if order_by is None:
            order_string = ''
        else:
            order_string = ' order by ' + order_by
        conn = variables_snapshot_connection()
        with conn.cursor() as cur:
            cur.execute("select data from jsonstorage where tags='" + self.key + "'" + filter_string + order_string)
            results = [record[0] for record in cur.fetchall()]
        conn.close()
        return results
