"""
Simple Web Search Demo

This script demonstrates basic web search functionality using OpenAI's
WebSearchTool. It shows how to:
- Set up a search agent
- Execute a web search
- Get concise summaries
- View results in markdown format

COST NOTE: WebSearchTool costs ~$0.025 per search call
"""

import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, WebSearchTool, trace, Runner
from agents.model_settings import ModelSettings


# Load environment variables
load_dotenv(override=True)


# Agent configuration
SEARCH_INSTRUCTIONS = """You are a research assistant. Given a search term, you search the web for that term and \
produce a concise summary of the results. The summary must be 2-3 paragraphs and less than 300 \
words. Capture the main points. Write succinctly, no need to have complete sentences or good \
grammar. This will be consumed by someone synthesizing a report, so it's vital you capture the \
essence and ignore any fluff. Do not include any additional commentary other than the summary itself."""


def create_search_agent(context_size: str = "low"):
    """
    Create a web search agent.
    
    Args:
        context_size: Search context size - "low", "medium", or "high"
                     Higher context = more comprehensive but more expensive
    
    Returns:
        Configured search agent
    """
    return Agent(
        name="Search Agent",
        instructions=SEARCH_INSTRUCTIONS,
        tools=[WebSearchTool(search_context_size=context_size)],
        model="gpt-4o-mini",
        model_settings=ModelSettings(tool_choice="required"),
    )


async def simple_search(query: str, context_size: str = "low"):
    """
    Perform a simple web search and return summary.
    
    Args:
        query: Search term or question
        context_size: Search context size
        
    Returns:
        Search summary as string
    """
    print(f"\n{'='*60}")
    print(f"Searching for: {query}")
    print(f"Context size: {context_size}")
    print(f"{'='*60}\n")
    
    # Create agent
    search_agent = create_search_agent(context_size)
    
    # Execute search with tracing
    with trace(f"Simple Search: {query[:30]}..."):
        result = await Runner.run(search_agent, query)
    
    return result.final_output


async def compare_context_sizes(query: str):
    """
    Demonstrate different search context sizes.
    
    Args:
        query: Search term to test
    """
    print("\n" + "="*60)
    print("COMPARING SEARCH CONTEXT SIZES")
    print("="*60)
    
    context_sizes = ["low", "medium", "high"]
    
    for size in context_sizes:
        print(f"\n\n{'─'*60}")
        print(f"CONTEXT SIZE: {size.upper()}")
        print(f"{'─'*60}\n")
        
        result = await simple_search(query, context_size=size)
        print(result)
        print(f"\nWord count: {len(result.split())}")


async def multiple_searches():
    """Run multiple different searches."""
    queries = [
        "Latest AI Agent frameworks in 2025",
        "OpenAI Agents SDK vs LangGraph comparison",
        "Best practices for production AI agents"
    ]
    
    print("\n" + "="*60)
    print("MULTIPLE SEARCH QUERIES")
    print("="*60)
    
    for query in queries:
        result = await simple_search(query)
        print(f"\n{'-'*60}")
        print(f"Query: {query}")
        print(f"{'-'*60}")
        print(result)
        print()


async def main():
    """Run demonstrations."""
    
    # Check for API key
    if not os.environ.get('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        return
    
    print("\n" + "*"*60)
    print("SIMPLE WEB SEARCH DEMONSTRATIONS")
    print("*"*60)
    
    # Demo 1: Single search
    print("\n\n" + "="*60)
    print("DEMO 1: Single Web Search")
    print("="*60)
    
    query = "Latest AI Agent frameworks in 2025"
    result = await simple_search(query)
    
    print("\nRESULT:")
    print("-"*60)
    print(result)
    
    # Demo 2: Multiple searches (commented out to save cost)
    # Uncomment to run:
    # await multiple_searches()
    
    # Demo 3: Compare context sizes (expensive - use sparingly!)
    # Uncomment to run:
    # await compare_context_sizes("AI Agent frameworks 2025")
    
    print("\n\n" + "*"*60)
    print("DEMONSTRATIONS COMPLETED")
    print("*"*60)
    print("\n📊 Check traces at: https://platform.openai.com/traces")
    print("💰 Check costs at: https://platform.openai.com/usage")
    print()
    
    # Cost reminder
    print("\n⚠️  COST REMINDER:")
    print("   - Each WebSearchTool call: ~$0.025")
    print("   - This demo: ~$0.025 - $0.075")
    print("   - Monitor your usage in OpenAI dashboard")
    print()


if __name__ == "__main__":
    asyncio.run(main())
