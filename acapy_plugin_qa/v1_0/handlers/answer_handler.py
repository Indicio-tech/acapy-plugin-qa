from aries_cloudagent.messaging.base_handler import BaseHandler
from aries_cloudagent.messaging.request_context import RequestContext
from aries_cloudagent.messaging.responder import BaseResponder

from ..messages.answer import Answer

class AnswerHandler(BaseHandler):
    """Handler for Answer message."""

    async def handle(self, context: RequestContext, responder: BaseResponder):
        """Handle answer message."""
        assert isinstance(context.message, Answer)