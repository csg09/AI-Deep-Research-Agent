# AI Deep Research Agent

An intelligent multi-agent research system that automatically plans, executes web searches, synthesizes findings into comprehensive reports, and delivers them via email. Built with OpenAI's Agents SDK.

## 🎯 Overview

This project implements an automated research assistant that:
- Plans optimal web search strategies for any query
- Executes parallel web searches using OpenAI's WebSearchTool
- Synthesizes search results into detailed, coherent reports
- Formats reports as professional HTML emails
- Demonstrates structured outputs with Pydantic schemas

## ✨ Features

- **Intelligent Search Planning**: AI-powered query decomposition into optimal search terms
- **Parallel Execution**: Concurrent web searches for faster results
- **Structured Outputs**: Type-safe responses using Pydantic models
- **Comprehensive Reports**: 1000+ word markdown reports with citations
- **Automated Email Delivery**: Professional HTML-formatted email reports
- **Full Observability**: Complete tracing through OpenAI platform
- **Configurable Search Depth**: Adjustable search context size

## 🏗️ Architecture

### Multi-Agent System

```
Research Orchestrator (Your Code)
├── Planner Agent
│   ├── Input: Research query
│   └── Output: WebSearchPlan (structured)
│       ├── Search 1: Query + Reasoning
│       ├── Search 2: Query + Reasoning
│       └── Search 3: Query + Reasoning
│
├── Search Agent (parallel execution)
│   ├── Tool: WebSearchTool (OpenAI hosted)
│   └── Output: Concise summaries (2-3 paragraphs each)
│
├── Writer Agent
│   ├── Input: Query + Search summaries
│   └── Output: ReportData (structured)
│       ├── Short summary
│       ├── Markdown report (1000+ words)
│       └── Follow-up questions
│
└── Email Agent
    ├── Tool: send_email (function tool)
    └── Output: HTML formatted email
```

### Agentic Patterns

1. **Planning Pattern**: Planner agent decomposes complex queries
2. **Parallel Execution**: Multiple searches run concurrently
3. **Structured Outputs**: Type-safe responses with Pydantic
4. **Tool Integration**: Web search and email sending
5. **Synthesis**: Writer agent combines multiple sources

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key (with billing enabled)
- SendGrid account and API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/csg09/ai-deep-research-agent.git
cd ai-deep-research-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. Configure SendGrid:
   - Create account at [SendGrid](https://sendgrid.com/)
   - Verify your sender email
   - Create API key
   - Add to `.env`

### Quick Start

Run a simple web search:

```bash
python simple_search.py
```

Run the full research system:

```bash
python deep_research.py
```

Test email configuration:

```bash
python test_email.py
```

## 📁 Project Structure

```
ai-deep-research-agent/
├── README.md                  # This file
├── LICENSE                    # MIT License
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
│
├── simple_search.py          # Basic web search demo
├── deep_research.py          # Full research system
├── test_email.py             # Email configuration test
│
└── examples/
    ├── structured_outputs.py  # Pydantic schema examples
    ├── parallel_research.py   # Parallel search patterns
    └── custom_workflows.py    # Extensible workflow examples
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
SENDGRID_API_KEY=your_sendgrid_api_key_here
SENDER_EMAIL=your_verified_sender@example.com
RECIPIENT_EMAIL=your_recipient@example.com
```

### Customization

#### Adjust Number of Searches

In `deep_research.py`:

```python
HOW_MANY_SEARCHES = 3  # Change to 5, 10, etc.
```

#### Modify Search Context Size

```python
search_agent = Agent(
    tools=[WebSearchTool(search_context_size="low")],  # low, medium, high
    # ...
)
```

#### Customize Report Length

```python
INSTRUCTIONS = """
# ... 
Aim for 5-10 pages of content, at least 1000 words.  # Adjust as needed
"""
```

## 💰 Cost Considerations

### OpenAI WebSearchTool Pricing

- **Cost per search**: ~$0.025 (2.5 cents)
- **Typical research run**: 3 searches = ~$0.075
- **Full report generation**: ~$0.10-$0.30 total

**Note**: OpenAI may charge for multiple searches per call. Monitor your usage at [OpenAI Billing](https://platform.openai.com/account/billing).

### Cost Optimization

1. **Reduce searches**: Lower `HOW_MANY_SEARCHES` to 2 or 1
2. **Use smaller model**: Switch from `gpt-4o` to `gpt-4o-mini`
3. **Limit search context**: Use `search_context_size="low"`
4. **Cache results**: Store search results to avoid re-running

## 📊 Structured Outputs

This project demonstrates Pydantic-based structured outputs:

### Search Plan Schema

```python
class WebSearchItem(BaseModel):
    reason: str = Field(description="Reasoning for this search")
    query: str = Field(description="Search term to use")

class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(
        description="List of web searches to perform"
    )
```

### Report Schema

```python
class ReportData(BaseModel):
    short_summary: str = Field(description="2-3 sentence summary")
    markdown_report: str = Field(description="Full report in markdown")
    follow_up_questions: list[str] = Field(
        description="Topics to research further"
    )
```

Benefits:
- **Type safety**: Guaranteed response structure
- **Validation**: Automatic input validation
- **Documentation**: Self-documenting schemas
- **IDE support**: Autocomplete and type hints

## 🔍 Example Usage

### Basic Research Query

```python
query = "Latest AI Agent frameworks in 2025"

# Plan searches
search_plan = await plan_searches(query)

# Execute searches in parallel
search_results = await perform_searches(search_plan)

# Generate report
report = await write_report(query, search_results)

# Send via email
await send_email(report)
```

### Custom Research Workflow

```python
# Define your query
query = "Impact of quantum computing on cryptography"

# Run with custom trace
with trace("Quantum Crypto Research"):
    search_plan = await plan_searches(query)
    
    # Filter searches if needed
    filtered_searches = [
        s for s in search_plan.searches 
        if "quantum" in s.query.lower()
    ]
    
    # Execute
    results = await perform_searches(filtered_searches)
    report = await write_report(query, results)
```

## 📈 Monitoring and Debugging

All agent executions are traced. View at:

https://platform.openai.com/traces

Traces show:
- Search plan generation
- Individual web searches
- Report synthesis
- Email sending
- Token usage and costs

## 🛠️ Troubleshooting

### Web Search Errors

**Error**: `WebSearchTool not available`

**Solution**: Ensure you have OpenAI API key with billing enabled

### High Costs

**Issue**: Unexpectedly high costs

**Solutions**:
1. Check OpenAI usage dashboard
2. Reduce `HOW_MANY_SEARCHES`
3. Use `gpt-4o-mini` instead of `gpt-4o`
4. Set usage limits in OpenAI dashboard

### Email Not Sent

**Issue**: Report generated but email not received

**Solutions**:
1. Run `python test_email.py` to verify configuration
2. Check spam folder
3. Verify sender email in SendGrid
4. Check SendGrid activity feed

### SSL Errors

```bash
pip install --upgrade certifi
```

Then add to script:
```python
import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()
```

## 🎓 Learning Outcomes

This project demonstrates:

- **OpenAI Hosted Tools**: WebSearchTool integration
- **Structured Outputs**: Pydantic schema design
- **Parallel Execution**: Async/await patterns
- **Multi-Agent Orchestration**: Coordinating specialized agents
- **Report Generation**: Synthesizing multiple sources
- **Production Patterns**: Error handling, logging, configuration

## 🔄 Workflow Breakdown

### Step 1: Planning (Planner Agent)
- Input: User query
- Process: Decompose into optimal search terms
- Output: Structured search plan with reasoning

### Step 2: Searching (Search Agent × N)
- Input: Individual search items
- Process: Execute web searches in parallel
- Output: Concise summaries (2-3 paragraphs each)

### Step 3: Synthesis (Writer Agent)
- Input: Query + all search summaries
- Process: Create coherent narrative
- Output: Comprehensive report with follow-ups

### Step 4: Delivery (Email Agent)
- Input: Markdown report
- Process: Convert to HTML, format email
- Output: Professional email sent

## 🤝 Contributing

Contributions welcome! Areas for enhancement:

- [ ] Alternative search providers (Tavily, Serper, etc.)
- [ ] PDF report generation
- [ ] Citation management
- [ ] Multi-language support
- [ ] Report templates
- [ ] Cost tracking and budgets
- [ ] Caching layer for searches
- [ ] Web UI for queries
- [ ] Export to Google Docs
- [ ] Slack integration

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- Built with [OpenAI Agents SDK](https://platform.openai.com/docs/agents)
- Web search via [OpenAI WebSearchTool](https://platform.openai.com/docs/tools/web-search)
- Email delivery via [SendGrid](https://sendgrid.com/)
- Inspired by modern AI research workflows

## 📧 Contact

- GitHub: [@csg09](https://github.com/csg09)
- Project: [https://github.com/csg09/ai-deep-research-agent](https://github.com/csg09/ai-deep-research-agent)

## 🔗 Related Projects

- [AI Sales Automation Agent](https://github.com/csg09/ai-sales-automation-agent)
- [Multi-Model LLM Comparison](https://github.com/csg09)
- [OpenAI Agents Examples](https://github.com/csg09)

## ⚠️ Important Notes

- **API Costs**: WebSearchTool charges per search (~$0.025 each)
- **Rate Limits**: OpenAI has rate limits on searches
- **Data Privacy**: Research content sent to OpenAI for processing
- **Email Limits**: SendGrid free tier has daily sending limits
- **Production Use**: Add proper error handling and monitoring

---

**Transform any research query into a comprehensive report with AI-powered search and synthesis!** 🔍📊✉️
