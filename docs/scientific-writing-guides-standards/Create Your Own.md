# Create Your Own

<sources\_index>
1. \*\*Nature Cancer (2023):\*\* Editorial on balancing informativeness with accessibility, defining the "narrative thread" and the "information sandwich" (IMRAD) structure.
2. \*\*Medvedev (2020):\*\* Ten rules for algorithmic bioinformatics, mandating clear novelty statements and rigorous arguments for methodological correctness.
3. \*\*Romano & Moore (2020):\*\* Guidelines for scientific software papers, emphasizing usability, open-source hosting, and transparent documentation.
4. \*\*Sainani SciWrite 2.3:\*\* Instructional module on active-voice defaults to ensure subject accountability and sentence vigor.
5. \*\*Sainani SciWrite 4.4:\*\* Analysis of the writing process, advocating for rapid drafting followed by rigorous clutter elimination and verb optimization.
6. \*\*SciWrite Demo Edit 3:\*\* Technical editing demonstration focusing on the front-loading of significant findings and the removal of technical jargon.
7. \*\*SciWrite Demo Edit 4:\*\* Review of data analytics prose, emphasizing parallel structure, concrete illustrations, and active-voice transformations.
8. \*\*UCR Graduate Writing Center:\*\* Technical guide for active vs. passive voice, providing diagnostic corrections for dangling modifiers and nominalization.
9. \*\*Steven Pinker (Columbia Blog):\*\* Analysis of "academese," identifying cognitive barriers and the necessity of direct, classic-style prose.
10. \*\*IMRAD Structure Guide:\*\* Definitive manual for the Introduction, Methods, Results, and Discussion architecture.
11. \*\*Stop-Slop Examples:\*\* Source repository for identifying and remediating "slop" or low-quality automated text to maintain document integrity.
12. \*\*Writing Principles & Process:\*\* The absolute ground truth for reader-centricity, the C-C-C paragraph framework, and the "Four Tests" (Elevator Pitch, Independence, So What, Formatting).
</sources\_index>

# TECHNICAL WRITING STANDARDS (TWS) v1.0

## 2. VOICE & REGISTER (V)
Voice and register are not stylistic preferences; they are precision-engineered tools for establishing accountability and minimizing cognitive load. Modern scientific disclosure requires a mandatory shift from the "impersonal" passive voice toward active-voice defaults. By identifying the actor, the writer eliminates ambiguity and creates a direct narrative that prioritizes data transfer over prose deciphering.

\*   \*\*V1: Default to Active Voice.\*\* Authors must use the active voice for all sections unless the actor is explicitly unknown or irrelevant to the technical outcome. \[Sources: UCR, Sainani 2.3\]
\*   \*\*V2: Mandatory First-Person Pronouns.\*\* Use "I" or "We" to describe specific experimental interventions (e.g., "We sequenced..." rather than "Sequencing was performed"). \[Sources: UCR, IMRAD Guide\]
\*   \*\*V3: Selective Passive Voice in Methods.\*\* The passive voice is reserved exclusively for the Methods section when the procedure must take precedence over the researcher. \[Sources: UCR, IMRAD Guide\]
\*   \*\*V4: Link Hedging to Data Type.\*\* For correlational data, authors must use "suggests" or "indicates." Avoid excessive hedging such as "it would seem that," which undermines professional credibility. \[Source: Writing Principles\]
\*   \*\*V5: Prohibit Anthropomorphism.\*\* Attribution of human intent to inanimate objects or data—such as "the data wants to show"—is strictly prohibited. \[Source: Writing Principles\]

Once the voice is established, the individual functional units—sentences—must be optimized for speed of comprehension.

## 3. SENTENCE CONSTRUCTION (S)
Sentences are the fundamental functional units of a scientific argument. High-fidelity technical writing prioritizes the immediate transfer of information, requiring sentences to be constructed such that the reader never backtracks to locate a subject or main verb.

\*   \*\*S1: Eliminate "Throat-Clearing" Fillers.\*\* Prohibit introductory phrases that lack semantic value, such as "It is important to note that," "There is," or "It has been shown that." \[Sources: Sainani 4.4, Writing Principles\]
\*   \*\*S2: Sentence Bifurcation.\*\* Any sentence exceeding 25 words must be bifurcated into distinct functional units to prevent information bloat. \[Source: Writing Principles\]
\*   \*\*S3: Fix Dangling Modifiers.\*\* Introductory phrases must modify the immediate subject of the sentence (e.g., "To examine cells, we used..." not "To examine cells, the microscope was used..."). \[Source: UCR\]
\*   \*\*S4: Prohibit Nominalization.\*\* Authors must convert nouns back into active verb forms to reduce word count and increase vigor (e.g., "analyze" instead of "perform an analysis"). \[Sources: UCR, Writing Principles\]
\*   \*\*S5: Mandatory Parallel Structure.\*\* Apply consistent grammatical form to all lists, comparisons, and series within a sentence. \[Sources: Writing Principles, SciWrite Demo 4\]

Once individual functional units are optimized, they must aggregate into larger logical architectures.

## 4. PARAGRAPH & SECTION ARCHITECTURE (P)
A paragraph must function as a single-themed container. Scientific manuscripts are engineered using the IMRAD "information sandwich" model: the Introduction and Discussion provide context and significance (the bread), while the Methods and Results provide the technical core (the filling).

\*   \*\*P1: Implement the C-C-C Framework.\*\* Every paragraph must follow the Context (Topic Sentence), Content (Evidence), and Conclusion (Take-home message) structure. \[Source: Writing Principles\]
\*   \*\*P2: Narrative Topic Sentences.\*\* Open every paragraph with a topic sentence that orients the reader to the "red thread" of the narrative. \[Sources: Nature Cancer, Writing Principles\]
\*   \*\*P3: Funnel Structure for Introductions.\*\* Organize the Introduction to move from the Big Picture (broad field) to a Narrowing Gap (prior art limitations) to a Specific Hypothesis. \[Source: IMRAD Guide\]
\*   \*\*P4: Flowing Prose for Abstracts.\*\* Abstracts must be written as a single, cohesive paragraph without labeled sections unless explicitly mandated by the journal's author guidelines. \[Sources: IMRAD Guide, Writing Process\]
\*   \*\*P5: Surgical Front-Loading.\*\* Place the most significant finding exclusively in the first paragraph of the Results and the first paragraph of the Discussion. \[Sources: SciWrite Demo 3, IMRAD Guide\]

Effective architecture provides the necessary framework for substantiating the claims within the document.

## 5. ARGUMENT & EVIDENCE (A)
A scientific document is a formal argument where every claim must be addressable to specific data. Authors must ensure that novel contributions are explicitly positioned and supported by rigorous evidence.

\*   \*\*A1: Explicit Statement of Novelty.\*\* State the main novel contribution—Idea, Theorem, Algorithm, or Tool—clearly in the Introduction. \[Source: Medvedev Rule 1\]
\*   \*\*A2: Introduction-Results Alignment.\*\* Support all claims made in the Introduction with corresponding evidence in the Results; avoid "bait and switch" arguments. \[Source: Medvedev Rule 5\]
\*   \*\*A3: Address Controversy Head-On.\*\* Do not omit conflicting findings; address field controversies or similar conclusions published elsewhere in the Introduction or Discussion. \[Source: Nature Cancer\]
\*   \*\*A4: Argument for Correctness.\*\* Provide a specific logical argument or proof for the correctness of any new algorithm or methodological step. \[Source: Medvedev Rule 9\]
\*   \*\*A5: State the "So What?".\*\* Explicitly define the strategic significance and broader implications of the findings in the Discussion. \[Source: IMRAD Guide\]

Claims of significance require the application of precise quantitative language to remain credible.

## 6. QUANTITATIVE LANGUAGE (Q)
Mathematical and statistical precision is fundamental to scientific integrity. Vague quantifiers undermine the objectivity of the record and prevent accurate expert interpretation.

\*   \*\*Q1: Replace Vague Quantifiers.\*\* Prohibit terms like "many," "recently," or "often." Replace with specific numerical values or timeframes. \[Source: Writing Principles\]
\*   \*\*Q2: Report Exact Statistics.\*\* Report exact \*p\*-values unless \*p\* < 0.001. Include Effect Sizes and Confidence Intervals for all primary outcomes. \[Source: IMRAD Guide\]
\*   \*\*Q3: Instrument Capability Matching.\*\* Match numerical precision strictly to the measurement capability of the instrument (e.g., do not report 4 decimal places if the tool only measures 1). \[Source: Writing Principles\]
\*   \*\*Q4: Computational Benchmarking.\*\* Report specific hardware configurations (CPU, RAM, Cores) when disclosing computational benchmarks. \[Source: Medvedev Rule 10\]
\*   \*\*Q5: Data Verification.\*\* Confirm that all numbers cited in the prose precisely match the data presented in Figures and Tables. \[Source: Writing Principles\]

Precise language is also required for the formal system of acknowledging prior research efforts.

## 7. CITATIONS & REFERENCES (C)
Citations must be used strategically to provide context without creating an exhaustive, irrelevant literature review.

\*   \*\*C1: Citation-Free Abstracts.\*\* Citations are prohibited in the Abstract. \[Source: IMRAD Guide\]
\*   \*\*C2: Prioritize Primary Research.\*\* Selectively cite primary research that directly supports the current work rather than citing every paper in the general field. \[Source: Nature Cancer\]
\*   \*\*C3: Citations as Procedural Proxies.\*\* Use citations in the Methods to point to standard procedures instead of re-describing established techniques. \[Source: Writing Principles\]
\*   \*\*C4: Cross-Reference Integrity.\*\* Every citation in the text must appear in the reference list and vice versa. \[Source: IMRAD Guide\]
\*   \*\*C5: Disclose Source Conflicts.\*\* Note conflicts between cited sources if they impact the interpretation of results. \[Source: Nature Cancer\]

Citations typically anchor the visual evidence provided in figures and tables.

## 8. FIGURES, TABLES, & LEGENDS (F)
Visual elements and legends must function as "standalone" units of information, conveying the study's message without reference to the main text.

\*   \*\*F1: Standalone Captions.\*\* Provide captions that define all abbreviations, statistical symbols, and error bars used within the figure. \[Sources: Writing Principles, IMRAD Guide\]
\*   \*\*F2: Strategic Element Selection.\*\* Use Figures for trends and patterns; use Tables for precise numerical values and demographic characteristics. \[Source: IMRAD Guide\]
\*   \*\*F3: Numerical Mention Order.\*\* Mention every Figure and Table in the text in chronological numerical order. \[Source: IMRAD Guide\]
\*   \*\*F4: Logic Visualization.\*\* For software or algorithms, include a workflow diagram or pseudocode in the main text. \[Sources: IMRAD Guide, Medvedev Rule 9\]
\*   \*\*F5: Explicit Sample Sizes.\*\* Report the sample size (n) for every experimental group within the figure legend. \[Source: IMRAD Guide\]

The impact of these visuals is maximized by the final linguistic polish of the prose.

## 9. WORD CHOICE & COMMON ERRORS (W)
Linguistic "friction" slows comprehension. Scientific writing requires precise, professional vocabulary to eliminate common pits of ambiguity.

\*   \*\*W1: Technical Use of "Significant".\*\* Use "significant" only when referring to statistical significance (\*p\* < 0.05). \[Source: Writing Principles\]
\*   \*\*W2: Affect vs. Effect.\*\* Use "Affect" as a verb (to influence) and "Effect" as a noun (the result). \[Source: Writing Principles\]
\*   \*\*W3: Fewer vs. Less.\*\* Use "Fewer" for countable items and "Less" for continuous quantities. \[Source: Writing Principles\]
\*   \*\*W4: The Abbreviation Rule.\*\* Abbreviate terms only if they appear four or more times; define them at the first occurrence. \[Source: Writing Principles\]
\*   \*\*W5: Mandatory Strong Verbs.\*\* Replace generic verbs ("obtained," "did") with strong, specific actions: "calcined," "sequenced," "titrated," "measured," "sliced," or "scooped." \[Sources: Sainani 4.4, SciWrite Demo 3\]

## 10. REVISION CHECKLIST (R)
The final verification process utilizes the diagnostic "Four Tests" to ensure the manuscript is ready for peer review.

\*   \*\*R1: The Elevator Pitch Test.\*\* Confirm the main finding is identifiable from the Title and Abstract alone. \[Source: Writing Principles\]
\*   \*\*R2: The Replication/Organic Standard.\*\* Verify that Methods are detailed enough to ensure exact replication of results. Ideally, methods should develop in an organic manner as experiments are conducted. \[Sources: IMRAD Guide, Nature Cancer\]
\*   \*\*R3: The Independence Test.\*\* Ensure every Figure and Table is understandable without referring to the main body text. \[Source: Writing Principles\]
\*   \*\*R4: The "So What?" Test.\*\* Verify that the Discussion answers both "So What?" (strategic significance) and "What Next?" (future directions). \[Source: IMRAD Guide, Writing Principles\]
\*   \*\*R5: Clutter Scan.\*\* Delete any word that does not add meaning or technical precision. Ensure every paragraph contains exactly one main idea. \[Sources: Sainani 4.4, SciWrite Demo 3, Writing Principles\]

## 11. CONFLICT NOTES
\*   \*\*Methods Placement Conflict:\*\* \*Nature Cancer\* suggests placing Methods in a supplement or separate editorial to maintain narrative flow. However, the \*\*IMRAD Structure Guide\*\* insists on Methods as a core part of the manuscript "sandwich." 
\*   \*\*Standard Selection:\*\* These standards adopt the \*\*IMRAD Structure Guide\*\* position as the mandatory default: Methods must remain in the main text to ensure immediate technical scrutiny and reproducibility. \[Sources: Nature Cancer, IMRAD Guide\]