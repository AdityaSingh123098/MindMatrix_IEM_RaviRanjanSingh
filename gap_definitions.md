# Communication Gap Definitions & Detection Logic

## Overview

Effective collaboration in distributed and asynchronous engineering teams depends on reliable conversational grounding—a shared mutual understanding between participants. When communication breaks down, projects suffer from delayed milestones, duplicate efforts, and interpersonal friction.

The **Communication Gap Detector** analyzes group conversation transcripts using deterministic, explainable, rule-based Natural Language Processing (NLP). It operates without external LLM dependencies, ensuring 100% data privacy, microsecond latency, zero hallucinations, and mathematically verifiable evidence.

---

## 1. Unanswered Question

### Definition
An interrogative message posed by a participant that receives no topical, temporal, direct, or confirmatory response from subsequent speakers in the conversation thread.

### Detection Mechanism
1. **Question Identification:**
   - Detects terminal question marks (`?`).
   - Identifies leading interrogative constructs (`who`, `what`, `when`, `where`, `why`, `how`, `which`, `is there`, `are there`, `can you`, `could you`).
2. **Subsequent Turn Analysis:**
   - Scans subsequent messages from other speakers.
   - Evaluates whether any subsequent message provides:
     - **Explicit Participant Mention:** e.g., `@Neha`, `Neha: ...`
     - **Temporal Anchoring:** For temporal questions (*"When"*, *"What time"*), checks for explicit time formats (`3:00 PM`, `10:30`, `at 4`, `noon`, `tomorrow`).
     - **Spatial/Resource Anchoring:** For location questions (*"Where"*), checks for storage or access coordinates (`repo`, `link`, `drive`, `room`, `zoom`).
     - **Topical Keyword Overlap:** Assesses shared non-stopword tokens between question and answer.
3. **Gap Flag:** If subsequent turns discuss unrelated topics or if the conversation ends without an answer, a gap is flagged with evidence identifying the deflection.

### Example
```text
Neha: What time is the meeting?
Ravi: I am working on the report.
Soham: I'll send the dataset.
```
* **Status:** Flagged as `Unanswered Question`
* **Speaker:** `Neha`
* **Evidence:** *"Question received no direct response. Subsequent responses shifted topics without addressing it (e.g., Ravi: 'I am working on the report.'; Soham: 'I'll send the dataset.')."*

### Impact on Teams
- Blocked dependencies while awaiting basic information.
- Frustration and feelings of being ignored by team members.
- Accidental scheduling conflicts or missed meetings.

---

## 2. Repeated Request

### Definition
An action or resource request that a participant must state two or more times because previous attempts were ignored, acknowledged without action, or left unfulfilled.

### Detection Mechanism
1. **Request Identification:**
   - Evaluates regular expressions targeting polite imperatives and requests:
     - `can you (please)? (send|share|provide|give|upload)`
     - `please (send|share|provide|give)`
     - `kindly (share|send|provide)`
     - `can someone (please)? (provide|share|send)`
     - `i need (you to|someone to)? (send|share)`
2. **Entity & Subject Extraction:**
   - Parses the object or action requested (e.g., `dataset`, `credentials`, `design mockups`).
3. **Fulfillment Tracking:**
   - Evaluates turns between the first request and subsequent requests.
   - Checks for resolution indicators (`sent`, `attached`, `here is`, `uploaded`).
   - If a duplicate or semantically overlapping request occurs without fulfillment, it flags the repetition.

### Example
```text
Ravi: Can you send the dataset?
Soham: Okay.
Ravi: Can you send the dataset?
```
* **Status:** Flagged as `Repeated Request`
* **Speaker:** `Ravi`
* **Evidence:** *"Request repeated without resolution. Originally requested in Message #1 by Ravi, and repeated in Message #3 by Ravi due to lack of fulfillment."*

### Impact on Teams
- Inefficient context switching and churn.
- Work stalls due to unavailable resources.
- Signals lack of accountability or follow-through.

---

## 3. Repeated Clarification

### Definition
Multiple expressions of confusion, ambiguity, or requests for elaboration occurring within a short conversation span. This indicates that a proposal, instruction, or explanation was poorly articulated.

### Detection Mechanism
1. **Clarification Expression Detection:**
   - Matches known clarification and confusion phrases:
     - `what do you mean?`
     - `can you clarify?` / `could you clarify?`
     - `please explain` / `can you explain?`
     - `which one?`
     - `what exactly?`
     - `i don't understand` / `not clear`
     - `what does that mean?`
     - `i'm confused`
2. **Frequency Threshold:**
   - If two or more clarification attempts occur within the conversation without resolving the underlying question, the system flags persistent ambiguity.

### Example
```text
Alex: We need to revamp the entire pipeline logic before tonight.
Ravi: What do you mean?
Alex: Just tweak the core modules.
Soham: Can you clarify?
Ravi: Which one?
```
* **Status:** Flagged as `Repeated Clarification`
* **Speakers:** `Soham`, `Ravi`
* **Evidence:** *"Multiple clarification requests detected (3 occurrences). Message #5 asks for clarification again ('Which one?'), indicating unresolved confusion in the discussion."*

### Impact on Teams
- Misunderstandings leading to wrong code implementations or broken contracts.
- Lengthy, circular discussions that waste sprint time.
- Cognitive fatigue and hesitation to ask further questions.

---

## 4. Unresolved Topic

### Definition
A discussion point, agenda item, proposal, or issue introduced into the dialogue that is subsequently sidetracked or abandoned without an explicit conclusion, decision, or action agreement.

### Detection Mechanism
1. **Topic Introduction Detection:**
   - Matches topic introduction triggers:
     - `about the [topic]`
     - `regarding the [topic]`
     - `discuss the [topic]`
     - `issue with the [topic]`
     - `update on the [topic]`
     - `decide on the [topic]`
     - `what about the [topic]?`
2. **Resolution Verification:**
   - Searches subsequent turns for resolution signals:
     - `fixed`, `resolved`, `done`, `completed`, `approved`, `agreed`, `decided`, `scheduled`, `merged`, `shipped`, `closed`.
   - Verifies whether the resolution signal references the introduced topic.
   - If no concluding agreement or action item is registered before the transcript ends, it is flagged as an `Unresolved Topic`.

### Example
```text
Neha: What about the budget for Q4?
Ravi: Let's focus on the client demo first.
Soham: Yes, the client demo is top priority today.
Neha: The demo looks stable on staging.
```
* **Status:** Flagged as `Unresolved Topic`
* **Speaker:** `Neha`
* **Evidence:** *"Topic 'budget Q4' was introduced but no resolution, decision, or concluding follow-up was found in the conversation."*

### Impact on Teams
- Loose ends that re-emerge right before product deadlines.
- Assumptions that "someone else is handling it".
- Lack of clear ownership and strategic drift.

---

## Summary Comparison Table

| Gap Category | Primary Linguistic Trigger | Resolution Requirement | Risk Severity |
| :--- | :--- | :--- | :--- |
| **Unanswered Question** | `?`, `who`, `what`, `when`, `where`, `why`, `how` | Contextual response, keyword alignment, or direct answering | High |
| **Repeated Request** | `can you send`, `please provide`, `kindly share` | Confirmation of delivery or shared resource | High |
| **Repeated Clarification** | `what do you mean`, `which one`, `clarify` | Specific explanatory elaboration | Medium |
| **Unresolved Topic** | `about the X`, `regarding X`, `issue with X` | Decision keyword (`approved`, `agreed`, `done`, etc.) | Medium-High |
