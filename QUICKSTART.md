# Quick Start Guide - Deep Research Agent

Get your AI research assistant running in 5 minutes.

## Prerequisites

- Python 3.8+
- OpenAI API key (with billing enabled)
- SendGrid account (free tier)

## Step 1: Install

```bash
# Clone repository
git clone https://github.com/csg09/ai-deep-research-agent.git
cd ai-deep-research-agent

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure

```bash
# Copy environment template
cp .env.example .env
```

Edit `.env`:

```env
OPENAI_API_KEY=sk-...your-key...
SENDGRID_API_KEY=SG....your-key...
SENDER_EMAIL=your-verified@email.com
RECIPIENT_EMAIL=recipient@email.com
```

### Get Your API Keys

**OpenAI**:
1. Visit https://platform.openai.com/api-keys
2. Create new key
3. Add billing method if needed

**SendGrid**:
1. Sign up at https://sendgrid.com/
2. Go to Settings → API Keys → Create
3. Verify sender email at Settings → Sender Authentication

## Step 3: Test

```bash
# Test email configuration
python test_email.py
```

Expected output:
```
✅ Success! Test email sent successfully.
```

## Step 4: Run Simple Search

```bash
python simple_search.py
```

This executes a single web search (~$0.025 cost).

## Step 5: Run Full Research

```bash
python deep_research.py
```

This runs the complete research workflow:
1. Plans 3 searches
2. Executes them in parallel
3. Generates comprehensive report
4. Emails the report to you

**Cost**: ~$0.10 - $0.30 per research query

## What You'll Get

A professional email with:
- Executive summary
- Comprehensive 1000+ word report in markdown
- Cited sources
- Follow-up research questions

## View Results

- **Email**: Check inbox (and spam folder!)
- **Traces**: https://platform.openai.com/traces
- **Costs**: https://platform.openai.com/usage

## Customize Your Research

Edit `deep_research.py`:

```python
# Change number of searches
HOW_MANY_SEARCHES = 5  # Default: 3

# Change search depth
SEARCH_CONTEXT_SIZE = "high"  # low, medium, high

# Change your research query
query = "Your research question here"
```

## Cost Management

Current costs:
- **WebSearchTool**: ~$0.025 per search
- **3 searches**: ~$0.075
- **Full report**: ~$0.10 - $0.30

To reduce costs:
- Lower `HOW_MANY_SEARCHES` to 2 or 1
- Use `search_context_size="low"`
- Set usage limits in OpenAI dashboard

## Common Issues

**Email not received**:
- Check spam folder
- Verify sender email in SendGrid
- Run `python test_email.py`

**API errors**:
- Verify API keys in `.env`
- Check billing is enabled
- Ensure OpenAI account has credits

**SSL errors**:
```bash
pip install --upgrade certifi
```

## Next Steps

1. Try different research queries
2. Adjust number of searches
3. Explore `examples/` directory
4. Check out structured_outputs.py
5. Review parallel_research.py patterns

## Resources

- [Full Documentation](README.md)
- [OpenAI Agents SDK](https://platform.openai.com/docs/agents)
- [OpenAI Traces](https://platform.openai.com/traces)
- [SendGrid Docs](https://docs.sendgrid.com/)

---

**Ready to research?** Start with `python simple_search.py` and scale up to `python deep_research.py`!
