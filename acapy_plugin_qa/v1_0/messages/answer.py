from marshmallow import fields, ValidationError, pre_dump
from typing import Optional
from aries_cloudagent.messaging.agent_message import AgentMessage, AgentMessageSchema
from aries_cloudagent.messaging.valid import UUIDFour
from ..message_types import PROTOCOL_PACKAGE, ANSWER

HANDLER_CLASS = f"{PROTOCOL_PACKAGE}.handlers.answer_handler.AnswerHandler"


class Answer(AgentMessage):
    """Class representing the answer message"""

    class Meta:
        """Answer Meta"""

        handler_class = HANDLER_CLASS
        message_type = ANSWER
        schema_class = "AnswerSchema"

    def __init__(
        self,
        *,
        thread_id: str,
        question_text: str,
        question_detail: Optional[str] = None,
        response: str,
        **kwargs,
    ):

        """Initialize answer message."""
        super().__init__(**kwargs)

        self.thread_id = thread_id
        self.question_text = question_text
        self.question_detail = question_detail
        self.response = response


class AnswerSchema(AgentMessageSchema):
    """Schema for Answer message."""

    @pre_dump
    def check_thread_deco(self, obj: AgentMessage, **kwargs):
        """Thread decorator, and its thid and pthid, are mandatory."""
        if not obj._decorators.get("~thread", {}).keys() >= {"thid"}:
            raise ValidationError("Missing required field(s) in thread decorator")
        return obj

    class Meta:
        model_class = ANSWER

    thread_id = fields.Str(
        required=True,
        description=("Thread ID used for connecting answer to question."),
        example=UUIDFour.EXAMPLE,
    )
    question_text = fields.Str(required=True, description=("The text of the question."))
    question_detail = fields.Str(
        required=False,
        description=(
            "This is optional fine-print giving context"
            + "to the question and its various answers."
        ),
    )
    response = fields.Int(required=True, description=("The response to the question."))
