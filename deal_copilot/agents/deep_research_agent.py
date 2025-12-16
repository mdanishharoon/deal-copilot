"""Deep Research Agent - Produces investor-grade research on markets, competitors, and companies"""

from typing import Dict, List, Optional
from datetime import datetime
from tavily import TavilyClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from deal_copilot.config import config


class DeepResearchAgent:
    """
    Agent that produces investor-grade research documents with:
    - Market Overview
    - Competitor Overview
    - Company/Team Overview and Newsrun
    """
    
    def __init__(self):
        """Initialize the Deep Research Agent with Gemini and Tavily"""
        self.llm = ChatGoogleGenerativeAI(
            model=config.MODEL_NAME,
            google_api_key=config.GOOGLE_API_KEY,
            temperature=config.TEMPERATURE,
            max_output_tokens=config.MAX_OUTPUT_TOKENS,
            convert_system_message_to_human=True  # Required for Gemini models
        )
        self.tavily_client = TavilyClient(api_key=config.TAVILY_API_KEY)
        
    def search_web(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search the web using Tavily API
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, content, and URL
        """
        try:
            response = self.tavily_client.search(
                query=query,
                max_results=max_results,
                search_depth=config.SEARCH_DEPTH,
                include_answer=True,
                include_raw_content=False
            )
            return response.get('results', [])
        except Exception as e:
            print(f"Error searching web: {e}")
            return []
    
    def generate_market_overview(self, company_name: str, sector: str, region: str) -> Dict:
        """
        Generate Market Overview section
        
        Key questions:
        - TAM/SAM/SOM and CAGR
        - Industry business model and monetization
        - Market structure & dynamics
        - Drivers and risks
        - Outcome potential
        """
        print(f"\n🔍 Researching Market Overview for {sector} in {region}...")
        
        # Conduct multiple targeted searches
        search_queries = [
            f"{sector} market size TAM SAM growth rate {region}",
            f"{sector} industry business model monetization trends {region}",
            f"{sector} market dynamics competitive landscape {region}",
            f"{sector} market growth drivers risks {region}"
        ]
        
        all_results = []
        for query in search_queries:
            results = self.search_web(query, max_results=3)
            all_results.extend(results)
        
        # Prepare context from search results
        context = self._format_search_results(all_results)
        
        # Generate analysis using LLM
        system_prompt = """You are a world-class investment analyst producing investor-grade market research.
Your analysis must be:
1. Factual and data-driven with specific numbers
2. Include inline citations as HTML links
3. Professional and concise
4. Focused on investment implications
5. Formatted as clean HTML (NOT markdown)"""

        user_prompt = f"""Based on the following research data, provide market context for evaluating {company_name} in the {sector} sector in {region}.

Focus on what matters for this specific investment opportunity:

1. **Market Size & Growth**: Current market size and CAGR? Is this a large, fast-growing market? Include specific numbers with sources.
2. **Market Dynamics & Structure**: Is it winner-takes-most or room for multiple players? Network effects or economies of scale? What makes this market attractive or challenging?
3. **Key Market Drivers & Risks**: Top growth drivers and main threats/risks. How do these affect {company_name}'s opportunity?
4. **Investment Opportunity**: Can a leader reach $100M+ revenue and $1B+ valuation? Why is now the right time?

Research Data:
{context}

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

Focus on insights relevant to evaluating {company_name}'s opportunity. Skip generic business model descriptions."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "section": "Market Overview",
            "content": response.content,
            "sources": [r.get('url') for r in all_results if r.get('url')],
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_competitor_overview(self, company_name: str, sector: str, region: str) -> Dict:
        """
        Generate Competitor Overview section
        
        Key questions:
        - Who are closest competitors?
        - How is the company positioned/differentiated?
        - What are the competitive moats?
        """
        print(f"\n🔍 Researching Competitor Overview for {company_name}...")
        
        search_queries = [
            f"{company_name} competitors alternatives {sector} {region}",
            f"{sector} competitive landscape market leaders {region}",
            f"{company_name} competitive advantages differentiation",
            f"{sector} market leaders comparison {region}"
        ]
        
        all_results = []
        for query in search_queries:
            results = self.search_web(query, max_results=3)
            all_results.extend(results)
        
        context = self._format_search_results(all_results)
        
        system_prompt = """You are a world-class investment analyst conducting competitive analysis.
Your analysis must:
1. Identify key competitors with evidence
2. Analyze competitive positioning and differentiation
3. Assess potential moats (network effects, data, brand, etc.)
4. Include inline citations as HTML links
5. Format output as clean HTML (NOT markdown)"""

        user_prompt = f"""Based on the research data, write a Competitor Overview for {company_name} in the {sector} sector ({region}).

Address these key questions:
1. **Identification & Scope**: Who are the closest competitors and substitutes in {region} and globally? Why are they comparable?
2. **Positioning & Differentiation**: How is {company_name} positioned relative to competitors in terms of scale, strategy, and business model?
3. **MOAT Analysis**: What potential competitive advantages exist? (data assets, brand, workflow lock-in, network density, partnerships, etc.)

Research Data:
{context}

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

Focus on investment-relevant insights."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "section": "Competitor Overview",
            "content": response.content,
            "sources": [r.get('url') for r in all_results if r.get('url')],
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_company_overview(self, company_name: str, website: str, sector: str) -> Dict:
        """
        Generate Company/Team Overview and Newsrun
        
        Key questions:
        - What problem does the company solve?
        - Who are the founders and key executives?
        - Recent milestones and momentum signals
        """
        print(f"\n🔍 Researching Company Overview for {company_name}...")
        
        search_queries = [
            f"{company_name} {website} company overview product",
            f"{company_name} founders executives team background",
            f"{company_name} funding news partnerships recent announcements",
            f"{company_name} traction growth product-market fit",
            f"{company_name} latest news 2024 2025"
        ]
        
        all_results = []
        for query in search_queries:
            results = self.search_web(query, max_results=3)
            all_results.extend(results)
        
        context = self._format_search_results(all_results)
        
        system_prompt = """You are a world-class investment analyst researching companies for due diligence.
Your analysis must:
1. Provide factual information about the company and team
2. Highlight material events and momentum signals
3. Assess product-market fit evidence
4. Include inline citations as HTML links with dates where available
5. Format output as clean HTML (NOT markdown)"""

        user_prompt = f"""Based on the research data, write a Company/Team Overview and Newsrun for {company_name}.

Address these key questions:

**Company Overview:**
- What core problem does {company_name} solve, and for whom?
- What is their product/service offering?
- What public evidence shows product-market fit (traction, scale, retention)?

**Team Overview:**
- Who are the founders and key executives?
- What is their relevant experience and past outcomes?
- Any leadership changes or governance signals?

**Momentum & Risk Signals:**
- Recent milestones: funding rounds, expansions, partnerships, product launches
- Any red flags: layoffs, executive departures, regulatory issues, security incidents
- For each material event, include: Date, Headline, 1-line description, Impact, and Source

Research Data:
{context}

FORMATTING INSTRUCTIONS - VERY IMPORTANT:
- Format your response as clean HTML suitable for web display
- Use <h3> for major section headings (Company Overview, Team Overview, Momentum & Risk Signals)
- Use <h4> for subheadings within sections
- Use <p> for paragraphs with clear spacing
- Use <strong> for emphasis (NOT asterisks or markdown)
- Use <ul> and <li> for bullet lists
- For news events, use a clean list format with HTML
- Use <a href="URL" target="_blank" class="text-blue-600 hover:underline">[Source]</a> for citations
- DO NOT use markdown syntax (**, ##, -, etc.)
- DO NOT return JSON or raw text
- Return ONLY well-formatted HTML content

Focus on material, investment-relevant information."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "section": "Company/Team Overview and Newsrun",
            "content": response.content,
            "sources": [r.get('url') for r in all_results if r.get('url')],
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
        print(f"DEEP RESEARCH AGENT - Deal Co-Pilot POC")
        print(f"{'='*60}")
        print(f"Company: {company_name}")
        print(f"Sector: {sector}")
        print(f"Region: {region}")
        print(f"Website: {website}")
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
    
    def _format_search_results(self, results: List[Dict]) -> str:
        """Format search results for LLM context"""
        formatted = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'N/A')
            content = result.get('content', '')
            url = result.get('url', '')
            
            formatted.append(f"""
[Result {i}]
Title: {title}
URL: {url}
Content: {content}
---""")
        
        return "\n".join(formatted)
    
    def format_report_as_text(self, report: Dict) -> str:
        """Format the report as readable text"""
        output = []
        
        # Header
        output.append("=" * 80)
        output.append("DEEP RESEARCH REPORT")
        output.append("Deal Co-Pilot POC")
        output.append("=" * 80)
        output.append(f"\nCompany: {report['company_name']}")
        output.append(f"Sector: {report['sector']}")
        output.append(f"Region: {report['region']}")
        output.append(f"Website: {report['website']}")
        output.append(f"Generated: {report['generated_at']}")
        output.append("\n" + "=" * 80 + "\n")
        
        # Sections
        for section in report['sections']:
            output.append(f"\n## {section['section']}\n")
            output.append(section['content'])
            output.append("\n" + "-" * 80 + "\n")
        
        # References
        output.append("\n## References\n")
        all_sources = []
        for section in report['sections']:
            all_sources.extend(section['sources'])
        
        unique_sources = list(set(all_sources))
        for i, source in enumerate(unique_sources, 1):
            output.append(f"{i}. {source}")
        
        return "\n".join(output)
