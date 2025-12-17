"""
Deep Research Agent using OpenAI's built-in web search capabilities
No external search API (like Tavily) needed - OpenAI handles search internally
"""

from typing import Dict, List, Optional
from datetime import datetime
from openai import OpenAI
from deal_copilot.config import config_openai as config


class DeepResearchAgentOpenAI:
    """
    Agent that produces investor-grade research using OpenAI's native capabilities
    
    Sections produced:
    - Market Overview
    - Competitor Overview
    - Company/Team Overview and Newsrun
    
    Unlike the Tavily+Gemini version, this uses OpenAI's built-in web search,
    so it handles both retrieval and generation in a single API call.
    """
    
    def __init__(self, stream_callback=None):
        """
        Initialize the Deep Research Agent with OpenAI
        
        Args:
            stream_callback: Optional function to call with streaming content chunks
                            Signature: callback(chunk: str)
        """
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL
        self.stream_callback = stream_callback
    
    def generate_market_overview(self, company_name: str, sector: str, region: str) -> Dict:
        """
        Generate Market Overview section using OpenAI's web search
        
        Key questions:
        - TAM/SAM/SOM and CAGR
        - Industry business model and monetization
        - Market structure & dynamics
        - Drivers and risks
        - Outcome potential
        """
        print(f"\n🔍 Researching Market Overview for {sector} in {region}...")
        
        prompt = f"""You are a world-class investment analyst conducting market research for a VC/PE firm.

Research the {sector} market in {region} to provide market context for evaluating {company_name}.

Your analysis should focus on what matters for this specific investment opportunity:

1. **Market Size & Growth**:
   - Current market size and CAGR for {sector} in {region}
   - Is this a large, fast-growing market? What's driving growth?
   - Include specific numbers with sources

2. **Market Dynamics & Structure**:
   - Is this winner-takes-most or room for multiple players?
   - Are there network effects, economies of scale, or data moats in this market?
   - What makes this market attractive or challenging?

3. **Key Market Drivers & Risks**:
   - What are the top growth drivers (regulatory tailwinds, digitization, AI adoption, demographics, etc.)?
   - What are the main threats/risks (regulatory headwinds, supply constraints, platform dependency, cyclicality)?
   - How do these affect {company_name}'s opportunity?

4. **Investment Opportunity**:
   - Can a leader in this space realistically reach $100M+ revenue and $1B+ valuation?
   - Why is now the right time for {sector} in {region}?

Requirements:
- Focus on insights relevant to evaluating {company_name}'s opportunity
- Use CURRENT data (2024-2025) where available
- Include key data points with sources
- Skip generic business model descriptions - focus on market dynamics
- Be specific to {region} while drawing global comparisons where relevant

FORMATTING INSTRUCTIONS - VERY IMPORTANT:
- Format your response as clean HTML suitable for web display
- Use <h3> for major headings
- Use <h4> for subheadings
- Use <p> for paragraphs with clear spacing
- Use <strong> for emphasis (NOT asterisks or markdown)
- Use <ul> and <li> for bullet lists
- Use proper HTML anchor tags for citations
- DO NOT use markdown syntax (**, ##, -, etc.)
- DO NOT return JSON or raw text
- Return ONLY well-formatted HTML content

Search the web and provide focused market context for this investment opportunity."""

        try:
            # Combine system message into the prompt
            full_input = f"""You are an expert investment analyst with deep knowledge of market research and due diligence. You have access to web search to find current, factual information.

{prompt}"""
            
            # Use Responses API with web search enabled
            response = self.client.responses.create(
                model=self.model,
                tools=[{"type": "web_search"}],
                input=full_input
            )
            
            content = response.output_text
            
            # Stream the content if callback provided (simulate streaming since Responses API returns complete response)
            if self.stream_callback:
                # Split into chunks and stream
                chunk_size = 50
                for i in range(0, len(content), chunk_size):
                    chunk = content[i:i+chunk_size]
                    self.stream_callback(chunk)
            
            return {
                "section": "Market Overview",
                "content": content,
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error generating market overview: {e}")
            return {
                "section": "Market Overview",
                "content": f"Error: {str(e)}",
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_competitor_overview(self, company_name: str, sector: str, region: str) -> Dict:
        """
        Generate Competitor Overview section using OpenAI's web search
        
        Key questions:
        - Who are closest competitors?
        - How is the company positioned/differentiated?
        - What are the competitive moats?
        """
        print(f"\n🔍 Researching Competitor Overview for {company_name}...")
        
        prompt = f"""You are a world-class investment analyst conducting competitive analysis for a VC/PE firm.

Research {company_name} and the {sector} competitive landscape in {region}.

Use web search to gather current information and address these key questions:

1. **Identification & Scope**: 
   - Who are {company_name}'s closest competitors and substitutes in {region}?
   - Who are the global exemplars/leaders in this space?
   - Why are these companies comparable (similar business model, customer segment, geography)?

2. **Competitive Positioning & Differentiation**:
   - How is {company_name} positioned relative to competitors in terms of:
     * Scale (revenue, users, market share)
     * Strategy (go-to-market, pricing, target customers)
     * Business model (monetization, unit economics)
   - What is {company_name}'s unique value proposition?

3. **MOAT Analysis**:
   - What competitive advantages (moats) does {company_name} have or is building?
     * Data assets or AI/ML capabilities
     * Brand and reputation
     * Workflow lock-in or switching costs
     * Network effects or marketplace density
     * Regulatory approvals/licenses
     * Strategic partnerships or distribution
     * Technology/IP advantages
   - How durable are these advantages?
   - What evidence exists for defensibility?

Requirements:
- Compare {company_name} to at least 3-5 direct competitors
- Use current information (2024-2025)
- Include specific examples and data points
- Cite sources inline using HTML links
- Focus on investment implications
- Be balanced - acknowledge both strengths and weaknesses

FORMATTING INSTRUCTIONS - VERY IMPORTANT:
- Format your response as clean HTML suitable for web display
- Use <h3> for major headings
- Use <h4> for subheadings
- Use <p> for paragraphs with clear spacing
- Use <strong> for emphasis (NOT asterisks or markdown)
- Use <ul> and <li> for bullet lists
- Use <a href="URL" target="_blank" class="text-blue-600 hover:underline">[Source]</a> for citations
- DO NOT use markdown syntax (**, ##, -, etc.)
- DO NOT return JSON or raw text
- Return ONLY well-formatted HTML content

Search the web thoroughly and provide detailed competitive intelligence."""

        try:
            # Combine system message into the prompt
            full_input = f"""You are an expert investment analyst specializing in competitive analysis and market intelligence. Use web search to find current, factual information.

{prompt}"""
            
            # Use Responses API with web search enabled
            response = self.client.responses.create(
                model=self.model,
                tools=[{"type": "web_search"}],
                input=full_input
            )
            
            content = response.output_text
            
            # Stream the content if callback provided (simulate streaming since Responses API returns complete response)
            if self.stream_callback:
                # Split into chunks and stream
                chunk_size = 50
                for i in range(0, len(content), chunk_size):
                    chunk = content[i:i+chunk_size]
                    self.stream_callback(chunk)
            
            return {
                "section": "Competitor Overview",
                "content": content,
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error generating competitor overview: {e}")
            return {
                "section": "Competitor Overview",
                "content": f"Error: {str(e)}",
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_company_overview(self, company_name: str, website: str, sector: str) -> Dict:
        """
        Generate Company/Team Overview and Newsrun using OpenAI's web search
        
        Key questions:
        - What problem does the company solve?
        - Who are the founders and key executives?
        - Recent milestones and momentum signals
        """
        print(f"\n🔍 Researching Company Overview for {company_name}...")
        
        prompt = f"""You are a world-class investment analyst conducting company due diligence for a VC/PE firm.

Research {company_name} ({website}) in the {sector} sector.

Use web search to gather comprehensive information and address these sections:

**COMPANY OVERVIEW:**
1. What core problem does {company_name} solve, and for whom (target customers)?
2. What is their product/service offering and value proposition?
3. What public evidence exists of product-market fit?
   - Traction metrics (users, revenue, growth)
   - Scale indicators
   - Customer retention/satisfaction signals
   - Notable customer wins or case studies

**TEAM OVERVIEW:**
1. Who are the founders and what are their backgrounds?
   - Previous companies/roles
   - Relevant domain expertise
   - Track record of success
2. Who are the key executives (CEO, CTO, CFO, etc.)?
3. Any notable advisors or board members?
4. Any red flags: leadership turnover, founder conflicts, governance issues?

**MOMENTUM & RISK SIGNALS (Recent 12-24 months):**
Research recent news and announcements. For each material event, provide:
- Date, Headline, 1-2 line description, Impact (positive/negative/neutral), and Source

Key events to look for:
- POSITIVE: Funding rounds, revenue milestones, partnerships, product launches, expansions, customer wins, awards
- NEGATIVE: Layoffs, executive departures, customer losses, regulatory issues, security breaches, lawsuits, negative press
- NEUTRAL: Rebrands, minor announcements, industry commentary

Requirements:
- Focus on MATERIAL events only (meaningful to investors)
- Include dates for all events
- Cite sources using HTML links
- Be factual and balanced - include both positive and negative signals
- Prioritize recent information (last 12-24 months)
- Look for patterns that signal momentum or concern

FORMATTING INSTRUCTIONS - VERY IMPORTANT:
- Format your response as clean HTML suitable for web display
- Use <h3> for major section headings (Company Overview, Team Overview, Momentum & Risk Signals)
- Use <h4> for subheadings within sections
- Use <p> for paragraphs with clear spacing
- Use <strong> for emphasis (NOT asterisks or markdown)
- Use <ul> and <li> for bullet lists
- For news events, use a clean table or list format with HTML
- Use <a href="URL" target="_blank" class="text-blue-600 hover:underline">[Source]</a> for all citations
- DO NOT use markdown syntax (**, ##, -, etc.)
- DO NOT return JSON or raw text
- Return ONLY well-formatted HTML content

Search the web thoroughly and provide comprehensive company intelligence."""

        try:
            # Combine system message into the prompt
            full_input = f"""You are an expert investment analyst conducting company due diligence. Use web search to find current, factual information about the company, team, and recent news.

{prompt}"""
            
            # Use Responses API with web search enabled
            response = self.client.responses.create(
                model=self.model,
                tools=[{"type": "web_search"}],
                input=full_input
            )
            
            content = response.output_text
            
            # Stream the content if callback provided (simulate streaming since Responses API returns complete response)
            if self.stream_callback:
                # Split into chunks and stream
                chunk_size = 50
                for i in range(0, len(content), chunk_size):
                    chunk = content[i:i+chunk_size]
                    self.stream_callback(chunk)
            
            return {
                "section": "Company/Team Overview and Newsrun",
                "content": content,
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error generating company overview: {e}")
            return {
                "section": "Company/Team Overview and Newsrun",
                "content": f"Error: {str(e)}",
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_full_report(
        self,
        company_name: str,
        website: str,
        sector: str,
        region: str,
        hq_location: Optional[str] = None
    ) -> Dict:
        """
        Generate complete Deep Research report with all sections
        
        Args:
            company_name: Name of the company being analyzed
            website: Company website URL
            sector: Industry sector (e.g., SaaS, Fintech, Marketplace)
            region: Geographic region (e.g., Southeast Asia, Vietnam)
            hq_location: HQ location if different from region
            
        Returns:
            Dictionary containing all report sections and metadata
        """
        print(f"\n{'='*60}")
        print(f"DEEP RESEARCH AGENT - OpenAI Edition")
        print(f"{'='*60}")
        print(f"Company: {company_name}")
        print(f"Sector: {sector}")
        print(f"Region: {region}")
        print(f"Website: {website}")
        print(f"Model: {self.model}")
        print(f"{'='*60}\n")
        
        # Generate each section - Company first (most important!)
        company_section = self.generate_company_overview(company_name, website, sector)
        competitor_section = self.generate_competitor_overview(company_name, sector, region)
        market_section = self.generate_market_overview(company_name, sector, region)
        
        # Compile full report
        report = {
            "company_name": company_name,
            "website": website,
            "sector": sector,
            "region": region,
            "hq_location": hq_location or region,
            "model": self.model,
            "generated_at": datetime.now().isoformat(),
            "sections": [
                company_section,      # Company first!
                competitor_section,   # Then competitive context
                market_section       # Then broader market context
            ]
        }
        
        print(f"\n{'='*60}")
        print(f"✅ Deep Research Report Complete!")
        print(f"{'='*60}\n")
        
        return report
    
    def format_report_as_text(self, report: Dict) -> str:
        """Format the report as readable text"""
        output = []
        
        # Header
        output.append("=" * 80)
        output.append("DEEP RESEARCH REPORT - OpenAI Edition")
        output.append("Deal Co-Pilot POC")
        output.append("=" * 80)
        output.append(f"\nCompany: {report['company_name']}")
        output.append(f"Sector: {report['sector']}")
        output.append(f"Region: {report['region']}")
        output.append(f"Website: {report['website']}")
        output.append(f"Model: {report.get('model', 'N/A')}")
        output.append(f"Generated: {report['generated_at']}")
        output.append("\n" + "=" * 80 + "\n")
        
        # Sections
        for section in report['sections']:
            output.append(f"\n## {section['section']}\n")
            output.append(section['content'])
            output.append("\n" + "-" * 80 + "\n")
        
        return "\n".join(output)





