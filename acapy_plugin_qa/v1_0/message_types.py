from aries_cloudagent.protocols.didcomm_prefix import DIDCommPrefix

SPEC_URI = "https://github.com/hyperledger/aries-rfcs/blob/main/features/0113-question-answer/README.md"
PROTOCOL = "questionanswer"
VERSION = "1.0"
BASE = f"{PROTOCOL}/{VERSION}"

# Message types
QUESTION = f"{BASE}/question"
ANSWER = f"{BASE}/answer"

PROTOCOL_PACKAGE = "acapy_plugin_qa.v1_0"
MESSAGE_TYPES = DIDCommPrefix.qualify_all(
    {
    QUESTION: f"{PROTOCOL_PACKAGE}.messages.question.Question",
    ANSWER: f"{PROTOCOL_PACKAGE}.messages.answer"}
)