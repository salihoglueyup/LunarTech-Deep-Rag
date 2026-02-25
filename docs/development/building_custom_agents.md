# Building Custom Agents

LunarTech's Swarm Studio is incredibly powerful because it is extensible. While we ship with default agents (Analyst, Critic, Translator), you might want to create an agent specific to your company's domain (e.g., `LegalContractReviewer`).

## 1. Understanding the Agent Concept

An "Agent" in LunarTech is essentially a state-machine node. It requires:

- A very explicit **System Prompt**.
- A predefined schema of what it should **Ingest** (from the previous agent).
- A predefined schema of what it should **Output** (for the next agent).

## 2. Best Practices for System Prompts

When defining an Agent in Swarm Studio, do not treat it like ChatGPT. You must be definitive and procedural.

**Bad Prompt:**
> "Please read the text and write a legal summary. Make sure it sounds professional."

**Good Prompt:**
> "You are the Legal Review Agent.
>
> 1. You will receive a drafted contract.
> 2. You will scan for liability clauses.
> 3. You will output your findings STRICTLY using the following structure:
>
> ### Liability Risks
>
> - [Risk 1]
> - [Risk 2]
> IF NO RISKS ARE FOUND, output exactly: 'NO RISKS DETECTED'."

## 3. Tool Binding (In Development)

Currently, the Swarm Studio orchestrator in `core/swarm.py` automatically binds specific python tools based on the Agent's name.

If you name your agent `Analyst`, the backend will dynamically attach the `nlp_to_sql` tool.

To define a new programmatic tool:

1. Write the Python function in `services/tool_service.py`.
2. Register the tool in `core/agents.py` within the `AVAILABLE_TOOLS` dictionary.
3. Ensure the function includes thorough Google-style docstrings, as this is how the LLM understands how to invoke the tool.
