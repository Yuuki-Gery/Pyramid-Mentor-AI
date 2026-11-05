import json

from app.memory.redis_client import redis_client


class MemoryService:


    def __init__(self):
        self.redis = redis_client


    def _key(self, session_id: str):

        return f"memory:{session_id}"


    def save_message(
        self,
        session_id: str,
        role: str,
        content: str
    ):

        key = self._key(session_id)


        history = self.get_history(session_id)


        history.append(
            {
                "role": role,
                "content": content
            }
        )


        self.redis.set(
            key,
            json.dumps(history, ensure_ascii=False),
            expire=86400
        )


        return history



    def get_history(
        self,
        session_id: str
    ):


        data = self.redis.get(
            self._key(session_id)
        )


        if not data:
            return []


        return json.loads(data)



    def clear(
        self,
        session_id: str
    ):

        return self.redis.client.delete(
            self._key(session_id)
        )



memory_service = MemoryService()