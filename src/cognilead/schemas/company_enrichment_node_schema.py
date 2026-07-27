from pydantic import BaseModel, Field
from typing import Optional, Literal

class CompanyEnrichmentNodeSchema(BaseModel):
    enrichment_status: Literal["SUCCESS", "NOT_FOUND", "FAILED", "MISMATCH"] = Field(description=(
            "Status of the research: 'SUCCESS' if reliable company info was found AND its "
            "profile (size, industry) does not contradict the lead's own stated "
            "company_description. 'NOT_FOUND' if search returned no usable matches. 'FAILED' "
            "if search results were corrupted or unusable. 'MISMATCH' if a company was found "
            "but its profile (size, industry) substantially contradicts what the lead "
            "themselves stated — e.g. lead said '15-person HR firm' but the found company has "
            "200+ employees in an unrelated industry. In MISMATCH cases, still return the found "
            "data, but flag it so it is not treated as verified. Note: this field judges "
            "attribute consistency (size/industry) only — identity confidence in the company "
            "name itself is captured separately in name_match_confidence."))
    name_match_confidence: Literal["exact", "plausible_variant", "uncertain", "contradicted"] = Field(
        description=(
            "How confident you are that the enriched company is the SAME legal/business entity "
            "the lead referred to. This field evaluates identity only, independent of company "
            "attributes such as industry, size, funding, or target market.\n\n"

            "'exact' — The search identifies a single clear company whose official name or "
            "domain exactly matches the lead's company, allowing only trivial differences such "
            "as punctuation, legal suffixes (Inc., LLC, Ltd.), spacing, or well-known "
            "abbreviations.\n\n"

            "'plausible_variant' — There is exactly ONE credible candidate, and its name is a "
            "reasonable informal, shortened, expanded, or slightly rebranded version of the "
            "lead's stated company name (e.g. 'Stripe' → 'Stripe, Inc.'). There must not be "
            "multiple equally plausible companies competing for the same identity.\n\n"

            "'uncertain' — The search results do not provide enough evidence to confidently "
            "identify a single company. Use this when:\n"
            "- multiple plausible companies exist with similar or overlapping names,\n"
            "- the search returns conflicting candidates,\n"
            "- the lead's company name is generic or ambiguous,\n"
            "- the available evidence is insufficient to determine which company is correct.\n"
            "If you cannot confidently choose one company over another, return 'uncertain' "
            "instead of guessing. Never use 'plausible_variant' when multiple reasonable "
            "candidates exist.\n\n"

            "'contradicted' — The evidence clearly indicates that the enriched company is a "
            "different business. Examples include different branding with no plausible naming "
            "relationship, different official domains, or search results explicitly showing "
            "that the lead's stated company and the enriched company are separate entities.\n\n"

            "Decision Rules:\n"
            "1. Determine identity BEFORE considering industry, company size, funding, or any "
            "other business attributes.\n"
            "2. A strong attribute match (industry, size, services) does NOT prove identity.\n"
            "3. If multiple companies could reasonably match the lead's company name, return "
            "'uncertain' rather than selecting the one whose profile appears to fit best.\n"
            "4. 'plausible_variant' is reserved ONLY for situations where there is one clear "
            "candidate and the name difference is merely an informal, abbreviated, or expanded "
            "variation.\n"
            "5. If this field is 'uncertain' or 'contradicted', the company must not be treated "
            "as verified, even if its industry or size aligns perfectly with the lead's "
            "description. A profile match is not identity verification."
        )
    )
    company_name: Optional[str] = Field(default=None, description="Official name of the company.")
    website_domain: Optional[str] = Field(default=None, description="Official website or domain of the company. Primary domain URL.")
    industry: Optional[str] = Field(default=None, description="Primary business sector or domain (e.g., B2B FinTech, AI Infrastructure).")
    what_they_do: Optional[str] = Field(default=None, description="A clear 2-3 sentence summary of their main product/service and value proposition.")
    company_size_and_stage: Optional[str] = Field(default=None, description="Mention employee count, funding stage (e.g., Series A, Bootstrapped), or headcount range if stated in the results.")
    target_market: Optional[str] = Field(default=None, description="Who their primary customers are (e.g., Enterprise IT, SMBs, Developers).")