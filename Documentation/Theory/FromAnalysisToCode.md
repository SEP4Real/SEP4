#### Analysis: Problem Focus (The "What")

This phase establishes the system's requirements and conceptual foundation, acting as a bridge between customers and programmers.

* **Problem Domain -> Goals:** The overarching business problem dictates the primary targets and scope.
* **Goals -> Use Cases:** High-level goals are translated into Use Case diagrams, identifying actors and system boundaries.
* **Use Cases -> Activity Diagrams & Descriptions:** The initial use cases expand into precise behavioral models. Activity diagrams map the flow of events, while detailed textual descriptions capture the step-by-step requirements.
* **Descriptions -> Domain Model:** Nouns and relationships extracted from the textual descriptions form the "Problem Domain Vocabulary." This shapes the conceptual Domain Model, a high-level class diagram devoid of software-specific details.

#### Design: Solution Focus (The "How")This phase translates the conceptual models into concrete software architecture, intended exclusively for programmers.

* **Domain Model -> System Sequence Diagrams:** The conceptual model transitions across the boundary, leading to the creation of System Sequence Diagrams (SSDs). These define the input/output events at the system boundary.
* **Domain Model -> Design Class Diagram:** The conceptual classes transition into software classes. This step ("Shape state & mapping") defines precise attributes, variable types, and method signatures.
* **Detailed Descriptions -> Detailed Sequence Diagrams:** The granular text requirements drive the creation of complex Sequence Diagrams. This step ("Extracting form" and "Detailed behaviour") maps exactly how specific objects interact in memory to fulfill a use case.
* **Sequence Diagrams <-> Design Class Diagram:** These two artifacts undergo continuous iterative refinement. The behavioral sequence interactions dictate the necessary operations required in the static class diagram.
* **Design Artifacts -> Code:** The finalized structural (Class) and behavioral (Sequence/State) diagrams form the complete blueprint, culminating directly in source code implementation.
