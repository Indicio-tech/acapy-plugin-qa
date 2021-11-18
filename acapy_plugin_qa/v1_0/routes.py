import logging
import re
from aiohttp import web

from aries_cloudagent.core.event_bus import Event, EventBus
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.messaging.responder import BaseResponder

from aries_cloudagent.storage.error import StorageError, StorageNotFoundError

LOGGER = logging.getLogger(__name__)

def register_events(event_bus: EventBus):
	"""Register to handle events."""
	pass

async def test_route(request: web.Request):
	return web.json_response({"success": True})

async def register(app: web.Application):
	app.add_routes([web.get("/qa", test_route)])