"""
Sidebar
"""

import streamlit as st
from utils import (
    validate_api_key,
    set_openai_api_key,
    set_logo_and_page_config
)

models = ['gpt-3.5-turbo','gpt-4']

def setup():
    with st.sidebar:
        set_logo_and_page_config()
        st.caption('⚠️ Experimental implementation.')
        with st.expander("How to use"):
            st.markdown(
                "1. Choose preferred OpenAI Model and provide your [OpenAI API key](https://platform.openai.com/account/api-keys) 🔑\n"
                "2. Configure the Agent Profile - Name, Description & Tools 💬\n")
            
        with st.expander("OpenAI Configuration"):
            st.session_state["OPENAI_MODEL_CHOSEN"] = st.selectbox('OpenAI Model', models, key='model', help="Learn more at [OpenAI Documentation](https://platform.openai.com/docs/models/)")
            api_key_input = st.text_input(
                    "OpenAI API Key",
                    type="password",
                    placeholder="sk-...",
                    help="You can get your API key from [OpenAI Platform](https://platform.openai.com/account/api-keys)", 
                    value=st.session_state.get("OPENAI_API_KEY", ""))
            if st.button('Configure', use_container_width=True, key="openAIconfig"):
                if validate_api_key(api_key_input):
                    st.session_state["is_key_configured"] = True
                    st.success('Successfully Configured!', icon="✅")
                else:
                    st.session_state["is_key_configured"] = False
                    error_message = 'Configuration failed. Please check the following input(s):'
                    if not validate_api_key(api_key_input):
                        error_message += '\n- OpenAI API Key format is invalid (should start with "sk-")'
                    st.error(error_message, icon="🚨")
            
            if api_key_input:
                set_openai_api_key(api_key_input)

        with st.expander("Generative Agent Configuration"):
            st.markdown("#### Agent 1")
            st.session_state["AGENT1_NAME"] = st.text_input('Name', value="", key="agent1n", placeholder="Marketing Intern")
            st.session_state["AGENT1_DESCRIPTION"] = st.text_input('Description', value="", key="agent1d", placeholder="Fresher. No industry experience.")
            st.session_state["AGENT1_TOOLS"] = st.multiselect('Tools', ['arxiv', 'ddg-search', 'wikipedia'], ['arxiv', 'ddg-search', 'wikipedia'], key="agent1t")


            st.markdown("#### Agent 2")
            st.session_state["AGENT2_NAME"] = st.text_input('Name', value="", key="agent2n", placeholder="Marketing Lead")
            st.session_state["AGENT2_DESCRIPTION"] = st.text_input('Description', value="", key="agent2d", placeholder="10Y+ industry experience.")
            st.session_state["AGENT2_TOOLS"] = st.multiselect('Tools', ['arxiv', 'ddg-search', 'wikipedia'], ['arxiv', 'ddg-search', 'wikipedia'],key="agent2t")

            st.markdown("General")
            st.session_state["WORD_LIMIT"] = st.number_input('Word Limit', value=50, step=10, help="Max. limit for an agent's message")
            st.session_state["TALKBACK_LIMIT"] = st.number_input('Talkback Limit', value=4, step=2, help="Max. conversations for both agents combined")

            if st.button('Configure', use_container_width=True, key="AgentConfig"):
                if st.session_state.get("AGENT1_NAME") and st.session_state.get("AGENT1_DESCRIPTION")  and st.session_state.get("AGENT2_NAME")  and st.session_state.get("AGENT2_DESCRIPTION")  and st.session_state.get("WORD_LIMIT")  and st.session_state.get("TALKBACK_LIMIT") :
                    st.success('Successfully Configured!', icon="✅")
                else:
                    error_message = 'Configuration failed. Please check the above input(s)'
                    st.error(error_message, icon="🚨")

        st.markdown("---")
        st.markdown(
            "Inspired from [Langchain - Agent Debate with Tools](https://python.langchain.com/en/latest/use_cases/agent_simulations/two_agent_debate_tools.html). \n"
        )
        st.markdown(
            "This tool is a work in progress. You can contribute to the project on [GitHub](https://github.com/ikram-shah/airtable-qna) \n"
        )
        st.markdown("Made by [ikramshah](https://twitter.com/ikram_shah_v)")