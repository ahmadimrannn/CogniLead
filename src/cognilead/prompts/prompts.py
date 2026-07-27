# Lead Extractor Prompt
def lead_extractor_prompt(data):
  prompt = f"""You are a senior B2B Lead Intelligence Extractor. Analyze the following inbound text and extract structured lead information.
  
    ### Rules:
    1. Strict Grounding: Extract ONLY facts explicitly stated in the text. Do NOT invent, assume, or extrapolate data.
    2. Missing Information: If a field is not directly mentioned, leave it empty/null. Never use filler placeholders like "N/A", "Unknown", or "Not provided".
    3. Role Inference: Infer decision-making authority from context, not just explicit titles. Phrases like "I run", "I founded", "my company", "we built" indicate ownership/founder-level authority even without a stated title. Only leave role null if there is truly no ownership or positional signal at all.
    4. Company Name vs Description: If a proper company name is stated, extract it as company_name. If the text describes the company without naming it (e.g. "a 40-person fintech", "a small consulting shop"), extract that description into company_description instead of leaving both fields null. Only leave both null if the text gives no company information whatsoever.
    5. Stated Need: Summarize their primary request, goal, or problem into a concise, action-oriented statement.
  
    ### Inbound Text to Extract From:
    {data}
  
    Extract and map the lead details (name, role, company_name, company_description, stated_need) from the text above."""

  return prompt


# Lead Scorer Prompt 
def lead_scorer_prompt(extracted_lead, extracted_company_data):
  prompt = f"""You are an expert B2B Lead Qualification and Ideal Customer Profile (ICP) Specialist. Analyze the extracted lead details alongside the enriched company research, assign a composite qualification score from 1 to 10, and provide a clear justification.
  
    ### Evaluation Criteria:
  
    1. **Decision-Maker Authority (Lead Signal)**:
      - **High**: Executive, ownership, or budget-holding roles (e.g., Founder, CEO, Head of Operations, Director, VP, Tech Lead).
      - **Low**: Non-decision makers (e.g., student, intern, individual contributor, job seeker) or missing role information.
  
    2. **Company Quality & ICP Fit (Enriched Research Signal)**:
      - **High**: `enrichment_status` is "SUCCESS" AND `name_match_confidence` is "exact" or "plausible_variant", with healthy indicators (e.g., 10+ employees, funded/Series A+, established revenue, B2B operational complexity).
      - **Medium**: `enrichment_status` is "SUCCESS" but early-stage/small business, OR `enrichment_status` is "NOT_FOUND"/"FAILED" — treat unverified company data as neutral, not negative, since a real business (especially a very new one) can legitimately have little to no findable web presence.
      - **Low**: `enrichment_status` is "MISMATCH", OR `name_match_confidence` is "uncertain"/"contradicted" regardless of what `enrichment_status` says — treat this as a red flag on data reliability, not a positive. Do NOT use any of the found company's size/industry/headcount facts as if they describe the lead's actual company in these cases. Base company judgment ONLY on what the lead themselves stated in company_description, and explicitly note in your reasoning that the enrichment result was disregarded and why (mismatch, or uncertain/contradicted identity).
  
    3. **Stated Need & Buying Intent (Lead Signal)**:
      - **High**: Specific, actionable problems requiring a solution (e.g., asking for a demo, onboarding automation, pricing, immediate timeline "this week").
      - **Low**: Generic inquiries, vague statements, or irrelevant requests.
  
    ### Scoring Matrix:
    - **8–10 (High Quality / Tier 1)**: Strong decision-maker + verified ICP company (growth stage / funded / solid headcount, status SUCCESS with exact/plausible_variant name match) + actionable, high-intent need.
    - **5–7 (Medium Quality / Tier 2)**: Moderate fit or partial information (e.g., strong need and role, but company is early-stage/unverified/NOT_FOUND; OR high-profile verified company, but vague role/need).
    - **1–4 (Low Quality / Disqualified)**: Non-business lead (student, intern), vague/non-existent buying need, or company data status is MISMATCH / name_match_confidence is uncertain-or-contradicted with no other strong signals to compensate.
  
    ### Explicitly Ignore:
    - Grammar, spelling, capitalization, and message formality. A messy, lowercase message stating solid facts must score identically to a polished email.
  
    ---
  
    ### Input Data for Evaluation:
  
    **1. Extracted Lead Information:**
    {extracted_lead}
  
    **2. Enriched Company Research:**
    {extracted_company_data}
  
    ---
  
    Evaluate both the lead and company data above. Assign an integer score (1–10) and write a concise 1–2 sentence explanation justifying the score based on ICP fit, authority, and intent. If `enrichment_status` is "MISMATCH" OR `name_match_confidence` is "uncertain"/"contradicted", your reasoning MUST explicitly state that the enrichment data was disregarded and why."""

  return prompt

# Company Enrichment Node Prompt 
def company_enrichment_node_prompt(company_name, company_description, search_results):
  prompt = f"""You are an expert Corporate Intelligence Research Analyst. Synthesize the provided search results to create a clean, factual summary profile for the target company.
  
    ### Inputs:
    Target Company Name (as stated by lead): {company_name}
    Target Company Description (as stated by lead): {company_description}
  
    Search Results:
    \"\"\"
    {search_results}
    \"\"\"
  
    ### Step 1 — Determine `name_match_confidence` FIRST, independently of company attributes:
    Ask only: "is the company in these search results plausibly the same entity the lead named?"
    - **"exact"**: same name, or trivial variation (Inc/LLC, punctuation, obvious abbreviation).
    - **"plausible_variant"**: the found name is a reasonable informal, shortened, or fuller
      version of what the lead said (e.g. lead said "Meridian Solutions", found company is
      "Meridian HR Consulting" — people commonly shorten or genericize their employer's name in
      casual speech; this counts as plausible, not a mismatch).
    - **"uncertain"**: the name is generic/common enough that this could easily be a different,
      unrelated company that happens to share it, and you have no other signal to break the tie.
    - **"contradicted"**: clear evidence this is a distinct, different company with no plausible
      naming link to what the lead said.
  
    ### Step 2 — Determine `enrichment_status`, using BOTH name_match_confidence AND attribute consistency:
    1. **"SUCCESS"**:
      - `name_match_confidence` is "exact" or "plausible_variant", AND
      - the found company's profile (size, industry, what it does) does not substantially
        contradict the lead's own stated company_description.
      - You MUST fill out `company_name` and `what_they_do` along with any other available fields.
  
    2. **"MISMATCH"**:
      - `name_match_confidence` is "uncertain" or "contradicted", OR
      - the name is a plausible match but size/industry substantially contradict the lead's
        description (e.g. lead said "15-person HR firm", found company has 200+ employees in an
        unrelated industry like IT consulting).
      - Still fill out the fields with what was found, but this status tells downstream consumers
        NOT to treat it as verified data about the lead's actual company.
      - In `what_they_do`, briefly note the specific contradiction that triggered this status.
  
    3. **"NOT_FOUND"**:
      - Search results are empty, irrelevant, or return nothing plausibly connected to the target.
      - Leave remaining fields as `null` (never invent, never use filler like "N/A").
  
    4. **"FAILED"**:
      - The search output is broken, corrupted text, or unreadable error messages.
      - Leave remaining fields as `null`.
  
    ### Instructions & Rules:
    1. **Strict Grounding**: Rely ONLY on facts directly stated in the search results above. Do NOT invent, assume, or extrapolate details (e.g., do not guess company size or revenue if it isn't explicitly mentioned).
    2. **Missing Information**: If a specific detail (like company size or funding) is not mentioned in the search results, explicitly set that field to null. Never write filler like "N/A", "Unknown", or "Not provided".
    3. **Synthesis & Clarity**: Distill noisy search snippets into concise, professional business facts. Avoid copy-pasting raw search snippets directly.
    4. **Order matters**: always decide `name_match_confidence` before `enrichment_status` — do not let a confident, well-documented company profile talk you into "exact"/"plausible_variant" if the name itself doesn't reasonably support it. A well-written profile of the wrong company is still the wrong company.
  
    ### Data to Extract:
    - **Company Name**: Official full name of the company.
    - **Website/Domain**: Primary domain URL if present in the results.
    - **Industry/Sector**: Primary business sector or domain (e.g., B2B FinTech, AI Infrastructure).
    - **What They Do**: A clear 2-3 sentence summary of their main product/service and value proposition.
    - **Company Size & Stage**: Mention employee count, funding stage (e.g., Series A, Bootstrapped), or headcount range if stated in the results.
    - **Target Market**: Who their primary customers are (e.g., Enterprise IT, SMBs, Developers).
  
    Extract and summarize the company facts according to these instructions."""

  return prompt