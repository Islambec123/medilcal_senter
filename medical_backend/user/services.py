import logging
from django.utils import timezone
from .models import UserSession

logger = logging.getLogger(__name__)


class SessionService:
    @staticmethod
    def create_session(user, refresh_token, request=None):
        """Создаем новую сессию"""
        try:
            user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
            ip_address = request.META.get('REMOTE_ADDR') if request else None

            session = UserSession.objects.create(
                user=user,
                refresh_token=refresh_token,
                user_agent=user_agent,
                ip_address=ip_address
            )

            logger.info(f"Session created for user {user.email} from IP {ip_address}")
            return session
        except Exception as e:
            logger.error(f"Error creating session for {user.email}: {str(e)}")
            return None

    @staticmethod
    def get_active_sessions(user):
        """Получаем активные сессии пользователя"""
        try:
            return user.sessions.filter(is_active=True).order_by('-last_activity')
        except Exception as e:
            logger.error(f"Error getting sessions for {user.email}: {str(e)}")
            return UserSession.objects.none()

    @staticmethod
    def deactivate_session(session_id, user):
        """Деактивируем конкретную сессию"""
        try:
            session = UserSession.objects.get(id=session_id, user=user, is_active=True)
            session.is_active = False
            session.save()

            logger.info(f"Session {session_id} deactivated for user {user.email}")
            return True
        except UserSession.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Error deactivating session {session_id}: {str(e)}")
            return False

    @staticmethod
    def deactivate_all_sessions(user, exclude_session_id=None):
        """Деактивируем все сессии пользователя, кроме указанной"""
        try:
            sessions = user.sessions.filter(is_active=True)
            if exclude_session_id:
                sessions = sessions.exclude(id=exclude_session_id)

            count = sessions.update(is_active=False)
            logger.info(f"Deactivated {count} sessions for user {user.email}")
            return count
        except Exception as e:
            logger.error(f"Error deactivating sessions for {user.email}: {str(e)}")
            return 0