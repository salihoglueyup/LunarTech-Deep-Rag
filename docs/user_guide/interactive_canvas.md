# Interactive Canvas

LunarTech Deep RAG features an **Interactive Canvas**, inspired by modern AI coding/writing paradigms. It bridges the gap between chatting and document editing.

## Usage

Instead of just sending text messages back and forth in a linear chat, the Interactive Canvas offers a two-pane workspace.

1. **Left Pane (Chat & Control):** This is where you talk to the AI, give it directives to edit documents, and handle document management.
2. **Right Pane (Canvas):** This provides specialized views depending on the context:
   - **Document Viewer:** When a PDF is uploaded, it can natively render the physical PDF (e.g., rendering pages using `pdf.js` directly within Streamlit).
   - **Rich Text Editor / Markdown Render:** When generating artifacts, the AI's output is written to the right pane.

## Smart Features Integration

When using the Canvas, you can utilize the `Open in Canvas` buttons placed underneath AI chat messages. Clicking these buttons takes the AI's answer out of the narrow chat layout and projects it into the wide canvas where you can read and analyze it more effectively.
