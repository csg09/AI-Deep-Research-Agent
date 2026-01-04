"""
Parallel Research Patterns

This script demonstrates advanced parallel execution patterns for
research tasks, including:
- Concurrent searches on different topics
- Race conditions for fastest results
- Timeout handling
- Error recovery in parallel tasks
"""

import asyncio
import time
from typing import List, Dict
from dotenv import load_dotenv

from agents import Agent, WebSearchTool, Runner, trace
from agents.model_settings import ModelSettings


load_dotenv(override=True)


# ============================================================================
# AGENT SETUP
# ============================================================================

SEARCH_INSTRUCTIONS = """You are a research assistant. Search the web and provide a concise 
2-3 paragraph summary of your findings."""

def create_search_agent():
    """Create a web search agent."""
    return Agent(
        name="Search Agent",
        instructions=SEARCH_INSTRUCTIONS,
        tools=[WebSearchTool(search_context_size="low")],
        model="gpt-4o-mini",
        model_settings=ModelSettings(tool_choice="required"),
    )


# ============================================================================
# PATTERN 1: Basic Parallel Searches
# ============================================================================

async def basic_parallel_searches():
    """Execute multiple searches in parallel."""
    print("="*60)
    print("Pattern 1: Basic Parallel Searches")
    print("="*60 + "\n")
    
    queries = [
        "OpenAI Agents SDK features",
        "LangGraph capabilities",
        "Crew AI framework overview"
    ]
    
    agent = create_search_agent()
    
    print(f"Executing {len(queries)} searches in parallel...")
    start_time = time.time()
    
    # Create tasks for parallel execution
    tasks = [Runner.run(agent, query) for query in queries]
    
    # Wait for all to complete
    results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start_time
    
    print(f"✅ Completed in {elapsed:.2f} seconds\n")
    
    for i, (query, result) in enumerate(zip(queries, results), 1):
        print(f"{i}. {query}")
        print(f"   Result: {result.final_output[:100]}...")
        print()


# ============================================================================
# PATTERN 2: Search with Timeout
# ============================================================================

async def search_with_timeout(query: str, timeout: int = 30):
    """Execute search with timeout."""
    agent = create_search_agent()
    
    try:
        result = await asyncio.wait_for(
            Runner.run(agent, query),
            timeout=timeout
        )
        return {"query": query, "result": result.final_output, "status": "success"}
    except asyncio.TimeoutError:
        return {"query": query, "result": None, "status": "timeout"}


async def parallel_with_timeouts():
    """Execute parallel searches with timeout protection."""
    print("="*60)
    print("Pattern 2: Parallel Searches with Timeouts")
    print("="*60 + "\n")
    
    queries = [
        "AI agent frameworks comparison",
        "Machine learning trends 2025",
        "LLM deployment best practices"
    ]
    
    print(f"Executing {len(queries)} searches with 30s timeout...")
    
    tasks = [search_with_timeout(query, timeout=30) for query in queries]
    results = await asyncio.gather(*tasks)
    
    print("\nResults:")
    for result in results:
        status_icon = "✅" if result["status"] == "success" else "⏱️"
        print(f"{status_icon} {result['query']}: {result['status']}")
    print()


# ============================================================================
# PATTERN 3: Race Condition - First to Finish
# ============================================================================

async def search_task(query: str, agent_id: int):
    """Execute a search task with ID."""
    agent = create_search_agent()
    start = time.time()
    result = await Runner.run(agent, query)
    elapsed = time.time() - start
    
    return {
        "agent_id": agent_id,
        "query": query,
        "result": result.final_output,
        "time": elapsed
    }


async def race_to_answer():
    """Race multiple agents to answer first."""
    print("="*60)
    print("Pattern 3: Race Condition - First to Finish")
    print("="*60 + "\n")
    
    query = "What are AI agents?"
    num_agents = 3
    
    print(f"Racing {num_agents} agents to answer: '{query}'...")
    
    # Create multiple tasks racing for the same query
    tasks = [search_task(query, i+1) for i in range(num_agents)]
    
    # Return when first one completes
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED
    )
    
    # Get the winner
    winner = list(done)[0].result()
    
    print(f"\n🏆 Winner: Agent {winner['agent_id']}")
    print(f"   Time: {winner['time']:.2f}s")
    print(f"   Result: {winner['result'][:150]}...")
    
    # Cancel remaining tasks
    for task in pending:
        task.cancel()
    
    print(f"\n   Cancelled {len(pending)} remaining tasks")
    print()


# ============================================================================
# PATTERN 4: Error Recovery
# ============================================================================

async def search_with_retry(query: str, max_retries: int = 3):
    """Execute search with retry logic."""
    agent = create_search_agent()
    
    for attempt in range(max_retries):
        try:
            result = await Runner.run(agent, query)
            return {"query": query, "result": result.final_output, "attempts": attempt + 1}
        except Exception as e:
            if attempt == max_retries - 1:
                return {"query": query, "result": None, "error": str(e), "attempts": attempt + 1}
            await asyncio.sleep(2 ** attempt)  # Exponential backoff


async def parallel_with_error_recovery():
    """Execute parallel searches with error recovery."""
    print("="*60)
    print("Pattern 4: Parallel Searches with Error Recovery")
    print("="*60 + "\n")
    
    queries = [
        "AI safety considerations",
        "Prompt engineering techniques",
        "RAG implementation patterns"
    ]
    
    print(f"Executing {len(queries)} searches with retry logic...")
    
    tasks = [search_with_retry(query, max_retries=3) for query in queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    print("\nResults:")
    for result in results:
        if isinstance(result, Exception):
            print(f"❌ Error: {result}")
        elif "error" in result:
            print(f"❌ {result['query']}: Failed after {result['attempts']} attempts")
        else:
            print(f"✅ {result['query']}: Success on attempt {result['attempts']}")
    print()


# ============================================================================
# PATTERN 5: Batch Processing with Limits
# ============================================================================

async def batch_parallel_searches(queries: List[str], batch_size: int = 3):
    """Process searches in batches to avoid overwhelming the API."""
    print("="*60)
    print("Pattern 5: Batch Processing with Concurrent Limits")
    print("="*60 + "\n")
    
    agent = create_search_agent()
    results = []
    
    print(f"Processing {len(queries)} queries in batches of {batch_size}...")
    
    for i in range(0, len(queries), batch_size):
        batch = queries[i:i+batch_size]
        print(f"\nBatch {i//batch_size + 1}: {len(batch)} queries")
        
        tasks = [Runner.run(agent, query) for query in batch]
        batch_results = await asyncio.gather(*tasks)
        results.extend(batch_results)
        
        print(f"  ✅ Completed batch {i//batch_size + 1}")
    
    print(f"\n✅ All {len(results)} searches completed")
    return results


async def demo_batch_processing():
    """Demonstrate batch processing."""
    queries = [
        "AI agent architecture",
        "LLM fine-tuning methods",
        "Vector database options",
        "Prompt optimization",
        "AI deployment strategies",
        "Token management",
        "Context window handling",
        "RAG best practices"
    ]
    
    await batch_parallel_searches(queries, batch_size=3)
    print()


# ============================================================================
# PATTERN 6: Progress Tracking
# ============================================================================

async def search_with_progress(query: str, index: int, total: int):
    """Execute search with progress reporting."""
    agent = create_search_agent()
    print(f"[{index}/{total}] Starting: {query[:50]}...")
    
    result = await Runner.run(agent, query)
    
    print(f"[{index}/{total}] ✅ Completed: {query[:50]}...")
    return result.final_output


async def parallel_with_progress():
    """Execute parallel searches with progress tracking."""
    print("="*60)
    print("Pattern 6: Parallel Searches with Progress Tracking")
    print("="*60 + "\n")
    
    queries = [
        "Multimodal AI applications",
        "AI ethics frameworks",
        "LLM evaluation metrics",
        "Agent memory systems",
        "Tool calling patterns"
    ]
    
    total = len(queries)
    
    tasks = [
        search_with_progress(query, i+1, total) 
        for i, query in enumerate(queries)
    ]
    
    results = await asyncio.gather(*tasks)
    
    print(f"\n✅ All {total} searches completed!")
    print()


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

async def main():
    """Run all parallel research pattern demonstrations."""
    
    print("\n" + "*"*60)
    print("PARALLEL RESEARCH PATTERNS")
    print("*"*60 + "\n")
    
    print("⚠️  Cost Warning: These demos use WebSearchTool")
    print("   Each search costs ~$0.025")
    print("   Total estimated cost: $0.30 - $0.60")
    print()
    
    # Demo 1: Basic parallel
    await basic_parallel_searches()
    
    # Demo 2: With timeouts
    await parallel_with_timeouts()
    
    # Demo 3: Race condition
    await race_to_answer()
    
    # Demo 4: Error recovery
    await parallel_with_error_recovery()
    
    # Demo 5: Batch processing
    await demo_batch_processing()
    
    # Demo 6: Progress tracking
    await parallel_with_progress()
    
    print("*"*60)
    print("All demonstrations completed!")
    print("*"*60)
    print("\nKey Patterns Demonstrated:")
    print("1. Basic parallel execution with asyncio.gather()")
    print("2. Timeout protection with asyncio.wait_for()")
    print("3. Race conditions with asyncio.wait()")
    print("4. Error recovery with retry logic")
    print("5. Batch processing to limit concurrency")
    print("6. Progress tracking for user feedback")
    print("\n📊 Check traces: https://platform.openai.com/traces")
    print()


if __name__ == "__main__":
    asyncio.run(main())
