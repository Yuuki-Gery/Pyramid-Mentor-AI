from app.core.logging import logger
from app.memory.memory_service import memory_service


class MemoryManager:


    def __init__(self):

        self.service = memory_service



    def get_history(
        self,
        session_id: str
    ):

        try:

            return self.service.get_history(
                session_id
            )


        except Exception:
            logger.exception("Memory read failed")
            return []



    def save_message(
        self,
        session_id: str,
        role: str,
        content: str
    ):

        try:

            return self.service.save_message(
                session_id,
                role,
                content
            )


        except Exception:
            logger.exception("Memory save failed")
            return None



    def clear(
        self,
        session_id: str
    ):

        try:

            return self.service.clear(
                session_id
            )

        except Exception:
            logger.exception("Memory clear failed")
            return None



memory_manager = MemoryManager()