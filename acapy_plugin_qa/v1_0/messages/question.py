"""Question Classes."""
from marshmallow import fields
from typing import Dict, List, Optional

from aries_cloudagent.messaging.agent_message import AgentMessage, AgentMessageSchema

from ..message_types import PROTOCOL_PACKAGE, QUESTION

HANDLER_CLASS = f"{PROTOCOL_PACKAGE}.handlers.question_handler.QuestionHandler"


class Question(AgentMessage):
    """Class representing the question message."""

    class Meta:
        """Question Meta."""

        handler_class = HANDLER_CLASS
        message_type = QUESTION
        schema_class = "QuestionSchema"

    def __init__(
        self,
        *,
        question_text: str,
        question_detail: Optional[str] = None,
        valid_responses: List[Dict],
        **kwargs,
    ):
        """Initialize question message."""
        super().__init__(**kwargs)

        self.question_text = question_text
        self.question_detail = question_detail
        self.valid_responses = valid_responses


class QuestionSchema(AgentMessageSchema):
    """Schema for Question message."""

    class Meta:
        """Meta class for QuestionSchema."""
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
        fields.Mapping(),
        required=True,
        description=(
            "A list of dictionaries indicating possible valid responses to the question."
        ),
    )
