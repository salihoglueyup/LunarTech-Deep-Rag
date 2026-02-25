# Agentic Swarms & Swarm Studio

LunarTech utilizes a modular "Agent" design, evolving beyond single monolithic prompts.

## Swarm Studio

Swarm Studio is the visual pipeline builder of the ecosystem. It allows users to define custom agents with specific roles and tools, then string them together in an execution chain.

### Creating a Custom Agent

Users can define:

- **Agent Name**: Identification.
- **System Prompt**: The behavioral persona and instruction set of the agent.
- **Tools**: Web Search (DuckDuckGo integration) and Data Analyst (SQL generation integration) capabilities.

### Pipeline Execution

When a Swarm Pipeline is executed:

1. The **User Input** is fed into `Agent 1`.
2. `Agent 1` executes necessary tools, appends tool context, and generates a response.
3. The response of `Agent 1` becomes the direct explicit input of `Agent 2`.
4. This continues until the terminal agent produces the **Final Result**.

## Default Swarm Capabilities

By default, the platform is shipped with:

- **Analyst Agent**: Specializes in numerical analysis.
- **Translator Agent**: Pure localization.
- **Critic Agent**: Validating logical consistency and web-checking facts.
