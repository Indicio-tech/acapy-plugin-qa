from marshmallow import fields
from typing import Dict, List, Optional
from aries_cloudagent.messaging.agent_message import AgentMessage, AgentMessageSchema
from aries_cloudagent.messaging.valid import UUIDFour
from ..message_types import PROTOCOL_PACKAGE, QUESTION

HANDLER_CLASS = f"{PROTOCOL_PACKAGE}.handlers.question_handler"

class Question(AgentMessage):
    """Class representing the question message"""

    class Meta:
        """Question Meta"""
        handler_class = HANDLER_CLASS
        message_type = QUESTION
        schema_class = "QuestionSchema"

    def __init__(self, *, thread_id: str, question_text: str, 
    question_detail: Optional[str] = None, valid_responses: List[Dict], **kwargs):

        """Initialize question message."""
        super().__init__(**kwargs)

        self.thread_id = thread_id
        self.question_text = question_text
        self.question_detail = question_detail
        self.valid_responses = valid_responses


class QuestionSchema(AgentMessageSchema):
    """Schema for Question message."""

    class Meta:
        model_class = QUESTION

    thread_id = fields.Str(
        required=True,
        description=(
            "Thread ID used for connecting answer to question."
        ),
        example=UUIDFour.EXAMPLE,
    )

    question_text = fields.Str(
        required=True,
        description=(
            "The text of the question."
        )
    )

    question_detail = fields.Str(
        required=False,
        description=(
            "This is optional fine-print giving context to the question and its various answers."
        )
    )

    valid_responses = fields.Str(
        required=True,
        description=(
            "A list of dictionaries indicating possible valid responses to the question."
        )
    )
    