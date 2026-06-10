# AWS Study Buddy — MCP + Strands Agents

An interactive CLI agent that searches official AWS documentation via MCP, explains services, saves study notes, and quizzes you on what you've learned.

## References

Based on the original blog post and code by **Dineshraj Dhanapathy** (AWS Community Builder):

- Blog: [Building an AWS Study Buddy with MCP + Strands Agents SDK](https://builder.aws.com/content/3EBFSHQD6b0TBD6hJnOM8h5p1B3/building-an-aws-study-buddy-with-mcp-strands-agents-sdk)
- Original repo: `Building-AI-Agents-from-Zero-to-Hero/challenge-5-mcp-agent`

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent framework | Strands Agents SDK |
| LLM | Amazon Nova Pro v1 (via Bedrock) |
| Knowledge source | AWS Documentation MCP Server |
| Memory | Persistent JSON file (`study_notes.json`) |
| Interface | Interactive CLI with streaming |

## Quick Start

See [playbook.md](playbook.md) for the full step-by-step run guide.

## What You Can Ask

| Category | Examples |
|----------|---------|
| Learn | "Explain Lambda", "What is DynamoDB?", "How does VPC work?" |
| Cost | "How much for 1M Lambda requests?", "S3 pricing for 500GB?" |
| Quiz | "Quiz me on S3", "Test my Lambda knowledge" |
| Progress | "What have I studied?", "Show my quiz scores" |
| Compare | "Difference between SQS and SNS?" |
