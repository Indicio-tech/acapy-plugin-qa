"""Store question details until answer is received."""

from typing import Optional

from marshmallow import fields
from marshmallow.utils import EXCLUDE

from aries_cloudagent.core.profile import ProfileSession
from aries_cloudagent.messaging.models.base_record import BaseRecord, BaseRecordSchema
from aries_cloudagent.messaging.valid import UUID4
from aries_cloudagent.storage.error import StorageNotFoundError, StorageDuplicateError

from ..messages.answer import Answer


class QAExchangeRecord(BaseRecord):
    """Question Answer Exchange Record."""

    class Meta:
        """QAExchangeRecord Meta."""

        schema_class = "QAExchangeRecordSchema"

    RECORD_TYPE = "question_answer"
    RECORD_ID_NAME = "question_answer_id"
    TAG_NAMES = {
        "connection_id",
        "thread_id",
    }

    def __init__(
        self,
        *,
        question_answer_id: str = None,
        thread_id: str = None,
        pthid: str = None,
        connection_id: str = None,
        valid_responses: list = None,
        question_text: str = None,
        question_detail: str = None,
        **kwargs,
    ):
        """Construct record."""
        super().__init__(question_answer_id, **kwargs)
        self.thread_id = thread_id
        self.pthid = pthid
        self.connection_id = connection_id
        self.valid_responses = valid_responses
        self.question_text = question_text
        self.question_detail = question_detail

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
                "thread_id",
                "question_text",
                "question_detail",
                "valid_responses",
            )
        }

    @classmethod
    async def query_by_ids(
        cls,
        session: ProfileSession,
        connection_id: str,
        thread_id: str,
    ) -> "QAExchangeRecord":
        """Retrieve QAExchangeRecord connection_id.
        Args:
            session: the profile session to use
            connection_id: the connection id by which to filter
            thread_id: the thread id by which to filter
        """
        tag_filter = {
            **{"connection_id": connection_id for _ in [""] if connection_id},
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

    # @pre_dump
    # def check_thread_deco(self, obj: AgentMessage, **kwargs):
    #     """Thread decorator, and its thid and pthid, are mandatory."""
    #     if not obj._decorators.get("~thread", {}).keys() >= {"thid"}:
    #         raise ValidationError("Missing required field(s) in thread decorator")
    #     return obj

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
        **UUID4,
    )
    _id = fields.Str(
        description=("Thread ID of the QAExchangeRecord message thread"),
        required=False,
        **UUID4,
    )
    thread_id = fields.Str(
        description=("Thread ID of the QAExchangeRecord message thread"),
        required=False,
        **UUID4,
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
