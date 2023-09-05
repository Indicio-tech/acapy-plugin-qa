"""Store question details until answer is received."""

from typing import Any, Optional

from aries_cloudagent.core.profile import ProfileSession
from aries_cloudagent.messaging.models.base_record import BaseRecord, BaseRecordSchema
from aries_cloudagent.messaging.valid import UUID4_EXAMPLE, UUID4_VALIDATE
from aries_cloudagent.storage.error import StorageDuplicateError, StorageNotFoundError
from marshmallow import fields
from marshmallow.utils import EXCLUDE

from ..messages.answer import Answer


class QAExchangeRecord(BaseRecord):
    """Question Answer Exchange Record."""

    class Meta:
        """QAExchangeRecord Meta."""

        schema_class = "QAExchangeRecordSchema"

    RECORD_TYPE = "question_answer"
    RECORD_ID_NAME = "question_answer_id"
    RECORD_TOPIC = "questionanswer"
    EVENT_NAMESPACE = "acapy"
    TAG_NAMES = {
        "state",
        "role",
        "connection_id",
        "thread_id",
    }

    ROLE_QUESTIONER = "questioner"
    ROLE_RESPONDER = "responder"
    STATE_PENDING = "pending"
    STATE_ANSWERED = "answered"

    def __init__(
        self,
        *,
        thread_id: str,
        connection_id: str,
        question_answer_id: str = None,
        state: str = None,
        role: str = None,
        valid_responses: list = None,
        question_text: str = None,
        question_detail: str = None,
        response: str = None,
        **kwargs,
    ):
        """Construct record."""
        super().__init__(question_answer_id, state or self.STATE_PENDING, **kwargs)
        self.role = role or self.ROLE_QUESTIONER
        self.thread_id = thread_id
        self.connection_id = connection_id
        self.valid_responses = valid_responses
        self.question_text = question_text
        self.question_detail = question_detail
        self.response = response

    @property
    def question_answer_id(self) -> Optional[str]:
        """Return record id."""
        return self._id

    @property
    def record_value(self) -> dict:
        """Return record value."""
        return {
            prop: getattr(self, prop)
            for prop in (
                "question_text",
                "question_detail",
                "valid_responses",
                "response",
            )
        }

    @classmethod
    async def query_by_thread_id(
        cls,
        session: ProfileSession,
        thread_id: str,
    ) -> "QAExchangeRecord":
        """Retrieve QAExchangeRecord connection_id.
        Args:
            session: the profile session to use
            connection_id: the connection id by which to filter
            thread_id: the thread id by which to filter
        """
        tag_filter = {
            **{"thread_id": thread_id for _ in [""] if thread_id},
        }

        result = await cls.query(session, tag_filter)
        if len(result) > 1:
            raise StorageDuplicateError(
                "More than one QAExchangeRecord was found for the given IDs"
            )
        if not result:
            raise StorageNotFoundError("No QAExchangeRecord found for the given IDs")
        return result[0]

    async def emit_event(self, session: ProfileSession, payload: Any = None):
        """
        Emit an event.

        Args:
            session: The profile session to use
            payload: The event payload
        """
        topic_detail = {
            f"{self.ROLE_QUESTIONER}::{self.STATE_PENDING}": "question_sent",
            f"{self.ROLE_RESPONDER}::{self.STATE_PENDING}": "question_received",
            f"{self.ROLE_QUESTIONER}::{self.STATE_ANSWERED}": "answer_received",
            f"{self.ROLE_RESPONDER}::{self.STATE_ANSWERED}": "answer_sent",
        }

        # If we don't have the state in the above topic list (such as when it's
        # deleted), don't send an event that we're not handling
        if f"{self.role}::{self.state}" not in topic_detail.keys():
            return
        topic_detail = topic_detail[f"{self.role}::{self.state}"]

        topic = f"{self.EVENT_NAMESPACE}::{self.RECORD_TOPIC}::{topic_detail}"

        if not payload:
            payload = self.serialize()

        await session.profile.notify(topic, payload)

    def to_message(self):
        """Return an answer constructed from this record."""
        if not self.thread_id:
            raise ValueError(
                "No thread ID set on QAExchangeRecord, " "cannot create message"
            )
        return Answer(
            thread_id=self.thread_id,
            response=self.response,
        )


class QAExchangeRecordSchema(BaseRecordSchema):
    """Question Answer Record Schema."""

    class Meta:
        """QAExchangeRecordSchema Meta."""

        model_class = "QAExchangeRecord"
        unknown = EXCLUDE

    connection_id = fields.Str(
        description=(
            "Connection ID to which the answer to the question will be sent; "
            "required if notify is true"
        ),
        required=False,
        validate=UUID4_VALIDATE,
        metadata={"example": UUID4_EXAMPLE},
    )
    _id = fields.Str(
        description=("Thread ID of the QAExchangeRecord message thread"),
        required=False,
        validate=UUID4_VALIDATE,
        metadata={"example": UUID4_EXAMPLE},
    )
    thread_id = fields.Str(
        description=("Thread ID of the QAExchangeRecord message thread"),
        required=False,
        validate=UUID4_VALIDATE,
        metadata={"example": UUID4_EXAMPLE},
    )
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
    response = fields.Str(required=False, description="The received answer response")
