"""
Example script demonstrating how to use the OpenAI Deep Research Agent
This version uses OpenAI's built-in web search - no Tavily needed!
"""

from deal_copilot.agents.deep_research_agent_openai import DeepResearchAgentOpenAI


def run_example():
    """Run an example research report for Bizzi using OpenAI"""
    
    # Initialize the OpenAI agent
    agent = DeepResearchAgentOpenAI()
    
    # Example from statement.md
    company_info = {
        "company_name": "Bizzi",
        "website": "https://bizzi.vn/en/",
        "sector": "SaaS",
        "region": "Vietnam",
        "hq_location": "Vietnam"
    }
    
    print("\n" + "="*80)
    print("Running Example: Bizzi Deep Research (OpenAI Edition)")
    print("="*80 + "\n")
    
    # Generate the full report
    report = agent.generate_full_report(**company_info)
    
    # Format and display the report
    text_report = agent.format_report_as_text(report)
    print(text_report)
    
    # Save to file
    output_file = "bizzi_research_report_openai.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text_report)
    
    print(f"\n✅ Report saved to: {output_file}")


if __name__ == "__main__":
    try:
        run_example()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()





