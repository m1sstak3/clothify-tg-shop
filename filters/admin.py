from aiogram.types import Message
from core.config import ADMIN_IDS

class IsAdmin:
    """Фильтр для проверки прав администратора."""
    def __call__(self, message: Message) -> bool:
        return message.from_user.id in ADMIN_IDS
