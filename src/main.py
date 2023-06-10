"""
IdeaStorm
"""

import streamlit as st
from sidebar import setup as set_sidebar

from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    BaseMessage,
)
from langchain.chat_models import ChatOpenAI

from utils import (
    clear_submit,
    dialogue_agent_with_tools,
    dialogue_simulator,
    select_next_speaker,
    check_all_config,
    generate_agent_description,
    generate_system_message
)


set_sidebar()

topic = st.text_area("Topic for Agents to discuss", label_visibility="visible",
                     placeholder="ex - As the AI startups are growing, discuss how our grammar check SaaS can standout", on_change=clear_submit)

button = st.button("Submit")

names = {
    st.session_state["AGENT1_NAME"]: st.session_state["AGENT1_TOOLS"], 
    st.session_state["AGENT2_NAME"]: st.session_state["AGENT2_TOOLS"]
}

if button or st.session_state.get("submit"):
    if not st.session_state.get("is_key_configured"):
        st.error("Please configure your OpenAI and Airtable keys!", icon="🚨")
    elif not topic:
        st.error("Please enter a topic!", icon="🚨")
    else:
        st.session_state["submit"] = True
        if check_all_config():
            st.write('\n')
            st.markdown("##### Agents Profile & Topic Interpretation")
            with st.spinner():
                conversation_description = f"""Here is the topic of conversation: **{topic}** The participants are: **{', '.join(names.keys())}**"""
                agent_descriptions = {name: generate_agent_description(name, conversation_description) for name in names}
                for name, description in agent_descriptions.items():
                    st.write(description)

                agent_system_messages = {name: generate_system_message(name, description, tools, conversation_description) for (name, tools), description in zip(names.items(), agent_descriptions.values())}
                topic_specifier_prompt = [
                    SystemMessage(content="You can make a topic more specific."),
                    HumanMessage(content=
                        f"""{topic}
                        
                        You are the moderator.
                        Please make the topic more specific.
                        Please reply with the specified quest in {st.session_state.get("WORD_LIMIT")} words or less. 
                        Speak directly to the participants: {*names,}.
                        Do not add anything else."""
                        )
                ]
                specified_topic = ChatOpenAI(model_name=st.session_state.get("OPENAI_MODEL_CHOSEN"), temperature=1.0, openai_api_key=st.session_state.get("OPENAI_API_KEY"))(topic_specifier_prompt).content
                
                st.write(f":blue[**Original topic**:]\n{topic}\n")
                st.write(f":blue[**Detailed topic**:]\n{specified_topic}\n")

            st.divider()
            st.markdown("##### Context setting for Conversation")
            with st.spinner():
                agents = [dialogue_agent_with_tools(name=name, system_message=SystemMessage(content=system_message),
                                                    model=ChatOpenAI(model_name=st.session_state.get("OPENAI_MODEL_CHOSEN"), temperature=0.2,openai_api_key=st.session_state.get("OPENAI_API_KEY")),
                                                    tool_names=tools, top_k_results=2,) for (name, tools), system_message in zip(names.items(), agent_system_messages.values())]
                
                max_iters = st.session_state.get("TALKBACK_LIMIT")
                n = 0
                
                simulator = dialogue_simulator(agents=agents, selection_function=select_next_speaker)
                simulator.reset()
                simulator.inject('Moderator', specified_topic)
                st.write(f"(Moderator): {specified_topic}")
                st.write('\n')

            st.markdown("##### Conversation Between AI Agents")
            with st.spinner():
                while n < max_iters:
                    name, message = simulator.step()
                    st.write(f":blue[**({name})**:] {message}")
                    st.write('\n')
                    n += 1
            
            st.text("End of conversation")
            st.divider()
            
