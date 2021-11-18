"""Status Request and response tests"""

from echo_agent.client import EchoClient
from echo_agent.models import ConnectionInfo
import pytest

import logging

LOGGER = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_send_and_receive(echo: EchoClient, connection: ConnectionInfo):
    """Testing the Status Request Message with no queued messages."""
    await echo.send_message(connection, {"@type": "https://didcomm.org/discover-features/1.0/query", "query": "*"})
    response = await echo.get_message(connection)
    import json
    protocols = [r["pid"] for r in response["protocols"]]
    protocols.sort()
    print(json.dumps(protocols, indent=4, sort_keys=True))
    await echo.send_message(
        connection,
        {
            "@type": "https://didcomm.org/questionanswer/1.0/question",
        },
    )
    response = await echo.get_message(connection)
    print(response)
    assert response["@type"] == (
        "https://didcomm.org/questionanswer/1.0/question"
    )
