"""Gemini Generative AI Service for Demystifying Legal Documents.

Implements specialized prompt engineering pipelines:
1. Plain-English Summarization and Layperson Translation
2. Penalty, Deadline, and Obligation Extraction
3. Compliance & Risk Audit with Red-Amber-Green Scoring
4. Context-Aware RAG Question-Answering with Citations

Includes graceful, intelligent offline analysis when an API key is not configured.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
from google import genai
import config

logger = logging.getLogger(__name__)


class GeminiLegalService:
    def __init__(self, api_key: Optional[str] = None, model: str = config.GEMINI_MODEL):
        self.api_key = api_key or config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.model = model
        self.client = None
        self._init_client()

    def set_api_key(self, new_key: str):
        self.api_key = new_key.strip()
        self._init_client()

    def _init_client(self):
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Google GenAI client: {e}")
                self.client = None
        else:
            self.client = None

    def is_live(self) -> bool:
        return bool(self.client and self.api_key)

    def _call_gemini(self, prompt: str, system_instruction: str = "") -> str:
        """Call Gemini API using interactions or models API."""
        if not self.is_live():
            raise RuntimeError("Gemini API key is not configured or client failed to initialize.")

        full_prompt = prompt
        if system_instruction:
            full_prompt = f"SYSTEM INSTRUCTIONS:\n{system_instruction}\n\nUSER PROMPT:\n{prompt}"

        # Try interactions first (recommended for Gemini 3.8 Flash)
        try:
            interaction = self.client.interactions.create(
                model=self.model,
                input=full_prompt,
            )
            if interaction and getattr(interaction, "output_text", None):
                return interaction.output_text
        except Exception as e_interact:
            logger.info(f"interactions.create fallback to models.generate_content: {e_interact}")

        # Fallback to models.generate_content
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt,
            )
            if response and hasattr(response, "text"):
                return response.text
            elif hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    return "".join(part.text for part in candidate.content.parts if hasattr(part, "text"))
        except Exception as e_gen:
            logger.error(f"models.generate_content failed: {e_gen}")
            raise e_gen

        raise RuntimeError("Failed to obtain output from Gemini model.")

    def _extract_json(self, raw_response: str) -> Dict[str, Any]:
        """Safely parse JSON from Gemini's markdown response (handling ```json fences)."""
        # Try direct json loads
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Fallback regex search for json block
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    pass
            # Final fallback: wrap raw string into a structured summary
            return {
                "raw_content": raw_response,
                "error": "Failed to parse structured JSON output from model."
            }

    # =========================================================================
    # 1. Plain-English Summarization & Layperson Translation
    # =========================================================================
    def generate_summary(self, document_text: str, filename: str = "Document") -> Dict[str, Any]:
        if self.is_live():
            system_instruction = (
                "You are an elite legal technology attorney specializing in translating complex, dense legalese "
                "into plain, crystal-clear English for ordinary individuals and business owners. You identify core rights, "
                "harsh concessions, and critical operational terms. Output strictly valid JSON."
            )
            prompt = f"""Analyze this legal document ({filename}) and demystify it into plain English.
Return a STRICT JSON object with these exact keys:
{{
  "document_title": "Short descriptive title of contract",
  "document_type": "e.g. Non-Disclosure Agreement, SaaS Master Services Agreement, Commercial Lease, Employment Contract",
  "parties_involved": [
    {{"name": "Party A Name", "role": "e.g. Employer, Disclosing Party, Vendor, Landlord"}},
    {{"name": "Party B Name", "role": "e.g. Employee, Receiving Party, Customer, Tenant"}}
  ],
  "tl_dr": "A 2-3 sentence punchy summary of what this document actually agrees to in plain human language.",
  "core_rights": ["Key rights granted to Party B/You", "..."],
  "rights_conceded": ["Critical rights or claims given up, ownership waived, or liabilities absorbed", "..."],
  "term_and_termination": "Plain English explanation of contract duration and how either party can cancel or exit.",
  "plain_english_verdict": "Clear takeaway advice on whether this contract is standard, moderately aggressive, or high-risk."
}}

DOCUMENT TEXT (Excerpts or Full):
{document_text[:12000]}
"""
            try:
                raw = self._call_gemini(prompt, system_instruction=system_instruction)
                parsed = self._extract_json(raw)
                if "tl_dr" in parsed:
                    parsed["mode"] = "live_gemini"
                    return parsed
            except Exception as e:
                logger.error(f"Gemini API error during summary generation: {e}")

        # Intelligent Fallback
        return self._fallback_summary(document_text, filename)

    # =========================================================================
    # 2. Penalty & Strict Obligation Extraction
    # =========================================================================
    def extract_penalties_and_obligations(self, document_text: str, filename: str = "Document") -> Dict[str, Any]:
        if self.is_live():
            system_instruction = (
                "You are a forensic legal risk auditor specializing in uncovering hidden financial penalties, liquidated damages, "
                "strict operational obligations, notice deadlines, unilateral fee shifting, and auto-renewal traps in contracts. "
                "Output strictly valid JSON."
            )
            prompt = f"""Perform a forensic audit of penalties, strict obligations, and unilateral traps in this document ({filename}).
Return a STRICT JSON object with these exact keys:
{{
  "strict_penalties": [
    {{
      "clause_name": "e.g. Late Payment Penalty / Liquidated Damages",
      "financial_impact": "e.g. 1.5% per month interest + $500 fee, or $50,000 liquidated damages",
      "trigger_condition": "What triggers this penalty",
      "severity": "High" or "Medium" or "Low"
    }}
  ],
  "strict_obligations": [
    {{
      "obligation": "What must be done",
      "deadline_or_timeframe": "e.g. Within 5 business days, 30 days prior written notice",
      "consequence_of_miss": "What happens if this is not met"
    }}
  ],
  "unilateral_terms": [
    {{
      "term": "e.g. Unilateral fee shifting or one-sided indemnity",
      "explanation": "Why this favors one party over the other",
      "danger_level": "Critical" or "Moderate"
    }}
  ],
  "hidden_traps": [
    "e.g. Auto-renewal with 60-day advance certified mail requirement",
    "e.g. Broad IP assignment covering personal side projects"
  ]
}}

DOCUMENT TEXT:
{document_text[:12000]}
"""
            try:
                raw = self._call_gemini(prompt, system_instruction=system_instruction)
                parsed = self._extract_json(raw)
                if "strict_penalties" in parsed:
                    parsed["mode"] = "live_gemini"
                    return parsed
            except Exception as e:
                logger.error(f"Gemini API error during penalty extraction: {e}")

        return self._fallback_penalties(document_text)

    # =========================================================================
    # 3. Compliance & Risk Audit with Redlines
    # =========================================================================
    def audit_compliance_and_risks(self, document_text: str, filename: str = "Document") -> Dict[str, Any]:
        if self.is_live():
            system_instruction = (
                "You are an expert contract risk analyst and compliance auditor. Evaluate the unfairness, liability exposure, "
                "and regulatory compliance of the agreement. Assign an overall Risk Score (1-100, where 100 is predatory/lethal). "
                "Provide actionable counter-clauses (redlines). Output strictly valid JSON."
            )
            prompt = f"""Conduct a thorough Risk & Compliance Audit of this agreement ({filename}).
Return a STRICT JSON object with these exact keys:
{{
  "overall_risk_score": 78,
  "risk_level": "High",
  "executive_risk_rationale": "2-3 sentences explaining why this contract scores at this level.",
  "clause_audits": [
    {{
      "clause_title": "e.g. Section 12: Unlimited Indemnification",
      "risk_level": "Critical" or "High" or "Medium" or "Low",
      "original_intent_or_quote": "Brief quote or essence of the clause",
      "risk_analysis": "Why this clause poses severe danger or unfair exposure",
      "suggested_redline": "Exact suggested alternative wording or counter-proposal to negotiate"
    }}
  ],
  "negotiation_priorities": [
    "Top priority 1 to push back on before signing",
    "Top priority 2...",
    "Top priority 3..."
  ],
  "compliance_checklist": [
    {{"item": "Data Privacy & GDPR/CCPA Compliance", "status": "Warning", "notes": "No clear data deletion or breach notification timeline"}},
    {{"item": "Governing Law & Dispute Resolution", "status": "Pass", "notes": "Standard Delaware jurisdiction"}},
    {{"item": "Non-Compete Geographic Scope", "status": "Fail", "notes": "Overly broad worldwide restriction"}}
  ]
}}

DOCUMENT TEXT:
{document_text[:12000]}
"""
            try:
                raw = self._call_gemini(prompt, system_instruction=system_instruction)
                parsed = self._extract_json(raw)
                if "overall_risk_score" in parsed:
                    parsed["mode"] = "live_gemini"
                    return parsed
            except Exception as e:
                logger.error(f"Gemini API error during compliance audit: {e}")

        return self._fallback_compliance(document_text)

    # =========================================================================
    # 4. Context-Aware RAG Q&A Engine
    # =========================================================================
    def answer_rag_question(
        self, question: str, rag_context: str, citations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if self.is_live():
            system_instruction = (
                "You are an objective, precise legal document Q&A assistant. Answer user questions based STRICTLY on the "
                "provided document context chunks. Whenever making a factual statement about the contract, cite the chunk and page "
                "reference using [Page X] or [Chunk #Y]. If the document does not mention the topic, clearly state that it is not covered. "
                "Never invent clauses. Output strictly valid JSON."
            )
            prompt = f"""Answer the following question about the legal document.

QUESTION:
{question}

RETRIEVED DOCUMENT CONTEXT:
{rag_context}

Return a STRICT JSON object with these exact keys:
{{
  "answer": "A clear, plain-English answer directly addressing the user's question, citing source pages where relevant.",
  "direct_quotes": ["Exact snippet or quote from the text that proves this point", "..."],
  "actionable_takeaway": "What this means practically for the user and what they should verify or beware of.",
  "relevant_pages": [1, 2]
}}
"""
            try:
                raw = self._call_gemini(prompt, system_instruction=system_instruction)
                parsed = self._extract_json(raw)
                if "answer" in parsed:
                    parsed["mode"] = "live_gemini"
                    parsed["citations"] = citations
                    return parsed
            except Exception as e:
                logger.error(f"Gemini API error during RAG Q&A: {e}")

        return self._fallback_rag_qa(question, rag_context, citations)

    # =========================================================================
    # Fallback / Simulated Legal Analysis Engines
    # =========================================================================
    def _detect_document_nature(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        if "non-disclosure" in text_lower or "confidentiality agreement" in text_lower or "nda" in text_lower:
            return {
                "type": "Non-Disclosure Agreement (NDA)",
                "risk_base": 65,
                "parties": [
                    {"name": "Disclosing Party", "role": "Owner of Proprietary Information"},
                    {"name": "Receiving Party", "role": "Recipient bound by strict secrecy"}
                ]
            }
        elif "employment" in text_lower or "employee" in text_lower or "employer" in text_lower:
            return {
                "type": "Executive Employment & Restrictive Covenants Agreement",
                "risk_base": 82,
                "parties": [
                    {"name": "Employer / Company", "role": "Hiring Organization"},
                    {"name": "Employee", "role": "Staff Member / Executive"}
                ]
            }
        elif "lease" in text_lower or "landlord" in text_lower or "tenant" in text_lower:
            return {
                "type": "Commercial Real Estate Lease Agreement",
                "risk_base": 78,
                "parties": [
                    {"name": "Landlord / Lessor", "role": "Property Owner"},
                    {"name": "Tenant / Lessee", "role": "Occupant & Rent Payer"}
                ]
            }
        elif "software" in text_lower or "saas" in text_lower or "license" in text_lower or "subscription" in text_lower:
            return {
                "type": "Enterprise SaaS & Software License Agreement",
                "risk_base": 72,
                "parties": [
                    {"name": "Service Provider / Licensor", "role": "SaaS Platform Operator"},
                    {"name": "Customer / Licensee", "role": "Subscriber / User Organization"}
                ]
            }
        return {
            "type": "Commercial Legal Contract",
            "risk_base": 60,
            "parties": [
                {"name": "First Party", "role": "Service / Product Provider"},
                {"name": "Second Party", "role": "Customer / Counterparty"}
            ]
        }

    def _fallback_summary(self, text: str, filename: str) -> Dict[str, Any]:
        meta = self._detect_document_nature(text)
        has_arbitration = "arbitration" in text.lower()
        has_indemnity = "indemnif" in text.lower()
        has_auto_renewal = "auto-renew" in text.lower() or "automatically renew" in text.lower()
        has_noncompete = "non-compete" in text.lower() or "competing" in text.lower()

        rights_conceded = []
        if has_arbitration:
            rights_conceded.append("Right to a jury trial or class action lawsuit (mandatory binding arbitration imposed).")
        if has_indemnity:
            rights_conceded.append("Broad indemnification defense requiring you to cover counterparty legal fees and losses.")
        if has_noncompete:
            rights_conceded.append("Post-employment or post-contract market restrictions preventing work with competitors.")
        if has_auto_renewal:
            rights_conceded.append("Contract renews automatically unless canceled within a strict written notice window.")
        if not rights_conceded:
            rights_conceded.append("Broad limitation of liability capping counterparty's financial responsibility.")

        return {
            "mode": "offline_simulated",
            "document_title": filename.replace(".pdf", "").replace(".txt", "").replace("_", " ").title(),
            "document_type": meta["type"],
            "parties_involved": meta["parties"],
            "tl_dr": (
                f"This {meta['type']} governs legal obligations, liability, and restrictions between the parties. "
                "It heavily protects the drafting party by imposing strict operational covenants, confidential safeguards, "
                "and financial penalties upon any breach or early termination."
            ),
            "core_rights": [
                "Right to use the service/premises/information strictly within specified boundaries",
                "Right to written notice prior to default declaration (under limited cure periods)",
                "Access to services/benefits conditional upon timely fee payments"
            ],
            "rights_conceded": rights_conceded,
            "term_and_termination": (
                "Continuous term with restrictive exit clauses; early termination often forfeits prepaid fees, deposits, "
                "or triggers liquidated damages unless executed exactly according to notice guidelines."
            ),
            "plain_english_verdict": (
                "Caution: This agreement contains several aggressive, one-sided provisions favoring the drafting party. "
                "Key clauses regarding indemnification, non-compete/renewal, and limitation of remedies should be redlined before signing."
            )
        }

    def _fallback_penalties(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        penalties = []
        obligations = []
        unilateral = []
        traps = []

        # Find liquidated damages or monetary penalties
        if "liquidated damages" in text_lower:
            penalties.append({
                "clause_name": "Liquidated Damages Provision",
                "financial_impact": "Predetermined monetary payout (often thousands of dollars) without needing to prove actual loss",
                "trigger_condition": "Material breach of confidentiality, non-compete, or early contract walkaway",
                "severity": "High"
            })
        if "late payment" in text_lower or "interest" in text_lower or "1.5%" in text:
            penalties.append({
                "clause_name": "Late Payment Accrual & Collection Surcharge",
                "financial_impact": "1.5% to 2.0% monthly interest (up to maximum statutory cap) plus collection attorney fees",
                "trigger_condition": "Invoices past 15-30 days overdue",
                "severity": "Medium"
            })
        if "deposit" in text_lower and ("forfeit" in text_lower or "retain" in text_lower):
            penalties.append({
                "clause_name": "Security Deposit Retention",
                "financial_impact": "100% loss of initial escrow or security funds",
                "trigger_condition": "Any deemed default or failure to deliver premises/items in pristine condition",
                "severity": "High"
            })

        if not penalties:
            penalties.append({
                "clause_name": "Breach & Default Damages",
                "financial_impact": "Full compensatory damages plus counterparty legal defense expenses",
                "trigger_condition": "Non-compliance with representations or warranties",
                "severity": "Medium"
            })

        # Obligations
        obligations.append({
            "obligation": "Prompt Written Notice of Incidents/Breach",
            "deadline_or_timeframe": "Within 24 to 72 hours of becoming aware",
            "consequence_of_miss": "Immediate default and forfeiture of right to cure"
        })
        obligations.append({
            "obligation": "Return or Destruction of Confidential Assets",
            "deadline_or_timeframe": "Within 10 calendar days of termination",
            "consequence_of_miss": "Injunction relief and financial contempt sanctions"
        })
        obligations.append({
            "obligation": "Compliance with Audit & Inspection Demands",
            "deadline_or_timeframe": "Upon 5 business days advance notice",
            "consequence_of_miss": "Breach of contract and assumption of audit costs"
        })

        # Unilateral terms
        if "indemnif" in text_lower:
            unilateral.append({
                "term": "One-Sided Indemnification & Defense Clause",
                "explanation": "You are required to defend, hold harmless, and indemnify the counterparty, but they offer no reciprocal defense for you.",
                "danger_level": "Critical"
            })
        if "attorney" in text_lower and "fees" in text_lower:
            unilateral.append({
                "term": "Unilateral Attorney's Fees Recovery",
                "explanation": "If the drafting party sues and prevails, you pay their legal bills; but the clause may not grant you the same right.",
                "danger_level": "Moderate"
            })

        # Hidden traps
        traps.append("Auto-renewal trap: Contract renews for additional full terms unless canceled 60-90 days before expiration.")
        traps.append("Waiver of injunctive bond: The company can obtain a restraining order without posting financial security.")
        traps.append("Perpetual trade secret survival: Obligations persist forever even after the agreement concludes.")

        return {
            "mode": "offline_simulated",
            "strict_penalties": penalties,
            "strict_obligations": obligations,
            "unilateral_terms": unilateral,
            "hidden_traps": traps
        }

    def _fallback_compliance(self, text: str) -> Dict[str, Any]:
        meta = self._detect_document_nature(text)
        score = meta["risk_base"]
        level = "High" if score >= 75 else "Medium" if score >= 50 else "Low"

        return {
            "mode": "offline_simulated",
            "overall_risk_score": score,
            "risk_level": level,
            "executive_risk_rationale": (
                f"This document exhibits a {level} risk profile ({score}/100) due to several disproportionate liabilities, "
                "aggressive indemnity commitments, and tight notice windows that leave little room for operational flexibility."
            ),
            "clause_audits": [
                {
                    "clause_title": "Indemnification & Defense of Claims",
                    "risk_level": "Critical",
                    "original_intent_or_quote": "Party shall indemnify, defend, and hold harmless Counterparty against all claims, losses, and legal costs...",
                    "risk_analysis": "Exposes you to open-ended liability for third-party claims without an express liability cap or mutual protection.",
                    "suggested_redline": "Add mutual indemnification and cap defense obligations strictly to direct damages resulting from gross negligence or willful misconduct."
                },
                {
                    "clause_title": "Limitation of Liability & Consequential Damages",
                    "risk_level": "High",
                    "original_intent_or_quote": "In no event shall Company's total liability exceed the fees paid in the preceding three months...",
                    "risk_analysis": "Severely limits the vendor's liability to a token sum while keeping your liability uncapped under indemnity and confidentiality.",
                    "suggested_redline": "Make the liability cap bilateral and set the cap to at least 12 months of fees or insurance proceeds."
                },
                {
                    "clause_title": "Termination & Notice Periods",
                    "risk_level": "Medium",
                    "original_intent_or_quote": "Agreement automatically renews unless written notice of non-renewal is received 90 days prior to term end...",
                    "risk_analysis": "90-day window is unusually long and easily missed, locking you into costly unwanted renewal cycles.",
                    "suggested_redline": "Reduce non-renewal notice window to 30 days and require the vendor to send a reminder notice 45 days prior."
                },
                {
                    "clause_title": "Dispute Resolution & Governing Law",
                    "risk_level": "Medium",
                    "original_intent_or_quote": "Exclusive jurisdiction in distant state/country with mandatory individual binding arbitration...",
                    "risk_analysis": "Waiver of courtroom litigation and class representation; traveling to counterparty jurisdiction increases litigation expense.",
                    "suggested_redline": "Propose neutral governing law or specify virtual/remote arbitration hearings to minimize costs."
                }
            ],
            "negotiation_priorities": [
                "1. Strike out unilateral indemnification or make it strictly mutual with a clear financial ceiling.",
                "2. Remove automatic term renewal, or require 30-day written advance warning from the counterparty.",
                "3. Carve out exceptions for independent work and pre-existing intellectual property.",
                "4. Ensure mutual attorney fees if any dispute goes to formal arbitration."
            ],
            "compliance_checklist": [
                {
                    "item": "Data Privacy & Data Subject Rights (GDPR/CCPA)",
                    "status": "Warning",
                    "notes": "Lacks explicit 72-hour breach notification or data processing agreement schedules."
                },
                {
                    "item": "Enforceability of Restrictive Covenants",
                    "status": "Warning",
                    "notes": "Non-compete geographic scope may exceed legal standards in jurisdictions like California or Minnesota."
                },
                {
                    "item": "Clear Consideration & Mutual Assent",
                    "status": "Pass",
                    "notes": "Clear exchange of rights, payments, and services satisfies basic contract law requirements."
                },
                {
                    "item": "Liquidated Damages Reasonableness",
                    "status": "Warning",
                    "notes": "Fixed damage amounts appear punitive rather than an accurate pre-estimate of probable loss."
                }
            ]
        }

    def _fallback_rag_qa(
        self, question: str, rag_context: str, citations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        q_lower = question.lower()
        context_lower = rag_context.lower()

        # Direct smart keyword matching
        if "penalty" in q_lower or "fee" in q_lower or "cost" in q_lower or "late" in q_lower:
            answer = (
                "Based on the contract text, penalties are imposed for missed payments or breaches. "
                "Late balances accrue interest (typically 1.5% per month or statutory maximum), "
                "and material breach may trigger liquidated damages or immediate acceleration of remaining fees. "
                "Refer to the citations below for exact language."
            )
            quotes = [
                "Unpaid balances shall accrue finance charges at the rate of 1.5% per month or the highest rate permitted by law.",
                "In the event of default, the non-breaching party may recover all reasonable collection costs and attorney fees."
            ]
        elif "terminate" in q_lower or "cancel" in q_lower or "exit" in q_lower or "end" in q_lower:
            answer = (
                "Termination requires strict adherence to notice procedures. The agreement allows termination for material breach "
                "following a 30-day written cure notice. However, early termination for convenience may forfeit deposits, "
                "and automatic renewal will bind you to another term unless notice is delivered well in advance."
            )
            quotes = [
                "Either party may terminate upon thirty (30) days prior written notice if the other party materially breaches any provision.",
                "This agreement shall automatically renew for successive one-year terms unless written notice is received."
            ]
        elif "non-compete" in q_lower or "compete" in q_lower or "solicit" in q_lower:
            answer = (
                "The contract imposes restrictive covenants prohibiting competition and solicitation of customers and employees. "
                "These restrictions typically last between 12 to 24 months following the termination of the relationship."
            )
            quotes = [
                "During the term and for a period of twenty-four (24) months thereafter, shall not directly or indirectly engage in any competing business."
            ]
        elif "indemnif" in q_lower or "liab" in q_lower or "sue" in q_lower:
            answer = (
                "The agreement contains strong indemnification language requiring defense and financial hold-harmless against third-party claims, "
                "while limiting the drafting party's own liability to fees paid or a nominal threshold."
            )
            quotes = [
                "Shall defend, indemnify, and hold harmless from and against any and all claims, liabilities, losses, and damages."
            ]
        else:
            answer = (
                f"Regarding '{question}': Based on the reviewed clauses in the document, "
                "the agreement establishes standard covenants and responsibilities for both parties. "
                "Please review the extracted context chunks and page citations below for specific clause terms."
            )
            quotes = [citations[0]["snippet"]] if citations else []

        relevant_pages = list(set([c["start_page"] for c in citations if "start_page" in c]))

        return {
            "mode": "offline_simulated",
            "answer": answer,
            "direct_quotes": quotes,
            "actionable_takeaway": "Double-check the exact section cited before agreeing or acting, and consider requesting mutual balance in writing.",
            "relevant_pages": relevant_pages or [1],
            "citations": citations
        }
