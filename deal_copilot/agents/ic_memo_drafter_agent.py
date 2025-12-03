"""
IC Memo Drafter Agent
Composes first-draft Investment Committee memo that merges outputs from all agents
Uses OpenAI for synthesis - produces professional, cited IC memo
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from openai import OpenAI
from deal_copilot.config import config_openai as config


class ICMemoDrafterAgent:
    """
    Agent that composes a first-draft Investment Committee memo
    
    Inputs:
    - Deep Research report (Agent 1)
    - Data Room report (Agent 2)
    - Risk Scanner report (Agent 3)
    
    Outputs:
    - Professional IC memo with all required sections
    - Citations throughout
    - Recommendations and next steps
    """
    
    def __init__(self, progress_callback=None, stream_callback=None):
        """
        Initialize the IC Memo Drafter Agent with OpenAI
        
        Args:
            progress_callback: Optional function to call with progress updates
            stream_callback: Optional function to call with streaming content chunks
                            Signature: callback(chunk: str)
        """
        self.progress_callback = progress_callback
        self.stream_callback = stream_callback
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL
    
    def _update_progress(self, step: str, progress: int, message: str):
        """Update progress if callback is provided"""
        if self.progress_callback:
            self.progress_callback(step, progress, message)
        print(f"  [{progress}%] {step}: {message}")
    
    def draft_memo(
        self,
        company_name: str,
        company_info: Dict,
        deep_research_report: Optional[Dict] = None,
        data_room_report: Optional[Dict] = None,
        risk_scanner_report: Optional[Dict] = None
    ) -> Dict:
        """
        Draft comprehensive IC memo
        
        Args:
            company_name: Name of the company
            company_info: Basic company information (sector, region, website)
            deep_research_report: Output from Deep Research Agent
            data_room_report: Output from Data Room Agent
            risk_scanner_report: Output from Risk Scanner Agent
            
        Returns:
            Dictionary with IC memo content
        """
        print(f"\n{'='*60}")
        print(f"IC MEMO DRAFTER AGENT")
        print(f"{'='*60}")
        print(f"Company: {company_name}")
        print(f"{'='*60}\n")
        
        self._update_progress("ic_memo", 10, "Preparing context from all agent outputs...")
        
        # Prepare context from all sources
        context = self._prepare_context(
            company_name,
            company_info,
            deep_research_report,
            data_room_report,
            risk_scanner_report
        )
        
        self._update_progress("ic_memo", 30, "Drafting Executive Summary...")
        
        # Generate IC memo
        memo_content = self._generate_memo(company_name, company_info, context)
        
        self._update_progress("ic_memo", 90, "Finalizing IC memo...")
        
        return {
            "company_name": company_name,
            "generated_at": datetime.now().isoformat(),
            "memo_content": memo_content,
            "sources_used": {
                "deep_research": deep_research_report is not None,
                "data_room": data_room_report is not None,
                "risk_scanner": risk_scanner_report is not None
            }
        }
    
    def _prepare_context(
        self,
        company_name: str,
        company_info: Dict,
        deep_research: Optional[Dict],
        data_room: Optional[Dict],
        risk_scanner: Optional[Dict]
    ) -> str:
        """Prepare context from all intelligence sources"""
        
        context_parts = []
        
        context_parts.append(f"Company: {company_name}\n")
        context_parts.append(f"Sector: {company_info.get('sector', 'N/A')}\n")
        context_parts.append(f"Region: {company_info.get('region', 'N/A')}\n")
        context_parts.append(f"Website: {company_info.get('website', 'N/A')}\n")
        context_parts.append("="*60 + "\n")
        
        # Add Deep Research (public intel)
        if deep_research and "sections" in deep_research:
            context_parts.append("\n## DEEP RESEARCH (Public Intelligence)\n")
            for section in deep_research["sections"]:
                context_parts.append(f"\n### {section.get('title', 'Section')}\n")
                content = section.get('content', '')
                # Strip HTML tags
                import re
                clean_content = re.sub('<[^<]+?>', '', content)
                context_parts.append(clean_content[:15000])  # Limit per section
        
        # Add Data Room intelligence
        if data_room:
            context_parts.append("\n\n## DATA ROOM (Private Intelligence)\n")
            
            # Qualitative
            if "qualitative_analysis" in data_room:
                context_parts.append("\n### Qualitative Analysis\n")
                qual_content = data_room["qualitative_analysis"].get("content", "")
                context_parts.append(qual_content[:20000])
            
            # Quantitative
            if "quantitative_data" in data_room:
                context_parts.append("\n### Quantitative Data\n")
                quant_content = data_room["quantitative_data"].get("content", "")
                context_parts.append(quant_content[:20000])
        
        # Add Risk Analysis
        if risk_scanner and "risk_analysis" in risk_scanner:
            context_parts.append("\n\n## RISK ANALYSIS\n")
            risk_content = risk_scanner["risk_analysis"].get("content", "")
            context_parts.append(risk_content[:15000])
        
        full_context = "\n".join(context_parts)
        print(f"    📊 Context prepared: {len(full_context):,} characters")
        
        return full_context
    
    def _generate_memo(
        self,
        company_name: str,
        company_info: Dict,
        context: str
    ) -> Dict:
        """Generate IC memo using OpenAI"""
        
        system_prompt = """You are an expert investment analyst drafting Investment Committee (IC) memos for a VC/PE firm.

Your role is to synthesize all available intelligence into a professional, actionable IC memo.

CRITICAL REQUIREMENTS:
1. Every factual claim MUST be cited (source: document name, page, or "Public research")
2. Write in professional, investment-grade prose
3. Be balanced - highlight both opportunities AND risks
4. Make a clear recommendation (Proceed to DD / Pass / Hold)
5. Focus on investment implications and decision-making
6. Use specific numbers and data points (with citations)
7. Flag any data gaps or inconsistencies"""

        user_prompt = f"""Draft a comprehensive Investment Committee memo for {company_name}.

Use ALL available intelligence below to create a complete, well-cited IC memo.

{context}

REQUIRED SECTIONS (in order):

1. **Executive Summary** (2-3 paragraphs)
   - Investment thesis in 1-2 sentences
   - Key highlights (traction, market, team)
   - Quick financial snapshot
   - Recommendation overview

2. **Company Overview**
   - What the company does (product/service)
   - Founding team and key executives
   - Key traction metrics and highlights
   - [Cite sources]

3. **Deal Snapshot** (if available)
   - Current round details (size, valuation, terms)
   - Current investors and ownership
   - Use of funds
   - Post-money ownership
   - [Mark N/A if not available]

4. **Market Overview**
   - Market size (TAM/SAM/SOM) and growth
   - Market dynamics and structure
   - Key drivers and tailwinds
   - Market risks
   - [Cite sources]

5. **Competition & MOAT**
   - Competitive landscape
   - Key competitors (regional and global)
   - Company's differentiation
   - Evidence of sustainable competitive advantage
   - [Cite sources]

6. **Team**
   - Founder backgrounds and relevant experience
   - Key executives
   - Any concerns or gaps
   - [Cite sources]

7. **Product & Value Proposition**
   - Customer pain point being solved
   - Key value propositions
   - Product-market fit evidence
   - [Cite sources]

8. **Business Model & Unit Economics**
   - How the company makes money
   - Key metrics (ARR, CAC, LTV, margins, etc.)
   - Unit economics analysis
   - Scalability assessment
   - [Cite sources - data from financials]

9. **Financial Performance** (if available)
   - Revenue trends and growth
   - Profitability / burn
   - Key financial metrics
   - [Use specific numbers from data room]

10. **Investment Highlights**
    - Top 3-5 reasons to invest
    - Each with supporting evidence
    - [Cite sources]

11. **Investment Risks & Mitigants**
    - Top 5 material risks
    - Potential mitigants for each
    - Severity assessment
    - [Reference risk scanner output]

12. **Recommendation & Next Steps**
    - Clear recommendation: Proceed to DD / Pass / Hold (with rationale)
    - If proceeding: List 5-10 key DD items to validate
    - If passing: Explain why
    - Suggested timeline

13. **Appendix Notes**
    - Data sources used
    - Key assumptions made
    - Any data inconsistencies noted
    - Information gaps

FORMAT AS HTML:
- Use <h2> for section headers
- Use <h3> for subsections
- Use <p> for paragraphs
- Use <strong> for emphasis
- Use <ul> and <li> for lists
- Use <em> for citations like: <em>[Source: financials.xlsx, P&L sheet]</em>
- DO NOT use markdown syntax
- Return clean, well-formatted HTML

CITATION FORMAT:
- Every number, claim, or data point MUST have a citation
- Format: <em>[Source: document name, specific location]</em>
- Examples:
  - <em>[Source: Deep Research - Market Overview]</em>
  - <em>[Source: Data Room - financials.xlsx, Revenue tab]</em>
  - <em>[Source: Pitch deck, page 5]</em>
  - <em>[Source: Public research, TechCrunch 2024]</em>

Generate a comprehensive, professional IC memo now."""

        self._update_progress("ic_memo", 40, f"Sending {len(context):,} chars to OpenAI for memo drafting...")
        
        # Use streaming if callback provided
        if self.stream_callback:
            content_parts = []
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_completion_tokens=16000,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    chunk_content = chunk.choices[0].delta.content
                    content_parts.append(chunk_content)
                    # Call stream callback for each chunk
                    if self.stream_callback:
                        self.stream_callback(chunk_content)
            
            content = "".join(content_parts)
        else:
            # Non-streaming fallback
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_completion_tokens=16000
            )
            content = response.choices[0].message.content
        
        self._update_progress("ic_memo", 85, f"Received {len(content):,} chars from OpenAI")
        
        return {
            "content": content,
            "generated_at": datetime.now().isoformat(),
            "word_count": len(content.split())
        }
    
    def format_report_as_text(self, report: Dict) -> str:
        """Format the IC memo as readable text"""
        output = []
        
        output.append("=" * 80)
        output.append("INVESTMENT COMMITTEE MEMO")
        output.append("=" * 80)
        output.append(f"\nCompany: {report['company_name']}")
        output.append(f"Generated: {report['generated_at']}")
        output.append("\n" + "=" * 80 + "\n")
        
        memo_content = report.get("memo_content", {})
        content = memo_content.get("content", "")
        
        # Strip HTML tags for text version
        import re
        text_content = re.sub('<[^<]+?>', '', content)
        text_content = text_content.replace('&nbsp;', ' ')
        text_content = text_content.replace('&lt;', '<')
        text_content = text_content.replace('&gt;', '>')
        text_content = text_content.replace('&amp;', '&')
        
        output.append(text_content)
        output.append("\n" + "=" * 80)
        output.append(f"Word Count: {memo_content.get('word_count', 'N/A')}")
        output.append("=" * 80)
        
        return "\n".join(output)

