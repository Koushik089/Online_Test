from django.utils import timezone
from datetime import timedelta


class StudentActivityMiddleware:
    """
    Updates UserProfile.last_activity on every authenticated request.
    Throttled to once per 60 seconds to avoid hammering the DB.
    Student is considered online if last_activity < 5 minutes ago.
    """

    THROTTLE_SECONDS = 60  # update DB at most once per minute per user

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            self._update_activity(request.user)
        return self.get_response(request)

    def _update_activity(self, user):
        try:
            profile = user.profile
            now = timezone.now()

            # Only hit the DB if last_activity is stale (older than throttle window)
            if (
                profile.last_activity is None
                or (now - profile.last_activity) > timedelta(seconds=self.THROTTLE_SECONDS)
            ):
                profile.last_activity = now
                profile.save(update_fields=['last_activity'])
        except Exception:
            # Never crash a request due to activity tracking failure
            pass
