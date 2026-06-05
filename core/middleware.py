from .models import Profile


class EnsureProfileMiddleware:
    """
    Guarantees every authenticated user has a Profile record before any view
    or template runs. Prevents RelatedObjectDoesNotExist crashes in base.html
    which accesses request.user.profile on every page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Use a per-request flag to avoid hitting the DB on every middleware call
            if not getattr(request.user, '_profile_ensured', False):
                Profile.objects.get_or_create(user=request.user)
                request.user._profile_ensured = True

        return self.get_response(request)
