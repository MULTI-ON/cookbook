import os
import uuid
from typing import Any, Dict, List, Tuple, Union

from dotenv import dotenv_values
from langchain import OpenAI
from langchain.agents import AgentExecutor, ConversationalAgent, Tool
from langchain.agents.tools import BaseTool, InvalidTool
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.schema import AgentAction, AgentFinish
from prompts import FORMAT_INSTRUCTIONS, PREFIX, SUFFIX
from tools import get_tools

if not os.getenv("RENDER"):
    env_config = dotenv_values(".local.env")
    OPENAI_MODEL_NAME = env_config.get("OPENAI_MODEL_NAME", "text-davinci-003")
    OPENAI_API_KEY = env_config.get("OPENAI_API_KEY", "")
else:
    OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "text-davinci-003")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class PausingAgent(ConversationalAgent):
    def get_full_inputs(
        self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs: Any
    ) -> Dict[str, Any]:
        """Create the full inputs for the LLMChain from intermediate steps."""
        if not intermediate_steps and "agent_scratchpad" in kwargs:
            new_inputs = {
                "agent_scratchpad": kwargs["agent_scratchpad"],
                "stop": self._stop,
            }
        else:
            thoughts = self._construct_scratchpad(intermediate_steps)
            new_inputs = {"agent_scratchpad": thoughts, "stop": self._stop}
        full_inputs = {**kwargs, **new_inputs}
        return full_inputs


class PausingAgentExecutor(AgentExecutor):
    user: str = ""
    pausing_tool_name: str = ""

    def _pause(self, output: AgentAction, intermediate_steps: list):
        """Return the output and the intermediate steps, to be saved & reloaded later."""
        full_thoughts = self.agent._construct_scratchpad(intermediate_steps)
        final_output = {
            "output": output.tool_input,
            "paused": True,
            "agent_scratchpad": full_thoughts + output.log,
        }
        return {"output": final_output}

    def _return(self, output: AgentFinish, intermediate_steps: list) -> Dict[str, Any]:
        self.callback_manager.on_agent_finish(
            output, color="green", verbose=self.verbose
        )
        final_output = output.return_values
        if self.return_intermediate_steps:
            final_output["intermediate_steps"] = intermediate_steps
        final_output["paused"] = False
        return {"output": final_output}

    def _take_next_step(
        self,
        name_to_tool_map: Dict[str, Tool],
        color_mapping: Dict[str, str],
        inputs: Dict[str, str],
        intermediate_steps: List[Tuple[AgentAction, str]],
    ) -> Union[AgentFinish, Tuple[AgentAction, str]]:
        """Take a single step in the thought-action-observation loop.
        Override this to take control of how the agent makes and acts on choices.
        """
        # Call the LLM to see what to do.
        output = self.agent.plan(intermediate_steps, **inputs)
        # If the tool chosen is the finishing tool, then we end and return.
        if isinstance(output, AgentFinish):
            return output

        # Otherwise we lookup the tool
        if output.tool in name_to_tool_map:
            tool = name_to_tool_map[output.tool]
            self.callback_manager.on_tool_start(
                {"name": str(tool.func)[:60] + "..."},
                output,
                color="green",
                verbose=self.verbose,
            )
            if output.tool == self.pausing_tool_name:
                return self._pause(output, intermediate_steps)
            try:
                # We then call the tool on the tool input to get an observation
                observation = tool.func(output.tool_input, user=self.user)
                color = color_mapping[output.tool]
                return_direct = tool.return_direct
            except (KeyboardInterrupt, Exception) as e:
                self.callback_manager.on_tool_error(e, verbose=self.verbose)
                raise e
        else:
            self.callback_manager.on_tool_start(
                {"name": "N/A"}, output, color="green", verbose=self.verbose
            )
            observation = f"{output.tool} is not a valid tool, try another one."
            color = None
            return_direct = False
        llm_prefix = "" if return_direct else self.agent.llm_prefix
        self.callback_manager.on_tool_end(
            observation,
            color=color,
            observation_prefix=self.agent.observation_prefix,
            llm_prefix=llm_prefix,
            verbose=self.verbose,
        )
        if return_direct:
            # Set the log to "" because we do not want to log it.
            return AgentFinish({self.agent.return_values[0]: observation}, "")
        return output, observation


class AgentExecutorWithContext(AgentExecutor):
    """Consists of an agent using tools."""

    user: str = None

    def _take_next_step(
        self,
        name_to_tool_map: Dict[str, BaseTool],
        color_mapping: Dict[str, str],
        inputs: Dict[str, str],
        intermediate_steps: List[Tuple[AgentAction, str]],
    ) -> Union[AgentFinish, Tuple[AgentAction, str]]:
        """Take a single step in the thought-action-observation loop.
        Override this to take control of how the agent makes and acts on choices.
        """
        # Call the LLM to see what to do.
        output = self.agent.plan(intermediate_steps, **inputs)
        # If the tool chosen is the finishing tool, then we end and return.
        if isinstance(output, AgentFinish):
            return output
        self.callback_manager.on_agent_action(
            output, verbose=self.verbose, color="green"
        )
        # Otherwise we lookup the tool
        if output.tool in name_to_tool_map:
            tool = name_to_tool_map[output.tool]
            return_direct = tool.return_direct
            color = color_mapping[output.tool]
            llm_prefix = "" if return_direct else self.agent.llm_prefix
            observation = tool.func(output.tool_input, user=self.user)
            # We then call the tool on the tool input to get an observation
            # observation = tool.run(
            #     output.tool_input,
            #     verbose=self.verbose,
            #     color=color,
            #     llm_prefix=llm_prefix,
            #     observation_prefix=self.agent.observation_prefix,
            #     user=self.user,
            # )

        else:
            observation = InvalidTool().run(
                output.tool_input,
                verbose=self.verbose,
                color=None,
                llm_prefix="",
                observation_prefix=self.agent.observation_prefix,
            )
            return_direct = False
        if return_direct:
            # Set the log to "" because we do not want to log it.
            return AgentFinish({self.agent.return_values[0]: observation}, "")
        return output, observation


def setup_sync_agent(buffer=None, **kwargs):
    if buffer is None:
        buffer = []
    tools = get_tools()
    if kwargs.get("openai_api_key"):
        openai_api_key = kwargs.get("openai_api_key")
    else:
        openai_api_key = OPENAI_API_KEY
    llm = OpenAI(
        temperature=0,
        openai_api_key=openai_api_key,
        max_tokens=1000,
        model_name=OPENAI_MODEL_NAME,
    )
    agent = ConversationalAgent.from_llm_and_tools(
        llm=llm,
        tools=tools,
        prefix=PREFIX,
        suffix=SUFFIX,
        format_instructions=FORMAT_INSTRUCTIONS,
        ai_prefix="Mion",
    )
    print("buffer is ", buffer)
    # memory = ConversationBufferWindowMemory(
    #     buffer=buffer,
    #     input_key="input",
    #     output_key="output",
    #     memory_key="chat_history",
    #     k=3
    # )
    agent_executor = AgentExecutorWithContext.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        # memory=memory,
        # pausing_tool_name="Ask for Clarification",
        **kwargs,
    )
    return agent_executor
