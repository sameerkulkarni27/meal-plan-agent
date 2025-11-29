from langchain.agents import create_agent
from dataclasses import dataclass
from tools import schedule_meal_reminder, end_conversation
from prompt import SYSTEM_PROMPT
from langgraph.checkpoint.memory import MemorySaver
import asyncio
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment!")

@dataclass
class RuntimeContext:
    user_id: str
    email: str

async def run_agent():
    """Run the interactive agent."""
    print("🍽️ Meal Reminder Scheduling Assistant")
    print("=" * 50)
    
    # Get user info for RuntimeContext
    user_id = input("Enter your user ID: ").strip()
    email = input("Enter your email: ").strip()
    print(f"\nScheduling reminders for {email}\n")
    
    # Create dynamic system prompt with actual values
    dynamic_prompt = f"""{SYSTEM_PROMPT}

    IMPORTANT CONTEXT:
    - The user's ID is: {user_id}
    - The user's email is: {email}
    - You MUST use these exact values when calling the meal_reminder_scheduler tool.
    - When the tool asks for user_id, pass: {user_id}
    - When the tool asks for email, pass: {email}
    """
    
    # Create agent with injected values in prompt
    agent = create_agent(
        model="openai:gpt-4o-mini",
        tools=[schedule_meal_reminder, end_conversation],
        system_prompt=dynamic_prompt,
        checkpointer=MemorySaver()
    )
    
    thread_id = f"user_{user_id}"
    
    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
        
        try:
            response = await agent.ainvoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config={
                    "configurable": {
                        "thread_id": thread_id
                    }
                }
            )
            
            ai_message = response["messages"][-1].content
            
            if "CONVERSATION_COMPLETE" in ai_message:
                print("Agent: Your reminders are scheduled. Have a great day! 👋\n")
                break
            
            print(f"Agent: {ai_message}\n")
            
        except Exception as e:
            print(f"[AGENT ERROR] Failed to invoke LLM: {str(e)}\n")

if __name__ == "__main__":
    asyncio.run(run_agent())

