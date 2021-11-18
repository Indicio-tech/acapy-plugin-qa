import logging
from aries_cloudagent.core.profile import Profile
from aries_cloudagent.core.error import BaseError

class QAManagerError(BaseError):
    """Q&A Manager error"""

class QAManager:
    """Class for managing Q&A operations"""

    def __init__(self, profile: Profile):
        """Initialize a QAManager"""
        self.profile = profile
        self.logger = logging.getLogger(__name__)
        
    async def answer_question():
        pass

    async def store_question():
        pass
    