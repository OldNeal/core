from pydantic import Field
from app.validate.api.base import AnswerBaseBody, AnswerBody, BaseAPIValidate, Page, QueryBody

class QustionBase(BaseAPIValidate):
    body: str
    description: str | None = None
    difficulty: int = Field(5, default=1, ge=1, le=10)
    tags: list[str] = Field([], default_factory=list)

class QuestionCreate(QustionBase):
    correct_answers: list[str]
    incorrect_answers: list[str]

class QueryQuestionCreate(QueryBody):
    purpose_user_id: int | None = None
    question: QuestionCreate

class QuestionAnswerUpdate(BaseAPIValidate):
    answer_id: int | None = None
    body: str
    is_correct: bool

class QuestionUpdate(BaseAPIValidate):
    question_id: int
    name: str | None = None
    description: str | None = None
    difficulty: int | None = Field(default=None, ge=1, le=10)
    tags: list[str] | None = None
    answers: list[QuestionAnswerUpdate] | None = None

class QueryQuestionUpdate(QueryBody):
    question: QuestionUpdate

class QuestionAnswer(BaseAPIValidate):
    answer_id: int
    body: str
    is_correct: bool | None = None

class Question(QustionBase):
    question_id: int
    answers: list[QuestionAnswer]

class AnswerQuestionAnswer(AnswerBody):
    answer_id: int
    is_correct: bool
    question: Question
    activity_points: int = 0 

class AnswerQuestion(AnswerBody):
    question: Question
    activity_points: int = 0

class AnswerAllQuestions(AnswerBaseBody):
    questions: list[Question]
    page: Page | None = None
    count: int = 0

class AnswerRandomQuestion(AnswerBaseBody):
    question: Question

class AnswerQuestionSearch(AnswerAllQuestions):
    search_value: str

class QuestionAnswerStatistics(QuestionAnswer):
    count: int

class AnswerQuestionStatistics(AnswerBody):
    question_id: int
    answers: list[QuestionAnswerStatistics]
    statistics: 'UserQuestionStatistics'

class UserQuestionStatistics(BaseAPIValidate):
    total: int
    correct: int
    incorrect: int
    accuracy: float

class AnswerUserQuestionStatistics(AnswerBody):
    statistics: UserQuestionStatistics

class AnswerQuestionLimit(AnswerBaseBody):
    used: int = 0
    limit: int = 0
    remaining: int = 0
    ttl: int = 0
