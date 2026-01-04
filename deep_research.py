"""
Deep Research Agent System

This script implements a comprehensive automated research system that:
1. Plans optimal web searches for a query
2. Executes searches in parallel
3. Synthesizes findings into detailed reports
4. Delivers reports via email

COST NOTE: WebSearchTool costs ~$0.025 per search
A typical run with 3 searches costs ~$0.10-$0.30 total
"""

import os
import asyncio
from typing import Dict, List
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from agents import Agent, WebSearchTool, trace, Runner, function_tool
from agents.model_settings import ModelSettings

import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content


# Load environment variables
load_dotenv(override=True)


# ============================================================================
# CONFIGURATION
# ============================================================================

# Number of web searches to perform (adjust based on budget)
HOW_MANY_SEARCHES = int(os.environ.get('HOW_MANY_SEARCHES', 3))

# Search context size: "low", "medium", or "high"
SEARCH_CONTEXT_SIZE = os.environ.get('SEARCH_CONTEXT_SIZE', 'low')


# ============================================================================
# STRUCTURED OUTPUT SCHEMAS
# ============================================================================

class WebSearchItem(BaseModel):
    """Schema for a single web search."""
    reason: str = Field(
        description="Your reasoning for why this search is important to the query."
    )
    query: str = Field(
        description="The search term to use for the web search."
    )


class WebSearchPlan(BaseModel):
    """Schema for a complete search plan."""
    searches: list[WebSearchItem] = Field(
        description="A list of web searches to perform to best answer the query."
    )


class ReportData(BaseModel):
    """Schema for the final research report."""
    short_summary: str = Field(
        description="A short 2-3 sentence summary of the findings."
    )
    markdown_report: str = Field(
        description="The final report in markdown format"
    )
    follow_up_questions: list[str] = Field(
        description="Suggested topics to research further"
    )


# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

# Planner Agent - Decomposes queries into search terms
PLANNER_INSTRUCTIONS = f"""You are a helpful research assistant. Given a query, come up with a set of web searches \
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for."""

planner_agent = Agent(
    name="Planner Agent",
    instructions=PLANNER_INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=WebSearchPlan,
)


# Search Agent - Executes web searches and summarizes
SEARCH_INSTRUCTIONS = """You are a research assistant. Given a search term, you search the web for that term and \
produce a concise summary of the results. The summary must be 2-3 paragraphs and less than 300 \
words. Capture the main points. Write succinctly, no need to have complete sentences or good \
grammar. This will be consumed by someone synthesizing a report, so it's vital you capture the \
essence and ignore any fluff. Do not include any additional commentary other than the summary itself."""

search_agent = Agent(
    name="Search Agent",
    instructions=SEARCH_INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size=SEARCH_CONTEXT_SIZE)],
    model="gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required"),
)


# Writer Agent - Synthesizes research into reports
WRITER_INSTRUCTIONS = """You are a senior researcher tasked with writing a cohesive report for a research query. \
You will be provided with the original query, and some initial research done by a research assistant.

You should first come up with an outline for the report that describes the structure and \
flow of the report. Then, generate the report and return that as your final output.

The final output should be in markdown format, and it should be lengthy and detailed. Aim \
for 5-10 pages of content, at least 1000 words."""

writer_agent = Agent(
    name="Writer Agent",
    instructions=WRITER_INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ReportData,
)


# Email Agent - Formats and sends reports via email
EMAIL_INSTRUCTIONS = """You are able to send a nicely formatted HTML email based on a detailed report.
You will be provided with a detailed report. You should use your tool to send one email, providing the 
report converted into clean, well presented HTML with an appropriate subject line."""


# ============================================================================
# FUNCTION TOOLS
# ============================================================================

@function_tool
def send_email(subject: str, html_body: str) -> Dict[str, str]:
    """Send out an email with the given subject and HTML body."""
    sender_email = os.environ.get('SENDER_EMAIL')
    recipient_email = os.environ.get('RECIPIENT_EMAIL')
    
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(sender_email)
    to_email = To(recipient_email)
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()
    sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}


email_agent = Agent(
    name="Email Agent",
    instructions=EMAIL_INSTRUCTIONS,
    tools=[send_email],
    model="gpt-4o-mini",
)


# ============================================================================
# RESEARCH WORKFLOW FUNCTIONS
# ============================================================================

async def plan_searches(query: str) -> WebSearchPlan:
    """
    Use the planner agent to plan which searches to run for the query.
    
    Args:
        query: Research question or topic
        
    Returns:
        Structured search plan with queries and reasoning
    """
    print("📋 Planning searches...")
    result = await Runner.run(planner_agent, f"Query: {query}")
    plan = result.final_output
    
    print(f"✅ Will perform {len(plan.searches)} searches:")
    for i, search in enumerate(plan.searches, 1):
        print(f"   {i}. {search.query}")
        print(f"      Reason: {search.reason}")
    
    return plan


async def perform_searches(search_plan: WebSearchPlan) -> List[str]:
    """
    Execute all searches in the plan concurrently.
    
    Args:
        search_plan: Plan containing search items
        
    Returns:
        List of search result summaries
    """
    print(f"\n🔍 Executing {len(search_plan.searches)} searches in parallel...")
    
    # Create tasks for parallel execution
    tasks = [
        asyncio.create_task(search(item)) 
        for item in search_plan.searches
    ]
    
    # Execute all searches concurrently
    results = await asyncio.gather(*tasks)
    
    print("✅ Finished searching")
    return results


async def search(item: WebSearchItem) -> str:
    """
    Execute a single web search.
    
    Args:
        item: Search item with query and reasoning
        
    Returns:
        Concise summary of search results
    """
    input_msg = f"Search term: {item.query}\nReason for searching: {item.reason}"
    result = await Runner.run(search_agent, input_msg)
    print(f"   ✓ Completed: {item.query}")
    return result.final_output


async def write_report(query: str, search_results: List[str]) -> ReportData:
    """
    Synthesize search results into a comprehensive report.
    
    Args:
        query: Original research question
        search_results: List of search summaries
        
    Returns:
        Structured report with summary, full text, and follow-ups
    """
    print("\n📝 Generating comprehensive report...")
    
    input_msg = f"Original query: {query}\nSummarized search results: {search_results}"
    result = await Runner.run(writer_agent, input_msg)
    
    report = result.final_output
    print("✅ Report generated")
    print(f"   Summary: {report.short_summary}")
    print(f"   Word count: ~{len(report.markdown_report.split())} words")
    print(f"   Follow-up questions: {len(report.follow_up_questions)}")
    
    return report


async def email_report(report: ReportData) -> None:
    """
    Send the report via email.
    
    Args:
        report: Report data to send
    """
    print("\n📧 Sending email...")
    result = await Runner.run(email_agent, report.markdown_report)
    print("✅ Email sent successfully!")


# ============================================================================
# MAIN RESEARCH FUNCTION
# ============================================================================

async def conduct_research(query: str) -> ReportData:
    """
    Execute the complete research workflow.
    
    Args:
        query: Research question or topic
        
    Returns:
        Final research report
    """
    print("\n" + "="*60)
    print(f"🔬 DEEP RESEARCH: {query}")
    print("="*60 + "\n")
    
    with trace("Deep Research Workflow"):
        # Step 1: Plan searches
        search_plan = await plan_searches(query)
        
        # Step 2: Execute searches in parallel
        search_results = await perform_searches(search_plan)
        
        # Step 3: Synthesize into report
        report = await write_report(query, search_results)
        
        # Step 4: Email the report
        await email_report(report)
    
    print("\n" + "="*60)
    print("🎉 RESEARCH COMPLETED!")
    print("="*60 + "\n")
    
    return report


async def demo_research():
    """Run demonstration research queries."""
    
    # Example 1: AI Frameworks
    query1 = "Latest AI Agent frameworks in 2025"
    report1 = await conduct_research(query1)
    
    print("\n📊 REPORT PREVIEW:")
    print("-"*60)
    print(f"Summary: {report1.short_summary}\n")
    print("Follow-up questions:")
    for i, q in enumerate(report1.follow_up_questions, 1):
        print(f"{i}. {q}")
    
    # Example 2: Uncomment to run additional research
    # query2 = "Impact of AI on software development jobs"
    # await conduct_research(query2)


async def main():
    """Run the deep research system."""
    
    # Verify environment
    if not os.environ.get('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        return
    
    if not os.environ.get('SENDGRID_API_KEY'):
        print("❌ Error: SENDGRID_API_KEY not found in .env file")
        return
    
    print("\n" + "*"*60)
    print("AI DEEP RESEARCH AGENT")
    print("*"*60)
    print(f"\nConfiguration:")
    print(f"  - Searches per query: {HOW_MANY_SEARCHES}")
    print(f"  - Search context size: {SEARCH_CONTEXT_SIZE}")
    print(f"  - Estimated cost: ${HOW_MANY_SEARCHES * 0.025:.3f} - ${HOW_MANY_SEARCHES * 0.1:.3f}")
    print()
    
    # Run demonstration
    await demo_research()
    
    print("\n📊 View traces: https://platform.openai.com/traces")
    print("💰 Check costs: https://platform.openai.com/usage")
    print("📧 Check your email for the report!\n")


if __name__ == "__main__":
    asyncio.run(main())
