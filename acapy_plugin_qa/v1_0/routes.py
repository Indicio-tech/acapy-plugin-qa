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
	event_bus.subscribe(
		re.compile(f"^{QA_EVENT_PREFIX_PLACEHOLDER}{QUESTION_RECEIVED_EVENT_PLACEHOLDER}.*"),
		on_question_received
	)
	event_bus.subscribe(
		re.compile(f"^{QA_EVENT_PREFIX_PLACEHOLDER}{ANSWER_RECEIVED_EVENT_PLACEHOLDER}.*"),
		on_answer_received
	)
	# When delegating, event subscriber prepares another
	# question message and sends to delegated connection


	# need to register to our question and answer events
	# the cases of delegation
	# see revocation routes.py for example below
	"""
	event_bus.subscribe(
        re.compile(f"^{REVOCATION_EVENT_PREFIX}{REVOCATION_PUBLISHED_EVENT}.*"),
        on_revocation_published,
    )
    event_bus.subscribe(
        re.compile(f"^{REVOCATION_EVENT_PREFIX}{REVOCATION_CLEAR_PENDING_EVENT}.*"),
        on_pending_cleared,
    )"""

async def on_question_received(profile: Profile, event: Event):
	"""Handle question received event."""
	# When delegating, event subscriber prepares another
	# question message and sends to delegated connection



    # LOGGER.debug("Sending notification of revocation to recipient: %s", event.payload)

    # should_notify = profile.settings.get("revocation.notify", False)
    # responder = profile.inject(BaseResponder)
    # crids = event.payload.get("crids") or []



async def on_answer_received(profile: Profile, event: Event):
	"""Handle answer received event."""










async def test_route(request: web.Request):
	return web.json_response({"success": True})

async def register(app: web.Application):
	app.add_routes([web.get("/qa", test_route)])