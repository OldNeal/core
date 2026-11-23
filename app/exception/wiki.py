from app.exception.base import BaseException

class WikiException(BaseException):
    default_message = 'The wiki exception'
    
class DontSearchException(BaseException):
    default_message = 'Ничего не найдено'
    status_code = 433

class PathDontEnterFilterException(BaseException):
    default_message = 'Вы не указали ни имя, ни ID'
    status_code = 434

