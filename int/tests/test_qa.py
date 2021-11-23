"""Status Request and response tests"""

from echo_agent.client import EchoClient
from echo_agent.models import ConnectionInfo
# from aries_cloudagent.messaging.responder import MockResponder
import pytest
import httpx

import logging

LOGGER = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_send_question(echo: EchoClient, backchannel_endpoint: str, connection: ConnectionInfo):
    """Testing the Status Request Message with no queued messages."""
    await echo.send_message(connection, {"@type": "https://didcomm.org/discover-features/1.0/query", "query": "*"})
    response = await echo.get_message(connection)

    # DEBUG
    import json
    protocols = [r["pid"] for r in response["protocols"]]
    protocols.sort()
    print(json.dumps(protocols, indent=4, sort_keys=True))

    thread_id = "MockTestRequestID"

    await echo.send_message(
        connection,
        {
            "@type": "https://didcomm.org/questionanswer/1.0/question",
            "@id": thread_id,
            "question_text": "Are you a test agent?",
            "question_detail": "Verifying that the Q&A Handler works via integration tests",
            "valid_responses": [
                {"text": "yes"},
                {"text": "no"}
            ],
        },
    )
    response = await echo.get_message(connection)
    print(response)

    assert response["@type"] == (
        "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/questionanswer/1.0/question"
    )

    answer = {
        "@type": "https://didcomm.org/questionanswer/1.0/answer",
        "response": "yes",
    }

    r = httpx.post(f"{backchannel_endpoint}/qa/{thread_id}/send-answer", json=answer)
    assert r.status_code == 200

    response = await echo.get_message(connection)
    print(response)

    assert response["@type"] == (
        "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/questionanswer/1.0/answer"
    )
    assert response["response"] == "yes"

@pytest.mark.skip
@pytest.mark.asyncio
async def test_send_answer(echo: EchoClient, connection: ConnectionInfo):
    """Testing the Status Request Message with no queued messages."""
    # await echo.send_message(connection, {"@type": "https://didcomm.org/discover-features/1.0/query", "query": "*"})
    # response = await echo.get_message(connection)
    # import json
    # protocols = [r["pid"] for r in response["protocols"]]
    # protocols.sort()
    # print(json.dumps(protocols, indent=4, sort_keys=True))
    await echo.send_message(
        connection,
        {
            "@type": "https://didcomm.org/questionanswer/1.0/answer",
            "response": "yes",
            "~thread": {
                "thid": "ad285eef-a5e4-4cea-9a40-12f3294d1826"
            }
        },
    )
    response = await echo.get_message(connection)
    print(response)
    assert response["@type"] == (
        "https://didcomm.org/questionanswer/1.0/answer"
    )