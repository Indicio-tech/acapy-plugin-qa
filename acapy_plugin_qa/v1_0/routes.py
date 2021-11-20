import logging
import re
from aiohttp import web

from aries_cloudagent.core.event_bus import Event, EventBus
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.messaging.responder import BaseResponder

from aries_cloudagent.storage.error import StorageError, StorageNotFoundError

from aiohttp_apispec import docs, request_schema, response_schema
from .message_types import SPEC_URI
from aries_cloudagent.messaging.agent_message import AgentMessage, AgentMessageSchema
from .messages.question import Question
from marshmallow import fields, ValidationError, pre_dump
import uuid

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










# async def test_route(request: web.Request):
# 	return web.json_response({"success": True})

# async def register(app: web.Application):
# 	app.add_routes([web.get("/qa", test_route)])


class QuestionSchema(AgentMessageSchema):
    """Schema for Question message."""

    class Meta:
        model_class = Question

    question_text = fields.Str(required=True, description=("The text of the question."))
    question_detail = fields.Str(
        required=False,
        description=(
            "This is optional fine-print giving context "
            "to the question and its various answers."
        ),
    )
    valid_responses = fields.List(
        fields.String(),
        required=True,
        description=(
            "A list of dictionaries indicating possible valid responses to the question."
        ),
    )
@docs(
    tags=["QAProtocol"],
    summary="Question & Answer Protocol",
)
@request_schema(QuestionSchema())
@response_schema(QuestionSchema(), 200, description="")
async def qa_features(request: web.BaseRequest):
    """
    Request handler for inspecting supported protocols.

    Args:
        request: aiohttp request object

    Returns:
        The diclosed protocols response

    """
    context: AdminRequestContext = request["context"]
    print(request)
    # registry: ProtocolRegistry = context.inject(ProtocolRegistry)
    # results = registry.protocols_matching_query(request.query.get("query", "*"))
    results = request.query.get("question_text")
    q = Question(
    	question_text=request.query.get("question_text"),
    	valid_responses={"valid_responses": {"text": k} for k in request.query.getall("valid_responses") }
    	# {"results": {k: {} for k in results}}
    	)
    # q.assign_thread_id(request.query.get("@id") or uuid.uuid4())
    q.assign_thread_from(q)

    return web.json_response(q.serialize())


async def register(app: web.Application):
    """Register routes."""

    app.add_routes([web.post("/qa", qa_features)])


def post_process_routes(app: web.Application):
    """Amend swagger API."""

    # Add top-level tags description
    if "tags" not in app._state["swagger_dict"]:
        app._state["swagger_dict"]["tags"] = []
    app._state["swagger_dict"]["tags"].append(
        {
            "name": "QAProtocol",
            "description": "Question & Answer Protocol",
            "externalDocs": {"description": "Specification", "url": SPEC_URI},
        }
    )
