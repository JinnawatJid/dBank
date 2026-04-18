# NotebookLM Interview Preparation Guide

Google's **NotebookLM** operates differently than standard AI generators (like Gamma or ChatGPT). It acts as a hyper-intelligent research assistant grounded *only* in the documents you upload.

Here is exactly how to use it to prepare for your CTO-level technical interview.

---

### Step 1: Create Your Notebook & Upload Sources
1. Go to [NotebookLM](https://notebooklm.google.com/).
2. Create a new Notebook called "dBank Technical Interview".
3. **Upload these specific files from your repository:**
   * `docs/interview_prep/architecture_breakdown.md`
   * `docs/interview_prep/presentation_script.md`
   * `docs/interview_prep/expected_qa.md`
   * `docs/interview_prep/presentation_slides_breakdown.md`
   * *(Optional: The `README.md` and `docs/architecture/ARCHITECTURE.md`)*

---

### Step 2: Prompts for Synthesis and Practice

Once your sources are loaded, use the chat box to run these specific prompts depending on what you want to achieve:

#### Prompt 1: Generate Deep-Dive Speaker Notes
> "Act as an expert technical communications coach. I am presenting this system to a CTO. Based on the uploaded 'presentation_slides_breakdown.md' and 'presentation_script.md', create a set of highly detailed, bulleted speaker notes for each slide. Focus heavily on explaining the 'Reversible PII Masking' and the 'Defense in Depth SQL Execution' clearly and concisely. Highlight where I should pause or emphasize certain points."

#### Prompt 2: The "Mock Interview" / Grilling
> "I am Jinnawat Jidsanoa, interviewing for the Mission Engineer role. Act as a highly technical, slightly skeptical CTO. Based on the uploaded 'expected_qa.md' and architecture documents, ask me the single hardest, most complex question you can think of regarding my choice of pgvector versus a dedicated vector database, or the security of the LLM executing SQL. Ask the question and wait for my response before giving feedback."

#### Prompt 3: Technical Gap Analysis
> "Review all the uploaded documentation regarding the dBank architecture. Are there any obvious security flaws, scalability bottlenecks, or architectural weaknesses that a CTO might spot that are NOT currently addressed in the 'expected_qa.md' document? Please list them out along with a suggested defensible answer for each."

---

### Step 3: The "Audio Overview" (Highly Recommended)
NotebookLM has a feature that generates an AI podcast (Audio Overview) discussing your sources.
1. In the Notebook Guide (the panel on the right or top), click **"Generate"** under Audio Overview.
2. Listen to this 5-10 minute generated audio on your commute or before the interview. It is an incredible way to hear two AI hosts naturally discuss the complex topics of your architecture (like PII masking and agentic tools), helping you internalize the talking points naturally.