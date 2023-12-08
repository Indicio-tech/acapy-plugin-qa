"""Status Request and response tests"""

from echo_agent.client import EchoClient
from echo_agent.models import ConnectionInfo
import pytest
import httpx

import logging

LOGGER = logging.getLogger(__name__)

question = {
    "@type": "https://didcomm.org/questionanswer/1.0/question",
    "question_text": "Are you a test agent?",
    "question_detail": "Verifying that the Q&A Handler works via integration tests",
    "valid_responses": [{"text": "yes"}, {"text": "no"}],
}


@pytest.mark.asyncio
async def test_send_question_receive_answer(
    echo: EchoClient, backchannel_endpoint: str, connection: ConnectionInfo
):
    """Test ACA-Py can respond to a question."""

    await echo.send_message(
        connection,
        question,
    )

    r = httpx.get(f"{backchannel_endpoint}/qa/get-questions")
    assert r.status_code == 200

    response = r.json()["results"][0]
    assert response["question_text"] == question["question_text"]
    assert response["question_detail"] == question["question_detail"]
    assert response["valid_responses"] == question["valid_responses"]
    thread_id = response["thread_id"]

    answer = {
        "response": "yes",
    }
    r = httpx.post(f"{backchannel_endpoint}/qa/{thread_id}/send-answer", json=answer)
    assert r.status_code == 200

    response = await echo.get_message(connection)

    assert response["@type"] == (
        "https://didcomm.org/questionanswer/1.0/answer"
    )
    assert response["response"] == "yes"

    r = httpx.get(f"{backchannel_endpoint}/qa/get-questions")
    assert r.status_code == 200
    results = r.json()["results"]
    assert results
    assert results[0]["response"]

    r = httpx.delete(f"{backchannel_endpoint}/qa/{thread_id}")
    assert r.status_code == 200

    r = httpx.get(f"{backchannel_endpoint}/qa/get-questions")
    assert r.status_code == 200
    assert r.json()["results"] == []


@pytest.mark.asyncio
async def test_receive_question(
    echo: EchoClient,
    backchannel_endpoint: str,
    connection: ConnectionInfo,
    connection_id: str,
):
    """Test ACA-Py can send a question and receive an answer."""
    r = httpx.post(
        f"{backchannel_endpoint}/qa/{connection_id}/send-question", json=question
    )
    assert r.status_code == 200
    question_thread_id = r.json()["thread_id"]

    response = await echo.get_message(connection)
    assert response["@type"] == (
        "https://didcomm.org/questionanswer/1.0/question"
    )
    thread_id = response["@id"]
    assert thread_id == question_thread_id

    await echo.send_message(
        connection,
        {
            "@type": "https://didcomm.org/questionanswer/1.0/answer",
            "response": "yes",
            "~thread": {"thid": thread_id},
        },
    )
    r = httpx.get(f"{backchannel_endpoint}/qa/get-questions")
    assert r.status_code == 200
    results = r.json()["results"]
    assert results
    assert results[0]["response"]
    assert results[0]["thread_id"] == thread_id

    r = httpx.delete(f"{backchannel_endpoint}/qa/{thread_id}")
    assert r.status_code == 200

    r = httpx.get(f"{backchannel_endpoint}/qa/get-questions")
    assert r.status_code == 200
    assert r.json()["results"] == []
