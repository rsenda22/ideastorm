"""
Utility functions
"""

import re
from PIL import Image
import streamlit as st
import pandas as pd

from typing import List, Dict, Callable
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts.prompt import PromptTemplate
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    BaseMessage,
)

from langchain.agents import Tool
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.agents import load_tools

def clear_submit():
    """
    Clears the 'submit' value in the session state.
    """
    st.session_state["submit"] = False

def validate_api_key(api_key_input):
    """
    Validates the provided API key.
    """
    api_key_regex = r"^sk-"
    api_key_valid = re.match(api_key_regex, api_key_input) is not None
    return api_key_valid

def set_logo_and_page_config():
    """
    Sets the Airtable logo image and page config.
    """
    im = Image.open("src/utilities/ideastorm.png")
    st.set_page_config(page_title="IdeaStorm", page_icon=im, layout="wide")
    st.markdown("# IdeaStorm")

def set_openai_api_key(api_key: str):
    """
    Sets the OpenAI API key in the session state.
    """
    st.session_state["OPENAI_API_KEY"] = api_key

class DialogueAgent:
    def __init__(
        self,
        name: str,
        system_message: SystemMessage,
        model: ChatOpenAI,
    ) -> None:
        self.name = name
        self.system_message = system_message
        self.model = model
        self.prefix = f"{self.name}: "
        self.reset()
        
    def reset(self):
        self.message_history = ["Here is the conversation so far."]

    def send(self) -> str:
        """
        Applies the chatmodel to the message history
        and returns the message string
        """
        message = self.model(
            [
                self.system_message,
                HumanMessage(content="\n".join(self.message_history + [self.prefix])),
            ]
        )
        return message.content

    def receive(self, name: str, message: str) -> None:
        """
        Concatenates {message} spoken by {name} into message history
        """
        self.message_history.append(f"{name}: {message}")


class dialogue_simulator:
    def __init__(
        self,
        agents: List[DialogueAgent],
        selection_function: Callable[[int, List[DialogueAgent]], int],
    ) -> None:
        self.agents = agents
        self._step = 0
        self.select_next_speaker = selection_function
        
    def reset(self):
        for agent in self.agents:
            agent.reset()

    def inject(self, name: str, message: str):
        """
        Initiates the conversation with a {message} from {name}
        """
        for agent in self.agents:
            agent.receive(name, message)

        # increment time
        self._step += 1

    def step(self) -> tuple[str, str]:
        # 1. choose the next speaker
        speaker_idx = self.select_next_speaker(self._step, self.agents)
        speaker = self.agents[speaker_idx]

        # 2. next speaker sends message
        message = speaker.send()

        # 3. everyone receives message
        for receiver in self.agents:
            receiver.receive(speaker.name, message)

        # 4. increment time
        self._step += 1

        return speaker.name, message
    
class dialogue_agent_with_tools(DialogueAgent):
    def __init__(
        self,
        name: str,
        system_message: SystemMessage,
        model: ChatOpenAI,
        tool_names: List[str],
        **tool_kwargs,
    ) -> None:
        super().__init__(name, system_message, model)
        self.tools = load_tools(tool_names, **tool_kwargs)

    def send(self) -> str:
        """
        Applies the chatmodel to the message history
        and returns the message string
        """
        agent_chain = initialize_agent(
            self.tools, 
            self.model, 
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, 
            verbose=True, 
            memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        )
        message = AIMessage(content=agent_chain.run(
            input="\n".join([
                self.system_message.content] + \
                self.message_history + \
                [self.prefix])))
        
        return message.content



agent_descriptor_system_message = SystemMessage(
    content="You can add detail to the description of the conversation participant.")

def generate_agent_description(name, conversation_description):
    agent_specifier_prompt = [
        agent_descriptor_system_message,
        HumanMessage(content=
            f"""{conversation_description}
            Please reply with a creative description of {name}, in {st.session_state.get("WORD_LIMIT")} words or less. 
            Speak directly to {name}.
            Give them a point of view.
            Do not add anything else."""
            )
    ]
    agent_description = ChatOpenAI(model_name=st.session_state.get("OPENAI_MODEL_CHOSEN"), temperature=1.0, openai_api_key=st.session_state.get("OPENAI_API_KEY"))(agent_specifier_prompt).content
    return agent_description
        
def generate_system_message(name, description, tools, conversation_description):
    return f"""{conversation_description}
    
    Your name is {name}.

    Your description is as follows: {description}

    Your goal is to persuade your conversation partner of your point of view.

    DO look up information with your tool to refute your partner's claims.
    DO cite your sources.

    DO NOT fabricate fake citations.
    DO NOT cite any source that you did not look up.

    Do not add anything else.

    Stop speaking the moment you finish speaking from your perspective.
    """

def select_next_speaker(step: int, agents: List[DialogueAgent]) -> int:
    idx = (step) % len(agents)
    return idx

def check_all_config():
    if st.session_state.get("AGENT1_NAME") and st.session_state.get("AGENT1_DESCRIPTION")  and st.session_state.get("AGENT2_NAME")  and st.session_state.get("AGENT2_DESCRIPTION")  and st.session_state.get("WORD_LIMIT")  and st.session_state.get("TALKBACK_LIMIT") and st.session_state.get("OPENAI_MODEL_CHOSEN") and st.session_state.get("OPENAI_API_KEY"):
        return True
    else:
        return False