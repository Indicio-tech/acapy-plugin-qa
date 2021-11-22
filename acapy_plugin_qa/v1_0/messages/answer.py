from marshmallow import fields, ValidationError, pre_dump
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
        response: str,
        **kwargs,
    ):

        """Initialize answer message."""
        super().__init__(**kwargs)

        self.thread_id = thread_id
        self.response = response


class AnswerSchema(AgentMessageSchema):
    """Schema for Answer message."""

    @pre_dump
    def check_thread_deco(self, obj: AgentMessage, **kwargs):
        """Thread decorator, and its thid and pthid, are mandatory."""
        if not obj._decorators.to_dict().get("~thread", {}).keys() >= {"thid"}:
            raise ValidationError("Missing required field(s) in thread decorator")
        return obj

    class Meta:
        model_class = ANSWER

    thread_id = fields.Str(
        required=True,
        description=("Thread ID used for connecting answer to question."),
        example=UUIDFour.EXAMPLE,
    )
    response = fields.Int(required=True, description=("The response to the question."))
