from paste import httpserver as HS
from paste.request import parse_formvars as PF
from paste.response import HeaderDict as HD
import threading
from webob import Request as RQ
from webob import Response as RP

webinfo = threading.local()


class Capitalizer(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        req = RQ(environ)
        resp = req.get_response(self.app)
        resp.body = resp.body.upper()
        return resp(environ, start_response)


class AuthMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        req = RQ(environ)
        for item in req.headers.iteritems():
          print item
        if not self.authorized(req.headers['authorization']):
            resp = self.auth_required(req)
        else:
            resp = self.app
        return resp(environ, start_response)

    def authorized(self, header):
        if not header:
            return False
        auth_type, encoded = header.split(None, 1)
        if not auth_type.lower() == 'basic':
            return False
        username, password = encoded.decode('base64').split(':', 1)
        return self.check_password(username, password)

    def check_password(self, username, password):
        return username == password

    def auth_required(self, req):
        return RP(status=401, headers={'WWW-Authenticate': 'Basic realm="this realm"'},
                         body="""\
         <html>
          <head><title>Authentication Required</title></head>
          <body>
           <h1>Authentication Required</h1>
           If you can't get in, then stay out.
          </body>
         </html>""")


class Request(object):

  def __init__(self, environ):
    self.environ = environ
    self.fields = PF(environ)


class Response(object):

  def __init__(self):
    self.headers = HD({'content-type': 'text/html',
                       'User-Agent': 'Mozilla/5.0'})


class ObjectPublisher(object):

  def __init__(self, root):
    self.root = root

  def __call__(self, environ, start_response):
    webinfo.request = Request(environ)
    webinfo.response = Response()
    obj = self.find_object(self.root, environ)
    response_body = obj(**dict(webinfo.request.fields))
    start_response('200 OK', webinfo.response.headers.items())
    return [response_body]

  def find_object(self, obj, environ):
      path_info = environ.get('PATH_INFO', '')
      if not path_info or path_info == '/':
          # We've arrived!
          return obj
      # PATH_INFO always starts with a /, so we'll get rid of it:
      path_info = path_info.lstrip('/')
      # Then split the path into the "next" chunk, and everything
      # after it ("rest"):
      parts = path_info.split('/', 1)
      next = parts[0]
      if len(parts) == 1:
          rest = ''
      else:
          rest = '/' + parts[1]
      # Hide private methods/attributes:
      assert not next.startswith('_')
      # Now we get the attribute; getattr(a, 'b') is equivalent
      # to a.b...
      next_obj = getattr(obj, next)
      # Now fix up SCRIPT_NAME and PATH_INFO...
      environ['SCRIPT_NAME'] += '/' + next
      environ['PATH_INFO'] = rest
      # and now parse the remaining part of the URL...
      return self.find_object(next_obj, environ)


class Root(object):
  def __call__(self):
    return '''
    <form action = "welcome">
    Name - <input type="text" name="name">
    <input type="submit">
    </form>
    '''

  def welcome(self, name):
    return 'Hello %s!' % name

app = ObjectPublisher(Root())
wrapped = AuthMiddleware(app)


if __name__ == '__main__':
  HS.serve(wrapped, host='127.0.0.1', port='8080')


