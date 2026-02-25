# Smart Features Engine

Beyond simple RAG (Retrieval-Augmented Generation), LunarTech comes pre-packaged with a **Smart Features Engine**. This is an orchestration layer defined in `core/smart_features.py` that contains 28 distinct, highly-prompted AI workflows.

## The 28 Intelligent Operations

The engine categorizes the smart operations into five distinct categories based on cognitive load and use-case:

### 1. Extraction & Analysis

- **Auto Summary**: Condenses large documents into 3-paragraph executive summaries.
- **Key Findings**: Uses named-entity recognition instructions to extract only actionable intelligence.
- **Fact Checker**: Cross-references factual claims within the text against known external truths.

### 2. Content Generation

- **Quiz Generator**: Autonomously writes Multiple Choice, True/False, or Open-Ended exams based on document contents.
- **Flashcard Maker**: Generates spaced-repetition style Q&A pairs.

### 3. Structural Transformation

- **Mind Map Generator**: Re-formats text into a hierarchical, indented list suitable for rendering into Markdown or Mermaid mind maps.
- **SWOT Analysis**: Forces the LLM to process business/technical documents through a Strengths, Weaknesses, Opportunities, and Threats quadrant matrix.

## Technical Execution

When a user triggers a Smart Feature from the `AI Tools` view:

1. The `app.views.ai_tools.py` orchestrator calls the specific function from `core.smart_features.py`.
2. The function injects a highly rigorous "System Prompt" designed specifically for that task.
3. The LLM processes the user's selected document context.
4. The output is streamed synchronously back to the UI, formatted strictly according to the feature's specific Markdown template.
