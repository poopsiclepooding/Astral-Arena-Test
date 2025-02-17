import ast
import asyncio
import json
from copy import deepcopy
from string import Template
from typing import TYPE_CHECKING, Any, List, Tuple

import httpx
from aiohttp import ClientSession
from colorama import Fore
from openai import OpenAI

from agentverse.agents import ExecutorAgent
from agentverse.llms.openai import DEFAULT_CLIENT_ASYNC as client_async
from agentverse.llms.utils.jsonrepair import JsonRepair
from agentverse.logging import logger
from agentverse.message import ExecutorMessage, Message, SolverMessage

from . import BaseExecutor, executor_registry

url = "http://127.0.0.1:8080"
SUMMARIZE_PROMPT = """Here is the text gathered from a webpage, and a question you need to answer from the webpage. 
-- Webpage -- 
${webpage}
-- Question --
${question}

Now summarize the webpage to answer the question. If the question cannot be answer from the webpage, return the summarization of the webpage."""


@executor_registry.register("tool-using")
class ToolUsingExecutor(BaseExecutor):
    num_agents: int = 3
    max_tool_call_times: int = 10
    tools: List[dict] = []
    tool_names: List[str] = []
    tool_config: str = None
    cookies: dict = {}
    tool_retrieval: bool = False
    real_execution_agents: dict = {}
    agent_names: List[str] = []
    # tool_description: str

    def __init__(self, *args, **kwargs):
        assert kwargs.get("tool_config", None) is not None
        with open(kwargs.get("tool_config"), "r") as f:
            tools_dict = json.load(f)
        tools = tools_dict["tools_json"]
        tool_names = [t["name"] for t in tools]

        # For each tool, we manually add a "thought" argument to achieve
        # chain-of-thought in OpenAI's function call.
        for t in tools:
            properties = t["parameters"]["properties"]
            thought = {
                "thought": {
                    "type": "string",
                    "description": "Your internal reasoning and thoughts on the task, and how you plan to solve it based on the current attempts.",
                }
            }
            thought.update(properties)
            t["parameters"]["properties"] = thought
            t["parameters"]["required"].insert(0, "thought")
        super().__init__(
            tools=tools,
            tool_names=tool_names,
            # tool_description=tool_description,
            *args,
            **kwargs,
        )

    async def astep(
        self,
        agent: ExecutorAgent,
        task_description: str,
        plans: List[SolverMessage],
        *args,
        **kwargs,
    ):
        plan_this_turn = {}
        agent_name_this_turn = []
        for i in range(len(plans)):
            name = plans[i].content.split("-")[0].strip()
            if name not in self.real_execution_agents:
                self.real_execution_agents[name] = deepcopy(agent)
                self.real_execution_agents[name].name = name
                self.agent_names.append(name)
            plan_this_turn[name] = plans[i].content.split("-")[1].strip()
            agent_name_this_turn.append(name)

        if self.tool_retrieval:
            # We retrieve 5 related tools for each agent
            tools_and_cookies = await asyncio.gather(
                *[
                    self.retrieve_tools(plan_this_turn[name], self.tools)
                    for name in agent_name_this_turn
                ]
            )
            tools = {
                name: t[0] for name, t in zip(agent_name_this_turn, tools_and_cookies)
            }
            cookies = {
                name: t[1] for name, t in zip(agent_name_this_turn, tools_and_cookies)
            }
            self.update_cookies(cookies)
        else:
            # We just use the tools that are provided in the config file
            tools = {name: self.tools for name in agent_name_this_turn}

        # Record the indices of agents that have finished their tasks
        # so that they will not be called again
        finished_agent_names = set()
        result = {name: "" for name in agent_name_this_turn}
        for current_turn in range(self.max_tool_call_times):
            if len(finished_agent_names) == len(agent_name_this_turn):
                # All agents have finished their tasks. Break the loop.
                break

            # Filter out agents that have finished and gather tool actions for the rest
            tool_calls = []
            active_agents_names = [
                name
                for name in agent_name_this_turn
                if name not in finished_agent_names
            ]
            for name in active_agents_names:
                if current_turn == self.max_tool_call_times - 1:
                    tool = [t for t in tools[name] if t["name"] == "submit_task"]
                else:
                    tool = tools[name]
                tool_calls.append(
                    self.real_execution_agents[name].astep(
                        task_description,
                        plan_this_turn[name],
                        tool,
                        current_turn=current_turn + 1,
                    )
                )
            # Use asyncio.gather to run astep concurrently
            tool_call_decisions = await asyncio.gather(*tool_calls)
            for name, tool_call_result in zip(active_agents_names, tool_call_decisions):
                self.real_execution_agents[name].add_message_to_memory(
                    [tool_call_result]
                )

            # Actually call the tool and get the observation
            tool_responses = await asyncio.gather(
                *[
                    ToolUsingExecutor.call_tool(
                        tool.tool_name,
                        tool.tool_input,
                        self.cookies.get(name, None),
                    )
                    for name, tool in zip(active_agents_names, tool_call_decisions)
                ]
            )
            # Update each agent's memory and check if they have finished
            cookies = {}
            for name, response in zip(active_agents_names, tool_responses):
                observation = response["observation"]
                is_finish = response["is_finish"]
                cookies[name] = response["cookies"]
                self.real_execution_agents[name].add_message_to_memory([observation])
                logger.info(
                    f"\nTool: {observation.tool_name}\nTool Input: {observation.tool_input}\nObservation: {observation.content}",
                    name,
                    Fore.YELLOW,
                )
                if is_finish:
                    finished_agent_names.add(name)
                    result[name] = observation.content
            self.update_cookies(cookies)

        message_result = []
        for name, conclusion in result.items():
            if conclusion != "":
                message_result.append(
                    ExecutorMessage(
                        content=f"[{name}]: My execution result:\n{conclusion}",
                        sender=name,
                    )
                )
        return message_result

    def update_cookies(self, cookies: dict):
        for name, cookie in cookies.items():
            self.cookies[name] = cookie

    @classmethod
    async def retrieve_tools(
        cls, plan: SolverMessage, curr_tools: List = [], cookies=None
    ):
        async with ClientSession(cookies=cookies) as session:
            if cookies is None:
                async with session.post(f"{url}/get_cookie", timeout=30) as response:
                    cookies = response.cookies
                    session.cookie_jar.update_cookies(cookies)
                    await response.text()
                    # Sometimes the toolserver's docker container is not ready yet
                    # So we need to wait for a while
                    await asyncio.sleep(10)
            async with session.post(
                f"{url}/retrieving_tools", json={"question": plan.content, "top_k": 5}
            ) as response:
                retrieved_tools = await response.json()
                retrieved_tools = ast.literal_eval(retrieved_tools)
        tools = deepcopy(curr_tools)
        existed_tool_names = set([t["name"] for t in tools])
        # Add the retrieved tools into the final tools
        for tool in retrieved_tools["tools_json"]:
            if tool["name"] not in existed_tool_names:
                existed_tool_names.add(tool["name"])
                tools.append(tool)
        return tools, cookies

    @classmethod
    async def call_tool(cls, command: str, arguments: dict, cookies=None):
        async def _summarize_webpage(webpage, question):
            summarize_prompt = Template(SUMMARIZE_PROMPT).safe_substitute(
                webpage=webpage, question=question
            )
            for _ in range(3):
                try:
                    response = await client_async.chat.completions.create(
                        messages=[{"role": "user", "content": summarize_prompt}],
                        model="gpt-3.5-turbo-16k",
                        functions=[
                            {
                                "name": "parse_web_text",
                                "description": "Parse the text of the webpage based on tthe question. Extract all related infomation about `Question` from the webpage. ! Don't provide information that is not shown in the webpage! ! Don't provide your own opinion!",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "summary": {
                                            "type": "string",
                                            "description": "Summary of the webpage with 50 words. Make sure all important information about `Question` is included. ! Don't provide information that is not shown in the webpage! ! Don't provide your own opinion!",
                                        },
                                        "related_details": {
                                            "type": "string",
                                            "description": "List all webpage details related to the question. Maximum 400 words. ! Don't provide information that is not shown in the webpage! ! Don't provide your own opinion!",
                                        },
                                        "useful_hyperlinks": {
                                            "type": "array",
                                            "description": "Maximum 3 items. Select useful hyperlinks in the webpage that related to the question. Make sure the url is useful for further browse. Don't provide repeated hyperlinks.",
                                            "items": {
                                                "type": "string",
                                                "description": "! Don't provide hyperlinks that is not shown in the webpage! ! Don't provide your own opinion!",
                                            },
                                        },
                                    },
                                    "required": [
                                        "summary",
                                        "related_details",
                                        "useful_hyperlinks",
                                    ],
                                },
                            }
                        ],
                        function_call={"name": "parse_web_text"},
                    )
                except Exception as e:
                    logger.error("Failed to call the tool. Exception: " + str(e))
                    continue
                arguments = ast.literal_eval(
                    JsonRepair(
                        response.choices[0].message.function_call.arguments
                    ).repair()
                )
                ret = (
                    "summary: "
                    + arguments["summary"]
                    + "\nrelated_details: "
                    + arguments["related_details"]
                    + "\nuseful_hyperlinks: ["
                    + ",".join(arguments["useful_hyperlinks"])
                    + "]\n"
                )

            return ret

        if command == "submit_task":
            return {
                "observation": ExecutorMessage(
                    content=f"Task Status: {arguments['status']}\nConclusion: {arguments['conclusion']}",
                    sender="function",
                    tool_name=command,
                    tool_input=arguments,
                ),
                "is_finish": True,
                "cookies": cookies,
            }
        if command == "":
            return {
                "observation": ExecutorMessage(
                    content=f"The function calling format is incorrect.",
                    sender="function",
                    tool_name=command,
                    tool_input=arguments,
                ),
                "is_finish": False,
                "cookies": cookies,
            }
        for i in range(3):
            try:
                async with httpx.AsyncClient(
                    cookies=cookies, trust_env=True
                ) as session:
                    if cookies is None:
                        async with session.post(
                            f"{url}/get_cookie", timeout=30
                        ) as response:
                            cookies = response.cookies
                            session.cookie_jar.update_cookies(cookies)
                            await response.text()
                            # Sometimes the toolserver's docker container is not ready yet
                            # So we need to wait for a while
                            await asyncio.sleep(10)

                    payload_arguments = deepcopy(arguments)
                    if "thought" in payload_arguments:
                        del payload_arguments["thought"]
                    payload = {
                        "tool_name": command,
                        "arguments": payload_arguments,
                    }
                    # async with ClientSession() as session:
                    async with session.post(
                        f"{url}/execute_tool",
                        json=payload,
                        timeout=30,
                    ) as response:
                        content = await response.text()
                        if command == "WebEnv_browse_website":
                            client_async.http_client = session
                            result = await _summarize_webpage(
                                content, arguments["goals_to_browse"]
                            )
                        elif command == "WebEnv_search_and_browse":
                            client_async.http_client = session
                            content = json.loads(content)

                            # for i in range(len(content)):
                            summarized = await asyncio.gather(
                                *[
                                    _summarize_webpage(
                                        content[i]["page"], arguments["goals_to_browse"]
                                    )
                                    for i in range(len(content))
                                ]
                            )
                            for i in range(len(content)):
                                content[i]["page"] = summarized[i]
                            result = ""
                            for i in range(len(content)):
                                result += f"SEARCH_REASULT {i}:\n"
                                result += content[i]["page"].strip() + "\n\n"
                            result = result.strip()
                        else:
                            result = content
                        message = ExecutorMessage(
                            content=result,
                            sender="function",
                            tool_name=command,
                            tool_input=arguments,
                        )
                    # async with session.post(
                    #     f"{url}/release_session", timeout=30
                    # ) as response:
                    #     await response.text()
                break
            except Exception as e:
                message = ExecutorMessage(
                    content="Failed to call the tool. Exception: " + str(e),
                    sender="function",
                    tool_name=command,
                    tool_input=arguments,
                )
                continue
        return {"observation": message, "is_finish": False, "cookies": cookies}

    def broadcast_messages(self, agents, messages) -> None:
        for agent in agents:
            agent.add_message_to_memory(messages)
