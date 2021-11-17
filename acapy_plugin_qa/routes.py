import logging
import re

from acapy_cloudagent.core.event_bus import Event, EventBus
from acapy_cloudagent.core.profile import Profile
from acapy_cloudagent.messaging.responder import Base Responder

from acapy_cloudagent.storage.error import StorageError, StorageNotFoundError

LOGGER = getLogger(__name__)

def register_events(event_bus: EventBus):
	"""Register to handle events."""
	pass

