import os
from docassemble.base.config import daconfig

SOCKET_PATH = daconfig.get('nltk socket', '/var/run/nltk/da_nltk.sock')
if os.path.exists(SOCKET_PATH):
    import socket
    import struct
    import threading
    import msgpack
    from types import SimpleNamespace
    _local = threading.local()

    def _get_conn():
        if not getattr(_local, 'sock', None):
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(SOCKET_PATH)
            _local.sock = s
        return _local.sock

    def _call(lang, method, pargs, kwargs):
        sock = _get_conn()
        payload = msgpack.packb([lang, method, pargs, kwargs])
        sock.sendall(struct.pack('>I', len(payload)) + payload)
        header = _recvexactly(sock, 4)
        n = struct.unpack('>I', header)[0]
        response = msgpack.unpackb(_recvexactly(sock, n))
        if 'error' in response:
            raise RuntimeError(response['error'])
        return response['result']

    def _recvexactly(sock, n):
        buf = b''
        while len(buf) < n:
            chunk = sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError('daemon closed connection')
            buf += chunk
        return buf

    def nltk_func(lang, method):
        def func(*pargs, **kwargs):
            return _call(lang, method, pargs, kwargs)
        return func

    pattern_de = SimpleNamespace()
    pattern_en = SimpleNamespace()
    pattern_es = SimpleNamespace()
    pattern_fr = SimpleNamespace()
    pattern_it = SimpleNamespace()
    pattern_nl = SimpleNamespace()
    pattern_de.article = nltk_func('de', 'article')
    pattern_de.conjugate = nltk_func('de', 'conjugate')
    pattern_de.pluralize = nltk_func('de', 'pluralize')
    pattern_de.singularize = nltk_func('de', 'singularize')
    pattern_en.article = nltk_func('en', 'article')
    pattern_en.conjugate = nltk_func('en', 'conjugate')
    pattern_en.pluralize = nltk_func('en', 'pluralize')
    pattern_en.singularize = nltk_func('en', 'singularize')
    pattern_es.article = nltk_func('es', 'article')
    pattern_es.conjugate = nltk_func('es', 'conjugate')
    pattern_es.pluralize = nltk_func('es', 'pluralize')
    pattern_es.singularize = nltk_func('es', 'singularize')
    pattern_fr.article = nltk_func('fr', 'article')
    pattern_fr.conjugate = nltk_func('fr', 'conjugate')
    pattern_fr.pluralize = nltk_func('fr', 'pluralize')
    pattern_fr.singularize = nltk_func('fr', 'singularize')
    pattern_it.article = nltk_func('it', 'article')
    pattern_it.conjugate = nltk_func('it', 'conjugate')
    pattern_it.pluralize = nltk_func('it', 'pluralize')
    pattern_it.singularize = nltk_func('it', 'singularize')
    pattern_nl.article = nltk_func('nl', 'article')
    pattern_nl.conjugate = nltk_func('nl', 'conjugate')
    pattern_nl.pluralize = nltk_func('nl', 'pluralize')
    pattern_nl.singularize = nltk_func('nl', 'singularize')
else:
    import nltk
    try:
        if not os.path.isfile(os.path.join(nltk.data.path[0], 'corpora', 'omw-1.4.zip')):
            nltk.download('omw-1.4')
    except:
        pass
    try:
        if not os.path.isfile(os.path.join(nltk.data.path[0], 'corpora', 'wordnet.zip')):
            nltk.download('wordnet')
    except:
        pass
    try:
        if not os.path.isfile(os.path.join(nltk.data.path[0], 'corpora', 'wordnet_ic.zip')):
            nltk.download('wordnet_ic')
    except:
        pass
    try:
        if not os.path.isfile(os.path.join(nltk.data.path[0], 'corpora', 'sentiwordnet.zip')):
            nltk.download('sentiwordnet')
    except:
        pass
    import docassemble_pattern.en  # pylint: disable=import-error,no-name-in-module
    import docassemble_pattern.es  # pylint: disable=import-error,no-name-in-module
    import docassemble_pattern.de  # pylint: disable=import-error,no-name-in-module
    import docassemble_pattern.fr  # pylint: disable=import-error,no-name-in-module
    import docassemble_pattern.it  # pylint: disable=import-error,no-name-in-module
    import docassemble_pattern.nl  # pylint: disable=import-error,no-name-in-module

    pattern_en = docassemble_pattern.en
    pattern_es = docassemble_pattern.es
    pattern_de = docassemble_pattern.de
    pattern_fr = docassemble_pattern.fr
    pattern_it = docassemble_pattern.it
    pattern_nl = docassemble_pattern.nl
