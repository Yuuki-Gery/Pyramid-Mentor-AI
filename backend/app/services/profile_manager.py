from app.core.logging import logger
from app.memory.profile_service import profile_service


class ProfileManager:


    def __init__(
        self,
        agent_manager
    ):

        self.agent_manager = agent_manager



    async def update_profile(
        self,
        session_id: str,
        message: str
    ):


        try:

            old_profile = profile_service.get_profile(
                session_id
            )

        except Exception:
            logger.exception("Profile read failed")
            old_profile = {}



        try:

            new_profile_result = await self.agent_manager.run(
                "profile",
                message,
                {
                    "profile": old_profile,
                    "history": [],
                    "knowledge": ""
                }
            )


            new_profile = (

                new_profile_result.analysis

                if new_profile_result

                else {}

            )


        except Exception:
            logger.exception("Profile agent failed")
            new_profile = {}



        merge_input = {

            "old_profile": old_profile,

            "new_profile": new_profile

        }



        try:


            merged_result = await self.agent_manager.run(
                "profile_merge",
                "",
                merge_input
            )


            final_profile = (

                merged_result.analysis

                if merged_result

                else old_profile

            )


        except Exception:
            logger.exception("Profile merge failed")
            final_profile = old_profile



        try:

            profile_service.save_profile(
                session_id,
                final_profile
            )


        except Exception:
            logger.exception("Profile save failed")



        return final_profile