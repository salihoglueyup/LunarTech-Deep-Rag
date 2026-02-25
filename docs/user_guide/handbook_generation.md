# Handbook Generator (AgentWrite)

Generating extensive, cohesive documents (like multi-page handbooks or academic papers) is a known challenge for modern LLMs due to context window degradation and attention shifting.

LunarTech solves this by employing the **AgentWrite** architecture.

## How it works

Instead of asking the LLM to write a 20,000-word book in a single prompt, the Handbook Generator follows a methodical phase-based approach:

1. **Global Planning**
   The system queries the Knowledge Graph and Vectors to gather overarching context. It then instructs the LLM to draft a structured "Table of Contents", estimating the word count required for each section.

2. **Iterative Generation**
   The system steps through the Table of Contents piece by piece. For each section, it runs a localized Deep RAG query specifically targeted at the section's topic.

3. **User-in-the-Loop Supervision**
   While the Handbook Generator *can* run autonomously, users have the option to review each draft section. You can accept the section, rewrite it manually, or provide feedback to the AI (e.g., "Make this section more academic") before moving to the next.

4. **Stitching and Export**
   Once all sections are approved, they are stitched together into a single, cohesive Markdown document which can then be exported iteratively to TXT, MD, or HTML file formats.
