from typing import List, Dict, Any
from langchain.agents import AgentExecutor, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from tools.base_tools import get_tools

class AgentManager:
    def __init__(self, llm):
        self.llm = llm
        self.tools = get_tools()
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        
        self.agent_executor = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True
        )

    async def process_message(self, message: str) -> str:
        """Process a message using the agent."""
        try:
            response = await self.agent_executor.arun(input=message)
            return response
        except Exception as e:
            return f"Error processing message: {str(e)}"