from aries_cloudagent.messaging.base_handler import BaseHandler
from aries_cloudagent.messaging.request_context import RequestContext
from aries_cloudagent.messaging.responder import BaseResponder

from ..messages.question import Question

class QuestionHandler(BaseHandler):
    """Handler for Question message."""

    # TODO: check these variables
    RECIEVED_TOPIC = "acapy::questionanswer::received"
    WEBHOOK_TOPIC = "acapy::webhook::questionanswer"

    async def handle(self, context: RequestContext, responder: BaseResponder):
        """Handle question message."""
        assert isinstance(context.message, Question)
        self._logger.debug(
            "Received question in thread %s "
            "with text: %s",
            context.message.thread_id,
            context.message.question_text,
        )
        # Emit a webhook
        # TODO: check this check
        if context.settings.get("revocation.monitor_notification"):
            await context.profile.notify(
                self.WEBHOOK_TOPIC,
                {
                    "thread_id": context.message.thread_id,
                    "question_text": context.message.question_text,
                    "question_detail": context.message.question_detail,
                    "valid_responses": context.message.valid_responses,
                },
            )

        # Emit an event
        await context.profile.notify(
            self.RECIEVED_TOPIC,
            {
                "thread_id": context.message.thread_id,
                "question_text": context.message.question_text,
                "question_detail": context.message.question_detail,
                "valid_responses": context.message.valid_responses,
            },
        )
