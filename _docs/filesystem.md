To do:

* Replace file upload storage with WebDAV
* Replace touching of the WSGI file with redis or memcached
* Replace playground storage with WebDAV
* Replace uploading of ZIP file with WebDAV
* When a user updates a Python package, there should be a queue in
  redis that all servers have to follow where they fetch from GitHub
  or from WebDAV
