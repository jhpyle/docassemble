from docassemble.base.util import as_datetime, DAFile
from ics import Calendar, Event, Attendee, Organizer

__all__ = ['make_event']


def make_event(title=None, location=None, description=None, begin_date=None, begin_time=None, end_date=None, end_time=None, organizer=None, attendees=None):
    if attendees is None:
        attendees = []
    if title is None:
        raise Exception("make_event: a title parameter is required")
    if begin_date is None:
        raise Exception("make_event: a begin_date parameter is required")
    if begin_time is None:
        raise Exception("make_event: a begin_time parameter is required")
    if end_date is None:
        raise Exception("make_event: an end_date parameter is required")
    if end_time is None:
        raise Exception("make_event: an end_time parameter is required")
    c = Calendar()
    e = Event()
    if organizer is not None:
        e.organizer = Organizer(common_name=organizer.name.full(), email=organizer.email)
    if len(attendees) > 0:
        e.attendees = [Attendee(common_name=attendee.name.full(), email=attendee.email) for attendee in attendees]
    e.name = str(title)
    e.begin = as_datetime(begin_date.replace_time(begin_time), timezone='UTC').format_datetime('yyyy-MM-dd hh:mm:ss')
    e.end = as_datetime(end_date.replace_time(end_time), timezone='UTC').format_datetime('yyyy-MM-dd hh:mm:ss')
    if location not in (None, ''):
        e.location = str(location)
    if description not in (None, ''):
        e.description = str(description)
    c.events.add(e)
    c.events  # pylint: disable=pointless-statement
    ics_file = DAFile('ics_file')
    ics_file.set_random_instance_name()
    ics_file.initialize(filename="event.ics", mimetype="text/calendar")
    with open(ics_file.path(), 'w', encoding='utf-8') as f:
        f.write(str(c))
    ics_file.commit()
    return ics_file
