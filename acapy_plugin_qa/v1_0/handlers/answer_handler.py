from aries_cloudagent.messaging.base_handler import BaseHandler
from aries_cloudagent.messaging.request_context import RequestContext
from aries_cloudagent.messaging.responder import BaseResponder
from aries_cloudagent.core.profile import Profile

from ..messages.answer import Answer


class AnswerHandler(BaseHandler):
    """Handler for Answer message."""

    # TODO: check these variables
    RECEIVED_TOPIC = "acapy::questionanswer::received"
    WEBHOOK_TOPIC = "acapy::webhook::questionanswer"

    async def handle(self, context: RequestContext, responder: BaseResponder):
        """Handle answer message."""

        """Handle question message."""
        await self.qa_notify(context.profile, context.message)

    @staticmethod
    def qa_notify(profile: Profile, answer: Answer):
        # print(context.message)
        # await responder.send_reply(context.message)
        assert isinstance(answer, Answer)
        self._logger.debug(
            "Received answer in thread %s " "with text: %s",
            answer._thread,
            answer.response,
        )
        # Emit a webhook
        await context.profile.notify(
            self.WEBHOOK_TOPIC,
            {
                "thread_id": answer._thread,
                "response": answer.response,
            },
        )

        # Emit an event
        await context.profile.notify(
            self.RECEIVED_TOPIC,
            {
                "thread_id": answer._thread,
                "response": answer.response,
            },
        )
