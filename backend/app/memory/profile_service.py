import json

from app.memory.redis_client import redis_client



class ProfileService:


    def __init__(self):

        self.redis = redis_client



    def _key(
        self,
        user_id: str
    ):

        return f"profile:{user_id}"



    def save_profile(
        self,
        user_id: str,
        profile: dict
    ):

        return self.redis.set(
            self._key(user_id),
            json.dumps(
                profile,
                ensure_ascii=False
            ),
            expire=2592000
        )



    def get_profile(
        self,
        user_id: str
    ):


        data = self.redis.get(
            self._key(user_id)
        )


        if not data:

            return {}


        return json.loads(data)



profile_service = ProfileService()