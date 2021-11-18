from marshmallow import fields
from typing import Dict, List, Optional
from aries_cloudagent.messaging.agent_message import AgentMessage, AgentMessageSchema
from aries_cloudagent.messaging.valid import UUIDFour
from ..message_types import PROTOCOL_PACKAGE, ANSWER

HANDLER_CLASS = f"{PROTOCOL_PACKAGE}.handlers.answer_handler"

class Answer(AgentMessage):
    """Class representing the answer message"""

    class Meta:
        """Answer Meta"""
        handler_class = HANDLER_CLASS
        message_type = ANSWER
        schema_class = "AnswerSchema"

    def __init__(self, *, thread_id: str, response: str, **kwargs):

        """Initialize answer message."""
        super().__init__(**kwargs)

        self.thread_id = thread_id
        self.response = response


class AnswerSchema(AgentMessageSchema):
    """Schema for Answer message."""

    class Meta:
        model_class = ANSWER

    thread_id = fields.Str(
        required=True,
        description=(
            "Thread ID used for connecting back to the question."
        ),
        example=UUIDFour.EXAMPLE,
    )

    response = fields.Str(
        required=True,
        description=(
            "The text of the answer."
        )
    )
