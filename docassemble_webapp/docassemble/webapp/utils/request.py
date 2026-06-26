from docassemble.webapp.config import HTTP_TO_HTTPS

def get_requester_ip(req):
    if not req:
        return '127.0.0.1'
    if HTTP_TO_HTTPS:
        if 'X-Real-Ip' in req.headers:
            return req.headers['X-Real-Ip']
        if 'X-Forwarded-For' in req.headers:
            return req.headers['X-Forwarded-For']
    return req.remote_addr
