# user/middleware.py
import logging
from django.utils import timezone
from .models import UserSession

logger = logging.getLogger(__name__)


class SessionActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Обновляем активность сессии для аутентифицированных пользователей
        if request.user.is_authenticated:
            session_id = request.META.get('HTTP_X_SESSION_ID')
            if session_id:
                try:
                    session = UserSession.objects.get(
                        id=session_id,
                        user=request.user,
                        is_active=True
                    )
                    session.last_activity = timezone.now()
                    session.save()
                    request.current_session_id = session_id
                except UserSession.DoesNotExist:
                    pass

        return response