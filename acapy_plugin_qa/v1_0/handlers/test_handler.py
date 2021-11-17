from aries_cloudagent.messaging.base_handler import BaseHandler
from aries_cloudagent.messaging.request_context import RequestContext
from aries_cloudagent.messaging.responder import BaseResponder


class TestHandler(BaseHandler):
	
	async def handle(self, context: RequestContext, responder: BaseResponder):
		self._logger.info("We made it to the Handler! \\o/")