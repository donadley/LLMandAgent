from typing import List, Dict, Any
from langchain.agents import AgentExecutor, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
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
            verbose=True,
            handle_parsing_errors=True,
            system_message="""You are a helpful AI assistant with access to various tools. Follow these guidelines:

1. When you receive a question, decide ONCE if you need a tool.
2. If you use a tool and get a response, provide that response to the user directly without further thinking.
3. For web searches about general topics, animals, history, etc., use the web_search tool immediately.
4. For weather queries, use the weather tool immediately.
5. For calculations, use the calculator tool immediately.
6. Never reconsider your tool choice after getting a response.
7. Always provide the tool's response directly to the user.

Remember: One decision, one tool use, direct response."""
        )

    async def process_message(self, message: str) -> str:
        """Process a message using the agent."""
        try:
            response = await self.agent_executor.arun(
                input=message
            )
            return response
        except Exception as e:
            return f"Error processing message: {str(e)}"