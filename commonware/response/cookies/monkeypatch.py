"""Monkey-patch secure and httponly cookies into Django by default.

Enable this by adding ``commonware.response.cookies`` to your INSTALLED_APPS.

You can exempt every cookie by passing secure=False or httponly=False,
respectively:

    response.set_cookie('hello', value='world', secure=False, httponly=False)

To disable either of these patches, set COOKIES_SECURE = False or
COOKIES_HTTPONLY = False in settings.py.

Note: The httponly flag on cookies requires Python 2.6. Patches welcome.
"""

from functools import wraps
import os

from django.conf import settings
from django.http import HttpResponse


def set_cookie_secure(f):
    """
    Decorator for HttpResponse.set_cookie to enable httponly and secure
    for cookies by default.
    """
    @wraps(f)
    def wrapped(self, *args, **kwargs):
        # Default to secure=True unless:
        # - feature disabled or
        # - secure=* defined in set_cookie call or
        # - this is not an HTTPS request.
        if (getattr(settings, 'COOKIES_SECURE', None) != False and
            not 'secure' in kwargs and
            os.environ.get('HTTPS') == 'on'):
            kwargs['secure'] = True

        # Set httponly flag unless feature disabled. Defaults to httponly=True
        # unless httponly=* was defined in set_cookie call.
        httponly = None
        if getattr(settings, 'COOKIES_HTTPONLY', None) != False:
            if 'httponly' in kwargs:
                httponly = kwargs['httponly']
                del kwargs['httponly']
            else:
                httponly = True

        r = f(self, *args, **kwargs)

        if httponly:
            key = kwargs.get('key') or args[0]
            self.cookies[key]['httponly'] = httponly

        return r
    return wrapped

HttpResponse.set_cookie = set_cookie_secure(HttpResponse.set_cookie)
