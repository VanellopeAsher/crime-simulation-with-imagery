"""UrbanLLM: 智能能力类及其定义"""

import json
from openai import OpenAI, AsyncOpenAI, APIConnectionError, OpenAIError

import asyncio
from typing import Any, Optional

import time
import jsonlines
from openai import OpenAI
from constant import PLATFORM, API_KEY_MAP, BASE_URL_MAP 

import os

os.environ["GRPC_VERBOSITY"] = "ERROR"


class LLM:
    """
    大语言模型对象
    The LLM Object used by Agent(Soul)
    """

    def __init__(self, 
                 model_name: str, 
                 platform: PLATFORM = 'openai', 
                 api_keys: list[str]|str = None, 
                 base_url: str = None
            ) -> None:

        self.model_name = model_name
        self.platform = platform
        self.api_keys = api_keys

        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.history = []

        self.request_number = 0
        self.semaphore = None
        self._current_client_index = 0

        if not base_url:
            assert platform in API_KEY_MAP, f"Platform {platform} is not supported or base url not provided."
            base_url = BASE_URL_MAP[platform]
        if not api_keys:
            api_keys = os.environ.get(API_KEY_MAP[platform])
            assert api_keys, f"API key is not provided."
        if not isinstance(api_keys, list):
            api_keys = [api_keys]
     
        self._aclients = []
        
        for api_key in api_keys:
            client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=300,
            )
            self._aclients.append(client)

    def set_semaphore(self, number_of_coroutine: int):
        self.semaphore = asyncio.Semaphore(number_of_coroutine)

    def clear_semaphore(self):
        self.semaphore = None

    def clear_used(self):
        """
        clear the storage of used tokens to start a new log message
        Only support OpenAI category API right now, including OpenAI, Deepseek
        """
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.request_number = 0

    def show_consumption(
        self, input_price: Optional[float] = None, output_price: Optional[float] = None
    ):
        """
        if you give the input and output price of using model, this function will also calculate the consumption for you
        """
        total_token = self.prompt_tokens + self.completion_tokens
        if self.completion_tokens != 0:
            rate = self.prompt_tokens / self.completion_tokens
        else:
            rate = "nan"
        if self.request_number != 0:
            TcA = total_token / self.request_number
        else:
            TcA = "nan"
        out = f"""Request Number: {self.request_number}
Token Usage:
    - Total tokens: {total_token}
    - Prompt tokens: {self.prompt_tokens}
    - Completion tokens: {self.completion_tokens}
    - Token per request: {TcA}
    - Prompt:Completion ratio: {rate}:1"""
        if input_price != None and output_price != None:
            consumption = (
                self.prompt_tokens / 1000000 * input_price
                + self.completion_tokens / 1000000 * output_price
            )
            out += f"\n    - Cost Estimation: {consumption}"
        print(out)
        return {
            "total": total_token,
            "prompt": self.prompt_tokens,
            "completion": self.completion_tokens,
            "ratio": rate,
        }

    def _get_next_client(self):
        """获取下一个要使用的客户端"""
        client = self._aclients[self._current_client_index]
        self._current_client_index = (self._current_client_index + 1) % len(self._aclients)
        return client

    async def atext_request(
        self,
        dialog: Any,
        model: Optional[str] = None,
        temperature: float = 1,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        timeout: int = 300,
        retries=3,
        # tools: Optional[list[dict[str, Any]]] = None,
        # tool_choice: Optional[dict[str, Any]] = None,
    ):
        """
        异步版文本请求
        """
        if model is None:
            model = self.model_name

        if isinstance(dialog, str):
            dialog = [{'role': 'user', 'content': dialog}]
        else:
            dialog = dialog

        # save system time when log history
        # for m in dialog:
        #     m.update({"time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})
        #     self.history.append(m)

        for attempt in range(retries):
            try:
                client = self._get_next_client()
                if self.semaphore != None:
                    async with self.semaphore:
                        response = await client.chat.completions.create(
                            model=model,
                            messages=dialog,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            top_p=top_p,
                            frequency_penalty=frequency_penalty,  # type: ignore
                            presence_penalty=presence_penalty,  # type: ignore
                            stream=False,
                            timeout=timeout,
                            # tools=tools,
                            # tool_choice=tool_choice,
                        )  # type: ignore
                        self.prompt_tokens += response.usage.prompt_tokens  # type: ignore
                        self.completion_tokens += response.usage.completion_tokens  # type: ignore
                        self.request_number += 1
                        
                        # self.history.append({'role': 'assistant', 'content': response.choices[0].message.content, 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})

                        # if tools and response.choices[0].message.tool_calls:
                        #     return json.loads(
                        #         response.choices[0]
                        #         .message.tool_calls[0]
                        #         .function.arguments
                        #     )
                        # else:
                        return response.choices[0].message.content
                else:
                    response = await client.chat.completions.create(
                        model=self.model_name,
                        messages=dialog,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                        frequency_penalty=frequency_penalty,  # type: ignore
                        presence_penalty=presence_penalty,  # type: ignore
                        stream=False,
                        timeout=timeout,
                        # tools=tools,
                        # tool_choice=tool_choice,
                    )  # type: ignore
                    self.prompt_tokens += response.usage.prompt_tokens  # type: ignore
                    self.completion_tokens += response.usage.completion_tokens  # type: ignore
                    self.request_number += 1

                    # self.history.append({'role': 'assistant', 'content': response.choices[0].message.content, 'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())})

                    # if tools and response.choices[0].message.tool_calls:
                    #     return json.loads(
                    #         response.choices[0]
                    #         .message.tool_calls[0]
                    #         .function.arguments
                    #     )
                    # else:
                    return response.choices[0].message.content
            except APIConnectionError as e:
                print("API connection error:", e)
                if attempt < retries - 1:
                    await asyncio.sleep(4**attempt)
                else:
                    raise e
            except OpenAIError as e:
                if hasattr(e, "http_status"):
                    print(f"HTTP status code: {e.http_status}")  # type: ignore
                else:
                    print("An error occurred:", e, "token_used:", self.prompt_tokens + self.completion_tokens)
                if attempt < retries - 1:
                    await asyncio.sleep(4**attempt)
                else:
                    raise e
                
    def clear_history(self):
        """
        Clear the history of generated text.
        """
        self.history = []

    def save_history(self, path: str):
        """
        Save the history of generated text to a file.

        Args:
            path (str): The path to save the history.
        """
        with jsonlines.open(path, 'w') as writer:
            for item in self.history:
                writer.write(item)
