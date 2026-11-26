from .base import PermissionException, BaseException, BaseExceptionResponse, UserDontFind, DBError, RedisError
from .beyonder import PathDontEnterException, UpseqError, SeqBusyException, UpseqNotComeException, DontBeyonderException, ALreadyBeyonderException, SeqDontExistException, MethodActionFullStudyError, HaveActivityPointsError
from .wiki import DontSearchException, PathDontEnterFilterException
from .question import (
    QuestionDontFindException,
    AnswerDontFindException,
    QuestionAlreadyAnsweredException,
    QuestionDailyLimitException,
)
from .item import ItemDontFindException, ItemQuantityException
from .organ import DontMemberError, ALreadyOwnerError, DontEnterPurposeError, ExistRankError, ExistOrganError, InOneOrganError, ALreadyMemberError, OrganPermissioError, OrganPermissionNewRankError, OrganPermissionPurposeRankError, ClosenOrganError, HiddenOrganError
from .logs import DontLogFileException, DontHavePermissionException, DontExistCategoryException
from .newspaper import ExistNewsPaperError, ReaderError, NewsPaperPermissioError
from .setting import ParametrValidateError, ParametrExistError, RankValidateError, ChoisesValidateError

exceptions: list[type[BaseException]] = [
    SeqDontExistException,
    PermissionException,
    UserDontFind,
    DBError, 
    RedisError,
    PathDontEnterException,
    DontSearchException,
    UpseqNotComeException,
    DontBeyonderException,
    BaseException,
    ALreadyBeyonderException,
    PathDontEnterFilterException,
    DontMemberError, 
    InOneOrganError, 
    ALreadyMemberError, 
    OrganPermissioError, 
    OrganPermissionNewRankError, 
    OrganPermissionPurposeRankError,
    ExistOrganError, 
    ClosenOrganError, 
    HiddenOrganError,
    ExistRankError, 
    ALreadyOwnerError, 
    DontEnterPurposeError,
    RankValidateError,
    ParametrExistError,
    ChoisesValidateError,
    ParametrValidateError,
    SeqBusyException,
    DontLogFileException, 
    DontHavePermissionException, 
    DontExistCategoryException,
    ExistNewsPaperError,
    ReaderError,
    NewsPaperPermissioError,
    QuestionDontFindException,
    AnswerDontFindException,
    QuestionAlreadyAnsweredException,
    QuestionDailyLimitException,
    ItemDontFindException,
    ItemQuantityException,
    MethodActionFullStudyError,
    HaveActivityPointsError,
    UpseqError
]

exception_codes = {e.status_code:e for e in exceptions}

def get_exception_codes(codes: list[int] | None = None, types: list[str] | None = None):
    base = {PermissionException.status_code:{'description':PermissionException.default_message, 'model':PermissionException.model_response}}
    if codes:
        return base | {k:{'description':v.default_message, 'model':v.model_response} for k,v in exception_codes.items() if k in codes} 
    elif types:    
        return base | {k:{'description':v.default_message, 'model':v.model_response} for k,v in exception_codes.items() if v.type() in types} 
    else:
        return {k:{'description':v.default_message, 'model':v.model_response} for k,v in exception_codes.items()} 