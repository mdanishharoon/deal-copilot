"""
Risk Scanner Agent
Identifies and prioritizes material risks and anomalies across public and private research
Uses OpenAI for analysis - outputs source-cited flags with validated evidence
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from openai import OpenAI
from deal_copilot.config import config_openai as config


class RiskScannerAgent:
    """
    Agent that identifies and prioritizes material risks and anomalies
    
    Inputs:
    - Deep Research report (public intel)
    - Data Room report (private intel)
    
    Outputs:
    - Top 5 validated risks with mitigants
    - Open questions / DD checklist
    """
    
    def __init__(self, progress_callback=None):
        """
        Initialize the Risk Scanner Agent with OpenAI
        
        Args:
            progress_callback: Optional function to call with progress updates
        """
        self.progress_callback = progress_callback
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL
    
    def _update_progress(self, step: str, progress: int, message: str):
        """Update progress if callback is provided"""
        if self.progress_callback:
            self.progress_callback(step, progress, message)
        print(f"  [{progress}%] {step}: {message}")
    
    def scan_risks(
        self,
        company_name: str,
        deep_research_report: Optional[Dict] = None,
        data_room_report: Optional[Dict] = None
    ) -> Dict:
        """
        Scan for risks across all available intelligence
        
        Args:
            company_name: Name of the company
            deep_research_report: Output from Deep Research Agent
            data_room_report: Output from Data Room Agent
            
        Returns:
            Dictionary with validated risks and open questions
        """
        print(f"\n{'='*60}")
        print(f"RISK SCANNER AGENT")
        print(f"{'='*60}")
        print(f"Company: {company_name}")
        print(f"{'='*60}\n")
        
        self._update_progress("risk_scan", 10, "Preparing context from all sources...")
        
        # Prepare context from all sources
        context = self._prepare_context(
            company_name,
            deep_research_report,
            data_room_report
        )
        
        self._update_progress("risk_scan", 30, "Analyzing for quantitative anomalies...")
        
        # Generate risk analysis
        risk_analysis = self._analyze_risks(company_name, context)
        
        self._update_progress("risk_scan", 80, "Validating risks and generating DD checklist...")
        
        return {
            "company_name": company_name,
            "generated_at": datetime.now().isoformat(),
            "risk_analysis": risk_analysis,
            "sources_analyzed": {
                "deep_research": deep_research_report is not None,
                "data_room": data_room_report is not None
            }
        }
    
    def _prepare_context(
        self,
        company_name: str,
        deep_research: Optional[Dict],
        data_room: Optional[Dict]
    ) -> str:
        """Prepare context from all intelligence sources"""
        
        context_parts = []
        
        context_parts.append(f"Company: {company_name}\n")
        context_parts.append("="*60 + "\n")
        
        # Add Deep Research (public intel)
        if deep_research and "sections" in deep_research:
            context_parts.append("\n## PUBLIC INTELLIGENCE (Deep Research)\n")
            for section in deep_research["sections"]:
                context_parts.append(f"\n### {section.get('title', 'Section')}\n")
                content = section.get('content', '')
                # Strip HTML tags for cleaner analysis
                import re
                clean_content = re.sub('<[^<]+?>', '', content)
                context_parts.append(clean_content[:10000])  # Limit per section
        
        # Add Data Room (private intel)
        if data_room:
            context_parts.append("\n\n## PRIVATE INTELLIGENCE (Data Room)\n")
            
            # Qualitative analysis
            if "qualitative_analysis" in data_room:
                context_parts.append("\n### Qualitative Analysis\n")
                qual_content = data_room["qualitative_analysis"].get("content", "")
                context_parts.append(qual_content[:15000])
            
            # Quantitative data
            if "quantitative_data" in data_room:
                context_parts.append("\n### Quantitative Data\n")
                quant_content = data_room["quantitative_data"].get("content", "")
                context_parts.append(quant_content[:15000])
        
        full_context = "\n".join(context_parts)
        print(f"    📊 Context prepared: {len(full_context):,} characters")
        
        return full_context
    
    def _analyze_risks(self, company_name: str, context: str) -> Dict:
        """Analyze risks using OpenAI"""
        
        system_prompt = """You are an expert investment risk analyst conducting due diligence for a VC/PE firm.

Your role is to identify material risks, anomalies, and red flags that could impact investment decisions.

CRITICAL RULES:
1. ONLY flag risks that have EVIDENCE in the provided documents
2. Do NOT make up or infer risks without supporting data
3. Every risk must be cited to specific sources
4. Distinguish between VALIDATED risks (evidence exists) and OPEN QUESTIONS (needs further DD)
5. Be specific - vague concerns are not helpful"""

        user_prompt = f"""Analyze the following intelligence for {company_name} and identify material risks.

{context}

Scan for risks across these categories:

1. **Market & Competition Risk**: Market size concerns, competitive threats, positioning weaknesses
2. **Customer & Revenue Risk**: Concentration risk, churn, contract terms, revenue quality
3. **Business Model & Monetization**: Margin issues, unit economics, scalability constraints
4. **Financial Risks**: Burn rate, runway, working capital, revenue/margin shifts
5. **Team & Governance**: Management gaps, turnover, cap table issues, founder control
6. **Legal & Regulatory**: Compliance gaps, litigation, regulatory exposure

For each risk category, identify:
- VALIDATED RISKS: Issues with clear evidence (cite sources)
- OPEN QUESTIONS: Areas requiring further due diligence

Return a JSON structure:

{{
  "top_risks": [
    {{
      "category": "Customer & Revenue Risk",
      "risk": "High customer concentration",
      "severity": "High",
      "evidence": "Top 3 customers represent 65% of revenue per financials.xlsx",
      "source": "Data Room - Cap Table sheet",
      "potential_impact": "Loss of any top customer could significantly impact revenue",
      "mitigant": "Diversification plan, multi-year contracts, expansion into new segments"
    }}
  ],
  "open_questions": [
    {{
      "category": "Market & Competition",
      "question": "What is the company's defensibility against larger competitors entering the market?",
      "context": "Market research shows low barriers to entry",
      "priority": "High",
      "suggested_dd": "Analyze competitive moats, interview customers about switching costs"
    }}
  ],
  "data_quality_issues": [
    {{
      "issue": "Revenue data inconsistency",
      "description": "Pitch deck shows $5M ARR but financials show $4.2M revenue",
      "sources": "Deck page 5 vs financials.xlsx",
      "recommendation": "Clarify revenue recognition methodology and reconcile numbers"
    }}
  ]
}}

REQUIREMENTS:
- Include 5-10 top risks (prioritize by severity and potential impact)
- Include 5-10 open questions for further DD
- Flag any data inconsistencies or quality issues
- Every item MUST have specific evidence and source citations
- If no risks found in a category, omit it (don't create placeholder risks)"""

        self._update_progress("risk_scan", 40, f"Sending {len(context):,} chars to OpenAI for risk analysis...")
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_completion_tokens=8000,
            response_format={"type": "json_object"}  # Enforce JSON output
        )
        
        content = response.choices[0].message.content
        
        self._update_progress("risk_scan", 70, f"Received {len(content):,} chars from OpenAI")
        
        # Parse JSON response
        try:
            risk_data = json.loads(content)
            self._update_progress("risk_scan", 75, f"Identified {len(risk_data.get('top_risks', []))} risks")
        except json.JSONDecodeError as e:
            print(f"⚠️  Error parsing JSON response: {e}")
            risk_data = {
                "top_risks": [],
                "open_questions": [],
                "data_quality_issues": [],
                "error": "Failed to parse risk analysis"
            }
        
        return {
            "content": content,
            "structured_data": risk_data,
            "generated_at": datetime.now().isoformat()
        }
    
    def format_report_as_text(self, report: Dict) -> str:
        """Format the risk scanner report as readable text"""
        output = []
        
        output.append("=" * 80)
        output.append("RISK SCANNER REPORT")
        output.append("=" * 80)
        output.append(f"\nCompany: {report['company_name']}")
        output.append(f"Generated: {report['generated_at']}")
        output.append("\n" + "=" * 80 + "\n")
        
        risk_analysis = report.get("risk_analysis", {})
        structured_data = risk_analysis.get("structured_data", {})
        
        # Top Risks
        top_risks = structured_data.get("top_risks", [])
        if top_risks:
            output.append("\n## TOP MATERIAL RISKS\n")
            for i, risk in enumerate(top_risks, 1):
                output.append(f"\n### Risk {i}: {risk.get('risk', 'Unknown')}")
                output.append(f"Category: {risk.get('category', 'N/A')}")
                output.append(f"Severity: {risk.get('severity', 'N/A')}")
                output.append(f"Evidence: {risk.get('evidence', 'N/A')}")
                output.append(f"Source: {risk.get('source', 'N/A')}")
                output.append(f"Potential Impact: {risk.get('potential_impact', 'N/A')}")
                output.append(f"Potential Mitigant: {risk.get('mitigant', 'N/A')}")
                output.append("")
        
        # Open Questions
        open_questions = structured_data.get("open_questions", [])
        if open_questions:
            output.append("\n## OPEN QUESTIONS / FURTHER DD REQUIRED\n")
            for i, q in enumerate(open_questions, 1):
                output.append(f"\n{i}. {q.get('question', 'Unknown')}")
                output.append(f"   Category: {q.get('category', 'N/A')}")
                output.append(f"   Priority: {q.get('priority', 'Medium')}")
                output.append(f"   Context: {q.get('context', 'N/A')}")
                output.append(f"   Suggested DD: {q.get('suggested_dd', 'N/A')}")
                output.append("")
        
        # Data Quality Issues
        data_issues = structured_data.get("data_quality_issues", [])
        if data_issues:
            output.append("\n## DATA QUALITY ISSUES\n")
            for i, issue in enumerate(data_issues, 1):
                output.append(f"\n{i}. {issue.get('issue', 'Unknown')}")
                output.append(f"   Description: {issue.get('description', 'N/A')}")
                output.append(f"   Sources: {issue.get('sources', 'N/A')}")
                output.append(f"   Recommendation: {issue.get('recommendation', 'N/A')}")
                output.append("")
        
        return "\n".join(output)

