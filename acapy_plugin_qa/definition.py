import logging
from typing import Dict, List, Optional

from aries_cloudagent.messaging.agent_message import AgentMessage

LOGGER = logging.getLogger(__name__)
PROTOCOL = "https://github.com/hyperledger/aries-toolbox/docs/admin-qa/0.1"

class QuestionHandler(AgentMessage):
    message_type = f"{PROTOCOL}/question"
    question_text: str
    question_detail: Optional[str] = None
    valid_responses: List[Dict]

    async def handle():
        pass
