from aries_cloudagent.messaging.base_handler import BaseHandler
from aries_cloudagent.messaging.request_context import RequestContext
from aries_cloudagent.messaging.responder import BaseResponder

from ..messages.question import Question
from ..manager import QAManager


class QuestionHandler(BaseHandler):
    """Handler for Question message."""

    RECEIVED_TOPIC = "acapy::questionanswer::question_received"
    WEBHOOK_TOPIC = "acapy::webhook::questionanswer"

    async def handle(self, context: RequestContext, responder: BaseResponder):
        """Handle question message."""
        # print(context.message)
        # await responder.send_reply(context.message)
        assert isinstance(context.message, Question)
        self._logger.debug(
            "Received question in thread %s " "with text: %s",
            context.message._thread,
            context.message.question_text,
        )

        qa_manager = QAManager(context.profile)
        await qa_manager.store_question(
            context.message, context.connection_record.connection_id
        )

        # Emit a webhook
        await context.profile.notify(
            self.WEBHOOK_TOPIC,
            {
                "thread_id": context.message._thread,
                "question_text": context.message.question_text,
                "question_detail": context.message.question_detail,
                "valid_responses": context.message.valid_responses,
            },
        )

        # Emit an event
        await context.profile.notify(
            self.RECEIVED_TOPIC,
            {
                "thread_id": context.message._thread,
                "question_text": context.message.question_text,
                "question_detail": context.message.question_detail,
                "valid_responses": context.message.valid_responses,
            },
        )
