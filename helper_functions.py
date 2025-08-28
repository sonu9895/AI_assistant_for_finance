from langchain.agents import initialize_agent, Tool, AgentType
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import init_chat_model
from transformers import pipeline
import torch

import os


os.environ["GOOGLE_API_KEY"] = "XXX"


input_message = [{
    "role": "system", "content":'''You are a helpful financial assistant.
        If you don't know the answer or need to look up current information use the DuckDuckGo Search tool
        If the user query is related to gold, silver, finance, investment, stock market etc, answer in detail about different options available for investment, recent trends, pros and cons, and suggest best possible options and answer in format that follows-
        Always finance query answer in a neat list:
            - Use numbered list (1., 2., 3.) for the main points.
            - For sub-points under each main point, use indented dashes (-).
            - Do not use bold text, asterisks, or markdown formatting.
            - Ensure indentation makes the hierarchy clear.''' },      
    ]





def speech_to_text(audio):
    pipe = pipeline(
            task="automatic-speech-recognition",
            model="openai/whisper-large-v3-turbo",
            torch_dtype=torch.float16,
            device="cpu",
            )
    
    result = pipe(audio, generate_kwargs={"language": "en"})
    print(result["text"])
    return result["text"]


def initialize_agentt(name):

    # 1. Create the search tool
    search = DuckDuckGoSearchRun()
    tools = [search]

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    

    try:
        # 2. Create the LLM
        llm = init_chat_model("gemini-2.5-flash-lite", model_provider="google_genai")

        # 3. Initialize agent
        agent_executor = initialize_agent(
            tools,
            llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
            memory=memory,
            max_iterations=2
        )
        message = input_message + [{"role": "user", "content": f"Hello, My name is {name}"}]
        ans = agent_executor.run(message)
        print(ans)
        return agent_executor


    except Exception as e:
        print("Error in initilizing agent with gemini, trying with gpt-2")
        return None


def get_llm_response(message, agent_executor):
    input = input_message+[{"role": "user", "content": message}]
    ans = agent_executor.run(input)
    print(ans)
    return ans
    


