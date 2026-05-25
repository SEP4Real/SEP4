---
title: "Process Report – StudyHelper"
date: "May 25, 2026"
author:
- Alexandru Savin(354790)
- Cristina Aurelia Matei (354776)
- Damian Michal Choina (354789)
- Eduard Fekete (355323)
- Jakub Maciej Baczek (354814)
- Karina Rubahova (354565)
- Mara-Ioana Statie (354536)
- Marta Zrno (355351)
- Piotr Junosz (355502)
- Tymoteusz Krzysztof Zydkiewicz (355413)
supervisor:
- Erland Ketil Larsen
- Joseph Chukwudi Okika
- Kasper Knop Rasmussen
- Markéta Tranberg
course: "SEP4"
semester: "4th Semester"
institution: "VIA University College"
---
<!-- ============================================================
  PROCESS REPORT — VIA Engineering Guidelines 2024 (Guideline 2)
  Purpose: Reflect on HOW you worked, not what you built.
  Tone: CONVERSATIONAL and SUBJECTIVE. Use first-person (I/we).
  This is the counterpart to the Project Report — include here
  anything that would be too personal/opinionated for that report.
  Content is visible to: your group, supervisor, and examiner.
  Constructive criticism is welcome; personal attacks are not.
  ============================================================ -->

# 1. Introduction

<!-- Introduce the project from a process perspective — not a technical one.
     Why did you choose this topic? What motivated the team?
     Give a factual overview of the project timeline and progress.
     Base this on actual data: logbook entries, meeting minutes, sprint records. -->

Provide a factual, chronological overview of the project from kick-off to submission,
grounded in concrete sources (logbook entries, meeting minutes, sprint retrospectives).
Highlight major milestones and any significant pivots in direction.]

We chose the project StudyHelper probably because of the relevance of the topic in all our lives. The idea of a device that can help navigate in choosing the best environment for studying was at the intersection of our interests and feasibility within the project scope. 

The initial phase of the project involved heavy brainstorming sessions and discussions. The main point of these debates was refining our problem statement to ensure it would be meaningful to solve with a solution that would be technically relevant for all sub-teams in a way that satisfies the overall expectations of the project.


# 2. Group Work

<!-- Describe WHO did WHAT and HOW the group functioned.
     Include personal profiles and cultural backgrounds where relevant —
     VIA projects are often multicultural and this context matters.
     Provide concrete examples from your collaboration to illustrate group dynamics. -->

## 2.1 Group Composition and Profiles

[Introduce each group member briefly — background, relevant skills, and prior
experience. If the group is multicultural or interdisciplinary, highlight this
and reflect on how it influenced the collaboration.]

| Member | Background     | Key Strengths | Role(s) in Project |
| :----- | :------------- | :------------ | :----------------- |
| [Name] | [Study/origin] | [Skills]      | [e.g. Backend, PM] |

## 2.2 Roles and Contributions

[Describe clearly how responsibilities were divided. Who led which areas?
Was the division planned or did it emerge organically?
Provide specific examples: "X took ownership of the database layer and
led the sprint planning sessions in weeks 3–6."]

## 2.3 Team Dynamics and Collaboration

<!-- Reflect on how the team actually functioned in practice.
     Reference relevant theory if your course requires it
     (e.g. Belbin roles, Tuckman stages, psychological safety). -->

[How did the team communicate day-to-day? What tools did you use (Discord, Jira, etc.)?
Were there informal leadership dynamics? How were decisions made — by consensus,
by vote, or by domain ownership?]

## 2.4 Conflict and Resolution

<!-- Only include if relevant. Be constructive — describe the situation and how
     it was handled, not who was at fault. -->

[Did any disagreements or tensions arise? How were they addressed?
What did the team learn from handling conflict?
If no significant conflict occurred, briefly note how the group maintained alignment.]

## 2.5 Social Loafing and Accountability

<!-- Include if relevant to your course description. -->

[Were there any instances where workload felt unevenly distributed?
How did the group ensure accountability? What mechanisms (standups, task boards,
peer review) helped keep everyone engaged?]

# 3. Project Initiation

<!-- Reflect on the BEGINNING of the project — how you got started.
     Cover: problem domain selection, problem statement formulation,
     time scheduling, and initial planning decisions. -->

## 3.1 Choosing the Problem Domain

[Why did your group choose this particular topic? Was it driven by personal interest,
practical relevance, available resources, or suggestions from a supervisor/company?
In hindsight, was this a good choice? What would you do differently?]

## 3.2 Problem Statement Development

[How did you arrive at the final problem statement? Describe the iterations.
Was the initial framing too broad, too narrow, or off-target?
What clarified your thinking — literature, supervisor input, prototyping?]

## 3.3 Time Planning and Scheduling

[How did you plan the project timeline? Did you use sprints, Gantt charts, or a
looser milestone structure? How realistic was the initial plan?
Reflect on deviations: what caused delays, and how were they managed?]

## 3.4 Ethical Perspectives

<!-- Required: consider ethical dimensions relevant to your problem area. -->

[What ethical questions arise from the problem your project addresses?
Consider: data privacy, environmental impact, fairness, accessibility, or societal effects.
Were these considerations built into the project from the start, or addressed reactively?]

# 4. Project Execution

<!-- Reflect on the MIDDLE of the project — how you actually worked through it.
     Focus on the process: what methods did you use and why, did they work,
     what surprised you, what would you change?
     Technical details belong in the Project Report — your reflections on
     using those techniques belong here. -->

This section describes the development process, divided into our collective efforts and team-specific contributions.

## 4.1 Together Process

This section describes the development process, divided into our collective efforts and team-specific contributions.

## 4.1 Together Process

[Describe how the whole group worked together during the execution phase.
How were the components (IoT, ML, Frontend) integrated?
How did we handle cross-team dependencies and API contracts?
Reflect on the effectiveness of our shared git workflow and communication.]

## 4.2 IOT Team Process

[... Describe the development of the embedded C code, hardware assembly, and testing. ...]

## 4.3 MAL Team Process

The Machine Learning and API (MAL) development followed an iterative path from data exploration to pipeline implementation. The following notes capture the key decisions and observations made during this process.

### 4.3.1 Mock Data Search and Goal Refinement

Initially, the focus was on how environmental noise influences focus. We attempted to combine datasets of focus-related noise effects with labeled sound categories from WAV files, extracting frequencies and loudness. However, we realized that "focus" cannot be measured directly. Consequently, we narrowed the goal to predicting a user-provided **Study Suitability Rating**, which made the target variable more grounded in user feedback.

### 4.3.2 Data Quality and Correlation Analysis

Further investigation led to the elimination of several datasets that appeared synthetic. We observed that in some candidate datasets, the distributions of features like humidity, noise, and light were suspiciously uniform, suggesting algorithmic generation rather than real sensor collection.

We also analyzed feature correlations as part of our validation process. Healthy datasets showed natural physical correlations (e.g., CO2, temperature, and humidity), while suspicious datasets exhibited either zero correlation or extreme overfitting potential. We decided to merge diverse datasets to create a more robust mock dataset.

### 4.3.3 Advanced Imputation Strategy

To handle missing values after merging, we implemented a sophisticated approach using the **MICE (Multivariate Imputation by Chained Equations)** framework. We enhanced this by:

- **Clustering**: Using k-means to find environment types (e.g., sessions made with high sun exposure vs. sessions made in labs).
- **ExtraTrees Estimator**: Modeling complex non-linear relationships.
- **Variance Modification**: Including natural distribution variance to avoid "flat average" imputation.
- **Global Median Fallback**: Used for extreme sparsity to prevent bias.

## 4.4 Frontend Team Process

[... Describe the development of the React application, UI/UX iterations, and integration with the backend API. ...]

## 4.5 Application of Methods and Theories

[Reflect on the engineering and analytical methods you applied (requirements analysis,
architecture design, testing frameworks, etc.). Were the methods well-suited to the
problem? Did you feel confident using them, or were there learning curves?
What worked well and what fell short?]

## 4.6 Challenges During Execution

[Describe the most significant technical or organisational challenges encountered.
How did the team respond? What was the outcome?
Examples: "The I2C sensor driver took much longer than expected," or
"The API contract changes caused significant rework in the frontend."]

## 4.7 Deviations from the Plan

[Compare what was planned versus what was actually executed.
What changed and why? Were changes proactive (intentional pivots) or reactive
(forced by circumstances)? How did the team adapt?]

## 4.8 Use of Tools and Technologies

[Reflect on the tools and technologies used throughout the project (IDEs, version
control, project management, testing frameworks, etc.). Were they effective?
Were there tools you wished you had used, or tools you regret choosing?]

# 5. Personal Reflections

<!-- INDIVIDUAL section — each group member writes their own subsection.
     Focus on YOUR OWN contribution, learning, and growth.
     Key requirements:
       - Refer to valid and reliable sources to support your reflections
       - "Reflect forward": define concrete future actions
       - Address: What did I learn? How did I learn it? What will I do differently?
     This section demonstrates your ability to identify and organise your own learning. -->

## 5.1 [Your Name]

### Learning Outcomes

[What new knowledge or skills did you gain during this project?
Were the learning goals from the course description met?
Be specific — "I learned X by doing Y, which resulted in Z."]

### Contribution and Role

[Honestly assess your own contribution to the group. Were you satisfied with
your level of involvement? Were there areas where you could have contributed more?
Were there areas where you exceeded your own expectations?]

### Challenges and Growth

[What was personally most challenging — technically, socially, or organisationally?
How did you respond to these challenges? What does this tell you about how you work?]

### Reflection Forward

[Based on this project, what will you deliberately do differently in future projects?
Identify 2–3 concrete actions. Reference learning theory or professional frameworks
if relevant (e.g. Kolb's learning cycle, growth mindset research).]

# 6. Reflection on Supervision

<!-- Reflect on the supervisor relationship from a student perspective.
     How did supervision affect the project? What made it effective or ineffective?
     What will you do more/less of in future to get more from supervision?
     This demonstrates your ability to engage constructively with external guidance. -->

## 6.1 The Supervision Process

[Describe how supervision was conducted. How often did you meet?
How did you prepare for meetings? What format did sessions typically take?]

## 6.2 Impact on the Project

[In what specific ways did supervision change or improve the project?
Were there suggestions or challenges from the supervisor that redirected your work?
Were there times you disagreed with feedback — how did you handle that?]

## 6.3 Lessons for Future Projects

[What will you do differently in your next supervised project?
Examples: prepare more structured agendas, present partial results earlier,
ask more targeted questions, be more proactive about seeking feedback.
Be concrete and actionable.]

# 7. Conclusion

<!-- GROUP section — written collectively as a summary.
     Provide a concise synthesis of what you learned about working together.
     The key deliverable here is a list of concrete recommendations for future groups. -->

## 7.1 Group Summary

[Summarise the group's overall experience. What defined this project's process?
What are the most important things you collectively learned — about software
engineering practice, teamwork, or the PBL learning model?
How has this project prepared you for professional work?]

## 7.2 Recommendations

[Produce a practical list of do's and don'ts for future groups undertaking a similar
project. These should be grounded in your actual experience — not generic advice.

**Do:**

- ...
- ...

**Avoid:**

- ...
- ...]

# 8. References

<!-- Use APA 7th edition format.
     Sources for reflective writing might include:
     - Learning theory (Kolb, Schön, Biggs)
     - Team dynamics (Belbin, Tuckman, Hackman)
     - Engineering methodology sources cited in reflections
     - Course descriptions and institutional guidelines

     APA examples:
     Author, A. A. (Year). Title of work. Publisher.
     Author, A. A. (Year). Article title. Journal, volume(issue), pages. https://doi.org/... -->

::: {#refs}
:::
