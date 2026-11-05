import json
import re

from app.core.logging import logger


class BaseAgent:

    name = "base"


    def __init__(
        self,
        llm,
        retriever=None
    ):

        self.llm = llm

        self.retriever = retriever



    def clean_json(
        self,
        text: str
    ):

        """
        提取LLM JSON
        防止markdown包裹
        """

        if not text:

            return {}


        text = text.strip()


        if "```" in text:

            text = re.sub(
                r"```json",
                "",
                text
            )

            text = re.sub(
                r"```",
                "",
                text
            )


        text = text.strip()


        try:

            return json.loads(
                text
            )


        except Exception:


            match = re.search(
                r"\{.*\}",
                text,
                re.S
            )


            if match:

                try:

                    return json.loads(
                        match.group()
                    )


                except Exception:

                    pass


        return {}



    def fill_json(
        self,
        data: dict,
        fields: dict
    ):

        """
        补充缺失字段
        """

        if not data:

            data = {}


        for key,value in fields.items():

            if key not in data:

                data[key] = value


        return data



    def safe_retrieval(
        self,
        query: str,
        k: int = 3
    ):

        """
        安全的知识检索调用
        """

        try:

            if self.retriever:

                return self.retriever.search(
                    query,
                    k
                )

            return []


        except Exception:
            logger.exception("Knowledge retrieval failed")

            return []



    async def safe_llm_call(
        self,
        prompt: str
    ):

        """
        安全的LLM调用
        """

        try:

            response = await self.llm.chat(

                [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response


        except Exception:
            logger.exception("LLM call failed")

            return ""
