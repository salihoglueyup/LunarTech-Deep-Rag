# Knowledge Graph Viewer

LunarTech extracts entities and relationships from uploaded documents rather than just performing isolated semantic searches. The **Knowledge Graph** view puts this data into your hands.

## Exploring the Graph

When you navigate to the `Knowledge Graph` tab from the sidebar, you will see a massive 3D-force-directed graph (powered by Apache ECharts).

### Time-Based Evolution

At the top of the interface is the **Timeline Slider**.
As you upload more documents, the graph grows. You can slide the timeline backwards to see how the graph looked when only the first foundational texts were ingested, and slide it forward to watch the AI connect new, esoteric concepts across multiple PDFs.

### Navigating the Nodes

- The nodes are clustered dynamically.
- `Entities` (Concepts, People, Technologies) are represented as glowing orbs.
- `Relations` are the lines connecting them.
- You can filter the view using the search bar on the left. Clicking any specific entity in the table will zoom the graph into its immediate neighborhood, showing direct connections.
