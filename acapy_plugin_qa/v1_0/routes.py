import logging

from aiohttp import web
from aiohttp_apispec import docs, match_info_schema, request_schema, response_schema
from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.connections.models.conn_record import ConnRecord
from aries_cloudagent.messaging.agent_message import AgentMessageSchema
from aries_cloudagent.messaging.models.openapi import OpenAPISchema
from aries_cloudagent.messaging.valid import UUIDFour
from aries_cloudagent.storage.error import StorageNotFoundError
from marshmallow import fields

from .message_types import SPEC_URI
from .messages.answer import Answer
from .messages.question import Question, QuestionSchema
from .models.qa_exchange_record import QAExchangeRecord

LOGGER = logging.getLogger(__name__)


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


# class QuestionListResponseSchema(OpenAPISchema):
#     """Path parameters and validators for request taking connection id."""

#     thread_id = fields.List(
#         description="Thread identifier", required=True, example=UUIDFour.EXAMPLE
#     )


@docs(
    tags=["QAProtocol"],
    summary="Question & Answer Protocol",
)
# @response_schema(QuestionListResponseSchema(), 200, description="")
async def get_questions(request: web.BaseRequest):
    """
    Request handler for inspecting supported protocols.

    Args:
        request: aiohttp request object

    Returns:
        The diclosed protocols response

    """
    # Extract question data sent to us (the Questioner)
    context: AdminRequestContext = request["context"]

    try:
        async with context.session() as session:
            records = await QAExchangeRecord.query(session)
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    return web.json_response({"results": [rec.serialize() for rec in records]})


@docs(
    tags=["QAProtocol"],
    summary="Question & Answer Protocol",
)
@match_info_schema(BasicConnIdMatchInfoSchema())
@request_schema(QuestionSchema())
@response_schema(QuestionSchema(), 200, description="")
async def send_question(request: web.BaseRequest):
    """
    Request handler for sending a question.

    Args:
        request: aiohttp request object

    Returns:
        empty response

    """
    # Extract question data sent to us (the Questioner)
    context: AdminRequestContext = request["context"]
    connection_id = request.match_info["conn_id"]
    outbound_handler = request["outbound_message_router"]
    params = await request.json()

    try:
        async with context.session() as session:
            connection = await ConnRecord.retrieve_by_id(session, connection_id)
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err

    if connection.is_ready:
        # Setup a question object to pass on to the responder
        msg = Question(
            # _id=params["@id"],
            question_text=params["question_text"],
            question_detail=params["question_detail"],
            valid_responses=params["valid_responses"],
        )
        record = QAExchangeRecord(
            role=QAExchangeRecord.ROLE_QUESTIONER,
            connection_id=connection_id,
            thread_id=msg._id,
            question_text=msg.question_text,
            question_detail=msg.question_detail,
            valid_responses=msg.valid_responses,
        )
        async with context.session() as session:
            await record.save(session, reason="New question received")

        await outbound_handler(msg, connection_id=connection_id)

    return web.json_response({"success": True})


@docs(
    tags=["QAProtocol"],
    summary="Question & Answer Protocol",
)
@match_info_schema(BasicThidMatchInfoSchema())
# @request_schema(AnswerSchema())
async def send_answer(request: web.BaseRequest):
    """
    Request handler for sending an answer.

    Args:
        request: aiohttp request object

    Returns:
        empty response

    """
    # Extract question data sent to us (the Questioner)
    context: AdminRequestContext = request["context"]
    thread_id = request.match_info["thread_id"]
    outbound_handler = request["outbound_message_router"]
    params = await request.json()

    async with context.session() as session:
        try:
            record = await QAExchangeRecord.query_by_thread_id(session, thread_id)
            connection = await ConnRecord.retrieve_by_id(session, record.connection_id)
        except StorageNotFoundError as err:
            raise web.HTTPNotFound(reason=err.roll_up) from err

        if connection.is_ready:
            # Setup a question object to pass on to the responder
            msg = Answer(
                response=params["response"],
            )
            msg.assign_thread_id(record.thread_id)
            await outbound_handler(msg, connection_id=record.connection_id)

            record.state = QAExchangeRecord.STATE_ANSWERED
            record.response = params["response"]
            await record.save(session, reason="Answer sent")

    return web.json_response({"success": True})


@docs(
    tags=["QAProtocol"],
    summary="Question & Answer Protocol",
)
@match_info_schema(BasicThidMatchInfoSchema())
# @request_schema(AnswerSchema())
async def delete(request: web.BaseRequest):
    """
    Request handler for sending an answer.

    Args:
        request: aiohttp request object

    Returns:
        empty response

    """
    context: AdminRequestContext = request["context"]
    thread_id = request.match_info["thread_id"]

    async with context.session() as session:
        try:
            record = await QAExchangeRecord.query_by_thread_id(session, thread_id)
        except StorageNotFoundError as err:
            raise web.HTTPNotFound(reason=err.roll_up) from err
        await record.delete_record(session)

    return web.json_response({"success": True})


async def register(app: web.Application):
    """Register routes."""

    app.add_routes(
        [
            web.get("/qa/get-questions", get_questions),
            web.post("/qa/{conn_id}/send-question", send_question),
            web.post("/qa/{thread_id}/send-answer", send_answer),
            web.delete("/qa/{thread_id}", delete),
        ]
    )


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
