import logging
import re
from aiohttp import web
from typing import Sequence

from aries_cloudagent.core.event_bus import Event, EventBus
from aries_cloudagent.core.profile import Profile, ProfileSession
from aries_cloudagent.messaging.responder import BaseResponder
from aries_cloudagent.storage.base import BaseStorage
from aries_cloudagent.storage.record import StorageRecord
from aries_cloudagent.connections.models.conn_record import ConnRecord
import json

from .messages.question import Question, QuestionSchema
from .messages.answer import Answer, AnswerSchema

from aiohttp_apispec import docs, request_schema, response_schema, match_info_schema
from .message_types import SPEC_URI
from aries_cloudagent.messaging.agent_message import AgentMessage, AgentMessageSchema
from marshmallow import fields, ValidationError, pre_dump
from aries_cloudagent.messaging.models.openapi import OpenAPISchema
from aries_cloudagent.messaging.valid import UUIDFour
from aries_cloudagent.connections.models.conn_record import ConnRecord
from .handlers.answer_handler import AnswerHandler
import uuid

LOGGER = logging.getLogger(__name__)

QA_EVENT_PREFIX = "acapy::questionanswer"
QUESTION_RECEIVED_EVENT = "received"
ANSWER_RECEIVED_EVENT = "received"

def register_events(event_bus: EventBus):
    """Register to handle events."""
    event_bus.subscribe(
        re.compile(f"^{QA_EVENT_PREFIX}::{QUESTION_RECEIVED_EVENT}.*"),
        on_question_received,
    )
    event_bus.subscribe(
        re.compile(f"^{QA_EVENT_PREFIX}::{ANSWER_RECEIVED_EVENT}.*"),
        on_answer_received,
    )


async def on_question_received(profile: Profile, event: Event, session: ProfileSession):
    """Handle question received event."""

    # check delegation
    if not profile.settings.get("plugin_config", {}).get("qa", {}).get("delegate"):
        return

    # check to whom to delegate
    key = profile.settings.get("plugin_config", {}).get("qa", {}).get("metadata_key")
    value = (
        profile.settings.get("plugin_config", {}).get("qa", {}).get("metadata_value")
    )

    storage: BaseStorage = session.inject(BaseStorage)
    records: Sequence[StorageRecord] = await storage.find_all_records(
        ConnRecord.RECORD_TYPE_METADATA, {key: value}
    )
    records = [
        record
        for record in records
        if json.loads(record.key) == "role"
        if json.loads(record.value) == "admin"
    ]
    results = []
    for record in records:
        results.append(
            await ConnRecord.retrieve_by_id(session, record.tags["connection_id"])
        )

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
    for result in results:
        await responder.send(rewrapped_question, connection_id=result.connection_id)


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


class QuestionRequestSchema(AgentMessageSchema):
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


class AnswerRequestSchema(AgentMessageSchema):
    """Schema for Question message."""

    class Meta:
        model_class = Answer

    response = fields.Str(required=True, description=("The text of the question."))


class BasicConnIdMatchInfoSchema(OpenAPISchema):
    """Path parameters and validators for request taking connection id."""

    conn_id = fields.Str(
        description="Connection identifier", required=True, example=UUIDFour.EXAMPLE
    )


class BasicThidMatchInfoSchema(OpenAPISchema):
    """Path parameters and validators for request taking connection id."""

    thread_id = fields.Str(
        description="Thread identifier", required=True, example=UUIDFour.EXAMPLE
    )

@docs(
    tags=["QAProtocol"],
    summary="Question & Answer Protocol",
)
@match_info_schema(BasicConnIdMatchInfoSchema())
@request_schema(QuestionSchema())
@response_schema(QuestionSchema(), 200, description="")
async def send_question(request: web. BaseRequest):
    """
    Request handler for inspecting supported protocols.

    Args:
        request: aiohttp request object

    Returns:
        The diclosed protocols response

    """
    # Extract question data sent to us (the Questioner)
    context: AdminRequestContext = request["context"]
    connection_id = request.match_info["conn_id"]
    outbound_handler = request["outbound_message_router"]
    params = await request.json()
    print(request)
    # registry: ProtocolRegistry = context.inject(ProtocolRegistry)
    # results = registry.protocols_matching_query(request.query.get("query", "*"))
    results = request.query.get("question_text")
    q = Question(
        question_text=request.query.get("question_text"),
        valid_responses={
            "valid_responses": {"text": k}
            for k in request.query.getall("valid_responses")
        }
        # {"results": {k: {} for k in results}}
    )
    # results = request.query.get("question_text")
    # q = Question(
    # 	question_text=request.query.get("question_text"),
    # 	valid_responses={"valid_responses": {"text": k} for k in request.query.getall("valid_responses") }
    # 	# {"results": {k: {} for k in results}}
    # 	)
    # q.assign_thread_id(request.query.get("@id") or uuid.uuid4())
    # q.assign_thread_from(q)


    try:
        async with context.session() as session:
            connection = await ConnRecord.retrieve_by_id(session, connection_id)
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    if connection.is_ready:
        # Setup a question object to pass on to the responder
        msg = Question(
            _id=params["@id"],
            question_text=params["question_text"],
            question_detail=params["question_detail"],
            valid_responses=params["valid_responses"]
        )
        manager = QAManager(context)
        manager.store_question()  # Store the question
        msg.assign_thread_id(params["@id"])  # At this time, the thid is required for serialization
        await outbound_handler(msg, connection_id=connection_id)

    return web.json_response({})

    return web.json_response(msg.serialize())

@docs(
    tags=["QAProtocol"],
    summary="Question & Answer Protocol",
)
# @match_info_schema(BasicThidMatchInfoSchema())
# @request_schema(AnswerSchema())
@response_schema(AnswerSchema(), 200, description="")
async def send_answer(request: web.BaseRequest):
    """
    Request handler for inspecting supported protocols.

    Args:
        request: aiohttp request object

    Returns:
        The diclosed protocols response

    """
    # Extract question data sent to us (the Questioner)
    print(request)
    print(dict(request))
    # return web.json_response({})
    context: AdminRequestContext = request["context"]
    thread_id = request.match_info["thread_id"]
    outbound_handler = request["outbound_message_router"]
    params = await request.json()
    manager = QAManager(context)

    try:
        async with context.session() as session:
            record = await manager.retrieve_by_id(thread_id)
            connection = await ConnRecord.retrieve_by_id(session, connection_id)
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    if connection.is_ready:
        # Setup a question object to pass on to the responder
        msg = Answer(
            response=params["response"],
        )
        msg.assign_thread_id(msg._thread.thid, thread_id)  # At this time, the thid is required for serialization
        AnswerHandler.qa_notify(context.profile, msg)
        await outbound_handler(msg, connection_id=connection_id)

    return web.json_response({})

    return web.json_response(msg.serialize())


async def register(app: web.Application):
    """Register routes."""

    app.add_routes([
        web.post("/qa/{conn_id}/send-question", send_question),
        web.post("/qa/{thread_id}/send-answer", send_answer),
        ])


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
