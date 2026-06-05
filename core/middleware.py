import logging

from django.db import IntegrityError

from .models import Profile

logger = logging.getLogger('puddle.auth')


class EnsureProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                Profile.objects.get_or_create(user=request.user)
            except IntegrityError:
                pass
        return self.get_response(request)


class SessionDebugMiddleware:
    """
    Sits BEFORE SessionMiddleware in the list → its __call__ wraps the full
    chain including SessionMiddleware.process_response(). The 'response'
    object we see already has the final Set-Cookie headers applied.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        cookie_in = request.COOKIES.get('sessionid', 'MISSING')

        # Full inner chain runs here (including SessionMiddleware.process_response)
        response = self.get_response(request)

        # Now check what SessionMiddleware put in Set-Cookie
        set_cookie_headers = []
        for key, morsel in response.cookies.items():
            if key == 'sessionid':
                max_age = morsel.get('max-age', '?')
                value   = morsel.coded_value[:12] if morsel.coded_value else 'EMPTY'
                set_cookie_headers.append(f'Set-Cookie sessionid={value}... Max-Age={max_age}')

        cookie_action = set_cookie_headers[0] if set_cookie_headers else 'no Set-Cookie for sessionid'

        logger.warning(
            '%s %s | req_cookie=%s | status=%s | %s',
            request.method,
            request.path,
            cookie_in[:12] if cookie_in != 'MISSING' else 'MISSING',
            response.status_code,
            cookie_action,
        )

        return response
