import logging

from aries_cloudagent.core.profile import Profile
from aries_cloudagent.core.error import BaseError

from .messages.question import Question
from .models.qa_exchange_record import QAExchangeRecord


class QAManagerError(BaseError):
    """Q&A Manager error"""


class QAManager:
    """Class for managing Q&A operations"""

    def __init__(self, profile: Profile):
        """Initialize a QAManager"""
        self.profile = profile
        self.logger = logging.getLogger(__name__)

    async def store_question(self, question: Question, connection_id: str):
        qa_exchange_record = QAExchangeRecord(
            # question_answer_id = question._id,
            thread_id=question._id,
            # thread_id=question._thread.thid if question._thread else question.id,
            # pthid=None,
            connection_id=connection_id,
            valid_responses=question.valid_responses,
            question_text=question.question_text,
            question_detail=question.question_detail,
        )

        async with self.profile.session() as session:
            await qa_exchange_record.save(session)

    async def retrieve_by_id(self, session, thread_id):
        return await QAExchangeRecord.retrieve_by_id(session, thread_id)

    async def delete_record(self, session, thread_id):
        record = await self.retrieve_by_id(session, thread_id)
        record.delete_record()
