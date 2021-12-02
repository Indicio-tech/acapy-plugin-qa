# Q&A Protocol Plugin

[![Code Quality Check](https://github.com/Indicio-tech/acapy-plugin-qa/actions/workflows/code-quality-check.yml/badge.svg)](https://github.com/Indicio-tech/acapy-plugin-qa/actions/workflows/code-quality-check.yml)
[![Tests](https://github.com/Indicio-tech/acapy-plugin-qa/actions/workflows/tests.yml/badge.svg)](https://github.com/Indicio-tech/acapy-plugin-qa/actions/workflows/tests.yml)

## [**Q&A RFC**](https://github.com/hyperledger/aries-rfcs/blob/main/features/0113-question-answer/README.md)

## Admin Routes
In the Q&A Protocol, the admin routes define ways to interact with the protocol, beyond sending messages as a simple agent. Each route is structured as an `http` request.

- In the examples below, ADMIN_ENDPOINT is the port of the admin agent, something like `http://agent:3001`

### get_questions
`{ADMIN_ENDPOINT}/qa/get-questions`

- This is a **GET** request. The `get_questions` route returns a list of questions that have been received and not yet deleted.

### send_question
`{ADMIN_ENDPOINT}/qa/{connection_id}/send-question`

**Body:**
```json=
{
    "@type": "https://didcomm.org/questionanswer/1.0/question",
    "question_text": "Are you a test agent?",
    "question_detail": "Verifying that the Q&A Handler works via integration tests",
    "valid_responses": [
        {"text": "yes"}, 
        {"text": "no"}
    ]
}
```
- This is a **POST** request. This allows us to specify a json object as the request payload and post that question to the connected agent.
- The `{connection_id}` specifies the connetion to send the question to.
- `question_text` is the question to answer.
- `question_detail`  is optional fine-print of the question. This might be displayed behind a “show more” button or similar.
- `valid_responses` is an enumeration of acceptable responses.

### send_answer
`{ADMIN_ENDPOINT}/qa/{thread_id}/send-answer`

**Body:**
```json=
{
    "@type": "https://didcomm.org/questionanswer/1.0/answer",
    "@id": "1ccf5055-ec8e-40bc-bbb9-a71bf5e4117f",
    "response": "yes"
}
```
- This is also a **POST** request. Similarly to the `send_question` route, this allows us to send an answer to a given thread. 
    - The answer is specified as a json object and passed as the request payload.
- The `{thread_id}` is the same as the `@id` of the question being answered 
- `response` is the only required attribute, and it SHOULD match one of the acceptable responses listed in the `question` message. In the case of an answer containing an unexpected response, the questioner must decide what to do.


### delete
`{ADMIN_ENDPOINT}/qa/{thread_id}`
- This is a **DELETE** request. 
- By supplying the `thread_id` of a question, the record of that question is deleted. 

