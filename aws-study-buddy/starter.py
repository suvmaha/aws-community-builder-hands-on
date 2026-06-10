"""
Challenge 5: AWS Study Buddy — MCP-Powered Agent 🚀
====================================================
An interactive AWS documentation expert that:
- 📚 Searches & reads AWS docs via MCP server
- 🧠 Remembers what you've studied (persistent memory)
- 📝 Can quiz you on topics you've learned
- 🧮 Does calculations (cost estimates, etc.)
- ⚡ Streams responses in real time

MCP Server: awslabs.aws-documentation-mcp-server
Model: Amazon Nova Pro v1 via Bedrock
"""

import os
import json
from datetime import datetime

from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.tools import tool
from strands.tools.mcp import MCPClient
from mcp import StdioServerParameters, stdio_client

# --- Memory file path ---
MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "study_notes.json")


def _load_notes():
    """Load study notes from disk."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"topics": [], "notes": {}, "quiz_scores": []}


def _save_notes(data):
    """Save study notes to disk."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


# --- Custom Tools ---

@tool
def save_note(topic: str, summary: str) -> str:
    """Save a study note about an AWS topic for future reference.

    Args:
        topic: The AWS topic (e.g., 'S3', 'Lambda', 'DynamoDB').
        summary: A brief summary of what was learned.

    Returns:
        Confirmation that the note was saved.
    """
    notes = _load_notes()
    topic_lower = topic.lower()
    if topic_lower not in notes["topics"]:
        notes["topics"].append(topic_lower)
    notes["notes"][topic_lower] = {
        "summary": summary,
        "studied_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    _save_notes(notes)
    return f"📝 Note saved for '{topic}'! You've now studied {len(notes['topics'])} topics."


@tool
def get_notes(topic: str) -> str:
    """Retrieve study notes for a topic. Use 'all' to see all studied topics.

    Args:
        topic: The topic to look up, or 'all' to list everything studied.

    Returns:
        The stored notes or list of all topics.
    """
    notes = _load_notes()
    if topic.lower() == "all":
        if not notes["topics"]:
            return "📭 No study notes yet! Ask me about an AWS service to get started."
        result = f"📚 You've studied {len(notes['topics'])} topics:\n"
        for t in notes["topics"]:
            info = notes["notes"].get(t, {})
            studied_at = info.get("studied_at", "unknown")
            result += f"  • {t.upper()} (studied: {studied_at})\n"
        return result
    topic_lower = topic.lower()
    if topic_lower in notes["notes"]:
        info = notes["notes"][topic_lower]
        return f"📖 {topic.upper()}:\n{info['summary']}\n(Studied: {info['studied_at']})"
    # Fuzzy match
    for t in notes["topics"]:
        if topic_lower in t or t in topic_lower:
            info = notes["notes"][t]
            return f"📖 {t.upper()}:\n{info['summary']}\n(Studied: {info['studied_at']})"
    return f"No notes found for '{topic}'. Try asking me to explain it!"


@tool
def record_quiz_score(topic: str, score: int, total: int) -> str:
    """Record a quiz score for tracking progress.

    Args:
        topic: The topic that was quizzed.
        score: Number of correct answers.
        total: Total number of questions.

    Returns:
        Progress summary.
    """
    notes = _load_notes()
    notes["quiz_scores"].append({
        "topic": topic,
        "score": score,
        "total": total,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    _save_notes(notes)
    percentage = (score / total) * 100
    if percentage >= 80:
        return f"🌟 Excellent! {score}/{total} ({percentage:.0f}%) on {topic}!"
    elif percentage >= 60:
        return f"👍 Good job! {score}/{total} ({percentage:.0f}%) on {topic}. Keep practicing!"
    else:
        return f"📖 {score}/{total} ({percentage:.0f}%) on {topic}. Let's review this topic again!"


@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression. Useful for cost calculations.

    Args:
        expression: A math expression (e.g., '0.023 * 1000000 / 1000').

    Returns:
        The result.
    """
    try:
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return f"Invalid expression: {expression}"
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error: {str(e)}"


# --- Streaming Callback ---

def streaming_callback(**kwargs):
    """Stream text and show tool usage in real time."""
    if "data" in kwargs:
        print(kwargs["data"], end="", flush=True)
    if "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
        tool_name = kwargs["current_tool_use"]["name"]
        print(f"\n🔧 Using tool: {tool_name}", flush=True)


# --- Configure Model ---

model = BedrockModel(
    model_id="amazon.nova-pro-v1:0",
    region_name="us-east-1"
)

# --- MCP Server Connection ---

print("🔌 Connecting to AWS Documentation MCP Server...")

aws_docs_mcp = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["awslabs.aws-documentation-mcp-server@latest"],
            env={**os.environ, "FASTMCP_LOG_LEVEL": "ERROR"}
        )
    )
)

with aws_docs_mcp:
    # Get MCP tools
    mcp_tools = aws_docs_mcp.list_tools_sync()
    print(f"✅ Connected! Loaded {len(mcp_tools)} MCP tools from AWS Docs server.")

    # Combine MCP tools + custom tools
    all_tools = mcp_tools + [save_note, get_notes, record_quiz_score, calculator]

    # --- Create the Agent ---
    agent = Agent(
        model=model,
        system_prompt="""You are AWS Study Buddy 📚🤖 — an expert AWS tutor powered by official AWS documentation!

Your capabilities:
- 📚 Search and read official AWS documentation (via MCP tools)
- 📝 save_note: Save study summaries for topics the user learns
- 🔍 get_notes: Retrieve past study notes (use topic='all' to list everything)
- 🧮 calculator: Do math for cost estimates
- 📊 record_quiz_score: Track quiz results

Your behavior:
1. When the user asks about an AWS service, SEARCH the docs first, then explain clearly
2. After explaining a topic, ALWAYS save a brief note using save_note
3. When asked to quiz, create 3-5 questions based on saved notes
4. Be encouraging, use emojis, and make learning fun!
5. For cost questions, use the calculator tool
6. Keep explanations concise but accurate — cite the docs

Example interactions:
- "Explain S3" → Search docs → Explain → Save note
- "Quiz me on Lambda" → Check notes → Ask questions
- "What have I studied?" → get_notes(topic='all')
- "How much would 1M Lambda requests cost?" → Search pricing → Calculate""",
        tools=all_tools,
        callback_handler=streaming_callback
    )

    # --- Interactive Chat Loop ---
    print("\n" + "=" * 60)
    print("📚 AWS Study Buddy — Learn AWS with Official Docs + Memory")
    print("   Powered by: AWS Docs MCP Server + Amazon Nova Pro")
    print("   Features: Search docs, save notes, quiz yourself!")
    print("   Type 'quit' to exit")
    print("=" * 60)

    # Show existing study progress
    notes = _load_notes()
    if notes["topics"]:
        print(f"\n📊 Welcome back! You've studied {len(notes['topics'])} topics so far.")
        print(f"   Topics: {', '.join(t.upper() for t in notes['topics'][:5])}")
        if len(notes["topics"]) > 5:
            print(f"   ...and {len(notes['topics']) - 5} more!")

    while True:
        try:
            user_input = input("\n🧑 You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q"):
                notes = _load_notes()
                print(f"\n📊 Session complete! Total topics studied: {len(notes['topics'])}")
                print("👋 Goodbye! Your study notes are saved for next time.")
                break

            print("\n🤖 Study Buddy: ", end="", flush=True)
            response = agent(user_input)
            print()

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
