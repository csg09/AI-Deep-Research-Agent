"""
Structured Outputs Examples

This script demonstrates how to use Pydantic models to create
structured, type-safe outputs from AI agents.

Benefits:
- Guaranteed response structure
- Automatic validation
- Type safety and IDE support
- Self-documenting schemas
"""

import asyncio
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

from agents import Agent, Runner, trace


load_dotenv(override=True)


# ============================================================================
# EXAMPLE 1: Simple Structured Output
# ============================================================================

class CompanyInfo(BaseModel):
    """Schema for company information."""
    name: str = Field(description="Company name")
    industry: str = Field(description="Primary industry")
    founded_year: int = Field(description="Year founded")
    employee_count: str = Field(description="Approximate number of employees")
    description: str = Field(description="Brief company description")


async def demo_simple_structure():
    """Demonstrate basic structured output."""
    print("="*60)
    print("Demo 1: Simple Structured Output")
    print("="*60 + "\n")
    
    agent = Agent(
        name="Company Researcher",
        instructions="Extract company information from the query.",
        model="gpt-4o-mini",
        output_type=CompanyInfo
    )
    
    query = "Tell me about Anthropic, the AI safety company"
    
    with trace("Simple Structure Demo"):
        result = await Runner.run(agent, query)
    
    company = result.final_output
    
    print(f"Company: {company.name}")
    print(f"Industry: {company.industry}")
    print(f"Founded: {company.founded_year}")
    print(f"Employees: {company.employee_count}")
    print(f"Description: {company.description}")
    print()


# ============================================================================
# EXAMPLE 2: Nested Structured Output
# ============================================================================

class Feature(BaseModel):
    """Schema for a product feature."""
    name: str = Field(description="Feature name")
    description: str = Field(description="What the feature does")
    benefit: str = Field(description="User benefit")


class ProductAnalysis(BaseModel):
    """Schema for product analysis."""
    product_name: str = Field(description="Product name")
    category: str = Field(description="Product category")
    key_features: List[Feature] = Field(description="List of key features")
    target_audience: str = Field(description="Primary target audience")
    competitive_advantage: str = Field(description="Main competitive advantage")


async def demo_nested_structure():
    """Demonstrate nested structured output."""
    print("="*60)
    print("Demo 2: Nested Structured Output")
    print("="*60 + "\n")
    
    agent = Agent(
        name="Product Analyst",
        instructions="Analyze the product and extract structured information.",
        model="gpt-4o-mini",
        output_type=ProductAnalysis
    )
    
    query = "Analyze the iPhone as a product"
    
    with trace("Nested Structure Demo"):
        result = await Runner.run(agent, query)
    
    analysis = result.final_output
    
    print(f"Product: {analysis.product_name}")
    print(f"Category: {analysis.category}")
    print(f"Target Audience: {analysis.target_audience}")
    print(f"Competitive Advantage: {analysis.competitive_advantage}")
    print(f"\nKey Features ({len(analysis.key_features)}):")
    for i, feature in enumerate(analysis.key_features, 1):
        print(f"\n{i}. {feature.name}")
        print(f"   Description: {feature.description}")
        print(f"   Benefit: {feature.benefit}")
    print()


# ============================================================================
# EXAMPLE 3: Validated Structured Output
# ============================================================================

class ResearchPaper(BaseModel):
    """Schema for research paper with validation."""
    title: str = Field(description="Paper title")
    authors: List[str] = Field(description="List of authors")
    year: int = Field(description="Publication year")
    abstract: str = Field(description="Paper abstract")
    key_findings: List[str] = Field(
        description="List of 3-5 key findings",
        min_length=3,
        max_length=5
    )
    
    @validator('year')
    def validate_year(cls, v):
        """Ensure year is reasonable."""
        if v < 1900 or v > 2030:
            raise ValueError('Year must be between 1900 and 2030')
        return v
    
    @validator('authors')
    def validate_authors(cls, v):
        """Ensure at least one author."""
        if len(v) < 1:
            raise ValueError('Must have at least one author')
        return v


async def demo_validated_structure():
    """Demonstrate validated structured output."""
    print("="*60)
    print("Demo 3: Validated Structured Output")
    print("="*60 + "\n")
    
    agent = Agent(
        name="Paper Analyzer",
        instructions="Extract structured information about the research paper.",
        model="gpt-4o-mini",
        output_type=ResearchPaper
    )
    
    query = """Analyze this paper: 'Attention Is All You Need' by Vaswani et al., published in 2017. 
    It introduced the Transformer architecture for neural networks."""
    
    with trace("Validated Structure Demo"):
        result = await Runner.run(agent, query)
    
    paper = result.final_output
    
    print(f"Title: {paper.title}")
    print(f"Authors: {', '.join(paper.authors)}")
    print(f"Year: {paper.year}")
    print(f"Abstract: {paper.abstract}")
    print(f"\nKey Findings ({len(paper.key_findings)}):")
    for i, finding in enumerate(paper.key_findings, 1):
        print(f"{i}. {finding}")
    print()


# ============================================================================
# EXAMPLE 4: Optional Fields
# ============================================================================

class ArticleSummary(BaseModel):
    """Schema for article summary with optional fields."""
    headline: str = Field(description="Article headline")
    author: Optional[str] = Field(
        default=None,
        description="Article author (if available)"
    )
    date: Optional[str] = Field(
        default=None,
        description="Publication date (if available)"
    )
    summary: str = Field(description="Brief summary of the article")
    sentiment: str = Field(
        description="Overall sentiment: positive, negative, or neutral"
    )
    topics: List[str] = Field(description="Main topics covered")


async def demo_optional_fields():
    """Demonstrate optional fields in structured output."""
    print("="*60)
    print("Demo 4: Optional Fields")
    print("="*60 + "\n")
    
    agent = Agent(
        name="Article Summarizer",
        instructions="Summarize the article and extract structured information.",
        model="gpt-4o-mini",
        output_type=ArticleSummary
    )
    
    query = """Summarize: AI agents are transforming software development. 
    They can write code, debug, and even deploy applications autonomously."""
    
    with trace("Optional Fields Demo"):
        result = await Runner.run(agent, query)
    
    summary = result.final_output
    
    print(f"Headline: {summary.headline}")
    print(f"Author: {summary.author or 'Not specified'}")
    print(f"Date: {summary.date or 'Not specified'}")
    print(f"Sentiment: {summary.sentiment}")
    print(f"Topics: {', '.join(summary.topics)}")
    print(f"\nSummary: {summary.summary}")
    print()


# ============================================================================
# EXAMPLE 5: Complex Research Schema (like deep_research.py)
# ============================================================================

class SourceReference(BaseModel):
    """Schema for a source reference."""
    title: str = Field(description="Source title or description")
    url: Optional[str] = Field(
        default=None,
        description="URL if available"
    )
    relevance: str = Field(description="Why this source is relevant")


class DetailedReport(BaseModel):
    """Schema for a comprehensive research report."""
    executive_summary: str = Field(
        description="2-3 sentence executive summary"
    )
    main_findings: List[str] = Field(
        description="List of 5-7 main findings",
        min_length=5,
        max_length=7
    )
    detailed_analysis: str = Field(
        description="Detailed analysis (500+ words)"
    )
    sources: List[SourceReference] = Field(
        description="Key sources referenced"
    )
    recommendations: List[str] = Field(
        description="3-5 actionable recommendations"
    )
    limitations: str = Field(
        description="Limitations of this analysis"
    )


async def demo_complex_schema():
    """Demonstrate complex nested schema."""
    print("="*60)
    print("Demo 5: Complex Research Schema")
    print("="*60 + "\n")
    
    agent = Agent(
        name="Research Analyst",
        instructions="""You are a research analyst. Create a comprehensive report 
        on the given topic with structured findings, analysis, and recommendations.""",
        model="gpt-4o-mini",
        output_type=DetailedReport
    )
    
    query = "Analyze the impact of AI on software development productivity"
    
    with trace("Complex Schema Demo"):
        result = await Runner.run(agent, query)
    
    report = result.final_output
    
    print(f"Executive Summary:\n{report.executive_summary}\n")
    
    print(f"Main Findings ({len(report.main_findings)}):")
    for i, finding in enumerate(report.main_findings, 1):
        print(f"{i}. {finding}")
    
    print(f"\nSources ({len(report.sources)}):")
    for source in report.sources:
        print(f"- {source.title}")
        if source.url:
            print(f"  URL: {source.url}")
        print(f"  Relevance: {source.relevance}")
    
    print(f"\nRecommendations ({len(report.recommendations)}):")
    for i, rec in enumerate(report.recommendations, 1):
        print(f"{i}. {rec}")
    
    print(f"\nLimitations:\n{report.limitations}\n")


async def main():
    """Run all demonstrations."""
    print("\n" + "*"*60)
    print("STRUCTURED OUTPUTS DEMONSTRATIONS")
    print("*"*60 + "\n")
    
    await demo_simple_structure()
    await demo_nested_structure()
    await demo_validated_structure()
    await demo_optional_fields()
    await demo_complex_schema()
    
    print("*"*60)
    print("All demonstrations completed!")
    print("*"*60)
    print("\nKey Takeaways:")
    print("- Pydantic models ensure type-safe responses")
    print("- Field descriptions guide the AI's output")
    print("- Validators enforce constraints")
    print("- Optional fields handle missing data")
    print("- Nested models support complex structures")
    print("\n📊 Check traces: https://platform.openai.com/traces")
    print()


if __name__ == "__main__":
    asyncio.run(main())
