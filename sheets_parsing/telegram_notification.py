from notifiers import get_notifier
from telegram_config import token, chat_id


def send_notification(message: str):
    """
    :param message: Уведомление которое отправится в чат
    :return:
    """
    # Функция отправляющая уведомления
    telegram = get_notifier("telegram")
    telegram.notify(token=token, chat_id=chat_id, message=message)
