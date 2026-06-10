# Playbook — AWS Study Buddy

**Estimated time:** ~15 min (clone ~1 min + AWS verify ~5 min + install ~3 min + run ~5 min)

An interactive CLI agent that searches official AWS documentation via MCP, explains services, saves study notes, and quizzes you. Powered by Amazon Nova Pro via Bedrock + Strands Agents SDK.

**Prerequisites:** AWS account with Bedrock access and Nova Pro enabled in us-east-1.

---

## Table of Contents

- [STEP 0 — Clone the Repo](#step-0--clone-the-repo)
- [STEP 1 — Create Virtual Environment](#step-1--create-virtual-environment)
- [STEP 2 — Verify Tools](#step-2--verify-tools)
- [STEP 3 — Verify AWS Credentials](#step-3--verify-aws-credentials)
- [STEP 4 — Verify Nova Pro Access](#step-4--verify-nova-pro-access)
- [STEP 5 — Install Python Dependencies](#step-5--install-python-dependencies)
- [STEP 6 — Run the Agent](#step-6--run-the-agent)

---

## STEP 0 — Clone the Repo

```bash
git clone https://github.com/suvmaha/aws-community-builder-hands-on.git
cd aws-community-builder-hands-on

# Set REPO_ROOT — all paths in this playbook are relative to here
export REPO_ROOT=$(pwd)
```

---

## STEP 1 — Create Virtual Environment

```bash
cd $REPO_ROOT/aws-study-buddy

python3 -m venv .venv
source .venv/bin/activate

# Verify
which python   # should point to .venv/bin/python
```

---

## STEP 2 — Verify Tools

```bash
python --version    # 3.11+
uvx --version       # from the uv package manager
```

Install `uv` if missing:
```bash
pip install uv
```

---

## STEP 3 — Verify AWS Credentials

```bash
export AWS_PROFILE=<your-profile>

aws sts get-caller-identity

# OUTPUT (example)
# {
#     "UserId": "AIDA...",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/..."
# }
```

If you do not have a profile configured, run `aws configure` first.

---

## STEP 4 — Verify Nova Pro Access

Nova Pro must be enabled in the Bedrock console before use. Check:

```bash
aws bedrock list-foundation-models \
  --region us-east-1 \
  --query "modelSummaries[?modelId=='amazon.nova-pro-v1:0'].{id:modelId,status:modelLifecycle.status}" \
  --output table

# OUTPUT (if enabled)
# ------------------------------------
# |    ListFoundationModels          |
# +---------------------+------------+
# |          id         |   status   |
# +---------------------+------------+
# |  amazon.nova-pro... |   ACTIVE   |
# +---------------------+------------+
```

If Nova Pro is not listed or not enabled:
1. Go to [Bedrock Console](https://console.aws.amazon.com/bedrock/) → select **us-east-1**
2. Navigate to **Model access** in the left sidebar
3. Find **Amazon Nova Pro** and request access
4. Wait for activation (usually instant)

---

## STEP 5 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## STEP 6 — Run the Agent

```bash
python starter.py

# OUTPUT
# 🔌 Connecting to AWS Documentation MCP Server...
# ✅ Connected! Loaded 3 MCP tools from AWS Docs server.
#
# ============================================================
# 📚 AWS Study Buddy — Learn AWS with Official Docs + Memory
#    Powered by: AWS Docs MCP Server + Amazon Nova Pro
#    Features: Search docs, save notes, quiz yourself!
#    Type 'quit' to exit
# ============================================================
#
# 🧑 You: Explain S3 in simple terms
#
# 🤖 Study Buddy:
# 🔧 Using tool: search_documentation
# 🔧 Using tool: read_documentation
#
# Amazon S3 (Simple Storage Service) is object storage! 🪣
# ...
# 🔧 Using tool: save_note
# 📝 Note saved for 'S3'! You've now studied 1 topic.
#
# 🧑 You: Quiz me on S3
#
# 🤖 Study Buddy:
# 🔧 Using tool: get_notes
# Q1: How many nines of durability does S3 have?
# ...
#
# 🧑 You: quit
# 📊 Session complete! Total topics studied: 1
# 👋 Goodbye! Your study notes are saved for next time.
```

> Study notes are saved to `study_notes.json` in this folder and persist across sessions.

---

## How It Works

```
starter.py
├── _load_notes() / _save_notes()   — read/write study_notes.json
├── save_note()                     — @tool: stores topic summary with timestamp
├── get_notes()                     — @tool: retrieves past notes (or lists all)
├── record_quiz_score()             — @tool: tracks quiz results
├── calculator()                    — @tool: evaluates math expressions
├── streaming_callback()            — prints text + tool names as they stream
├── aws_docs_mcp                    — MCPClient connecting to AWS Docs MCP server
└── Agent(model, tools, prompt)     — Strands agent combining MCP + custom tools
```

The agent loop:
```
User question
    ↓
Agent decides: search AWS docs (MCP)? save a note? quiz from notes?
    ↓
Executes tool(s), reads results
    ↓
Streams response back to terminal
```

---

## Common Issues

**`uvx: command not found`:**
Run `pip install uv` — `uvx` is bundled with `uv`.

**`aws: command not found`:**
Install the AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html

**`Bedrock access denied` or `nova-pro not found`:**
Enable Nova Pro in the Bedrock console (us-east-1) under **Model access**. See STEP 4.

**MCP connection timeout:**
Check your internet connection. The MCP server (`awslabs.aws-documentation-mcp-server`) is downloaded via `uvx` on first run — it needs network access.

**`No module named 'strands'`:**
Run `pip install -r requirements.txt` with your venv activated.
