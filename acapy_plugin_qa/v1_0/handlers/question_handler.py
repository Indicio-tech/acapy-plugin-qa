"""Question handler."""
from aries_cloudagent.messaging.base_handler import BaseHandler
from aries_cloudagent.messaging.request_context import RequestContext
from aries_cloudagent.messaging.responder import BaseResponder


from ..messages.question import Question
from ..models.qa_exchange_record import QAExchangeRecord


class QuestionHandler(BaseHandler):
    """Handler for Question message."""

    async def handle(self, context: RequestContext, responder: BaseResponder):
        """Handle question message."""
        assert isinstance(context.message, Question)
        self._logger.debug(
            "Received question in thread %s with text: %s",
            context.message._thread,
            context.message.question_text,
        )

        record = QAExchangeRecord(
            role=QAExchangeRecord.ROLE_RESPONDER,
            connection_id=context.connection_record.connection_id,
            thread_id=context.message._id,
            question_text=context.message.question_text,
            question_detail=context.message.question_detail,
            valid_responses=context.message.valid_responses,
        )
        async with context.session() as session:
            await record.save(session, reason="New question received")
