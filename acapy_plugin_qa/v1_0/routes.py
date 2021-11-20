import logging
import re
from aiohttp import web

from aries_cloudagent.core.event_bus import Event, EventBus
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.messaging.responder import BaseResponder

from .messages.question import Question
from .messages.answer import Answer

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
        re.compile(f"^{QA_EVENT_PREFIX}{QUESTION_RECEIVED_EVENT}.*"),
        on_question_received,
    )
    event_bus.subscribe(
        re.compile(f"^{QA_EVENT_PREFIX}{ANSWER_RECEIVED_EVENT}.*"),
        on_answer_received,
    )


async def on_question_received(profile: Profile, event: Event):
    """Handle question received event."""

    # check delegation
    if not profile.settings.get("plugin_config", {}).get("qa", {}).get("delegate"):
        return

    # check to whom to delegate
    key = profile.settings.get("plugin_config", {}).get("qa", {}).get("metadata_key")
    value = (
        profile.settings.get("plugin_config", {}).get("qa", {}).get("metadata_value")
    )

    # TODO: create proper metadata query
    # TODO: allow for returning more than one connection
    if key == "role" and value == "admin":
        thread_id = event.payload["@id"]
        question_text = event.payload["question_text"]
        question_detail = event.payload["question_detail"]
        valid_responses = event.payload["valid_responses"]

        rewrapped_question = Question(
            thread_id,
            question_text,
            question_detail,
            valid_responses,
        )
        responder = profile.inject(BaseResponder)
        await responder.send(rewrapped_question, connection_id=connection_id)


async def on_answer_received(profile: Profile, event: Event):
    """Handle answer received event."""

    # check delegation
    if not profile.settings.get("plugin_config", {}).get("qa", {}).get("delegate"):
        return

    # check pthid
    if not event.payload["pthid"]:
        return

    # TODO: properly lookup QAExchangeRecord by thread_id == pthid:
    if qa_exchange_record.pthid == event.payload["@id"]:
        thread_id = event.payload["@id"]
        pthid = event.payload["thread_id"]
        response = event.payload["response"]

        rewrapped_answer = Answer(
            thread_id,
            pthid,
            response,
        )
        responder = profile.inject(BaseResponder)
        await responder.send(
            rewrapped_answer, connection_id=qa_exchange_record.connection_id
        )


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
