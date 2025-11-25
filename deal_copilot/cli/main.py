"""
Main entry point for Deal Co-Pilot POC - Deep Research Agent

Usage:
    python main.py --company "Bizzi" --sector "SaaS" --region "Vietnam" --website "https://bizzi.vn/en/"
    
Or run interactively:
    python main.py
"""

import argparse
import json
import os
from datetime import datetime
from deal_copilot.agents.deep_research_agent import DeepResearchAgent


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Deal Co-Pilot POC - Deep Research Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with specific company
  python main.py --company "Bizzi" --sector "SaaS" --region "Vietnam" --website "https://bizzi.vn/en/"
  
  # Run interactively
  python main.py
  
  # Save output to file
  python main.py --company "Bizzi" --sector "SaaS" --region "Vietnam" --website "https://bizzi.vn/en/" --output report.txt
        """
    )
    
    parser.add_argument(
        '--company',
        type=str,
        help='Company name (e.g., Bizzi)'
    )
    
    parser.add_argument(
        '--sector',
        type=str,
        help='Sector/vertical (e.g., SaaS, Fintech, Marketplace, Healthtech)'
    )
    
    parser.add_argument(
        '--region',
        type=str,
        help='Geographic region (e.g., Vietnam, Southeast Asia, Global)'
    )
    
    parser.add_argument(
        '--website',
        type=str,
        help='Company website URL (e.g., https://bizzi.vn/en/)'
    )
    
    parser.add_argument(
        '--hq',
        type=str,
        help='HQ location if different from region'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file path (default: print to console)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )
    
    return parser.parse_args()


def get_interactive_input():
    """Get input interactively from user"""
    print("\n" + "="*60)
    print("Deal Co-Pilot POC - Deep Research Agent")
    print("="*60 + "\n")
    
    print("Please provide the following information:\n")
    
    company = input("Company name: ").strip()
    sector = input("Sector (e.g., SaaS, Fintech, Marketplace): ").strip()
    region = input("Region (e.g., Vietnam, Southeast Asia): ").strip()
    website = input("Website URL: ").strip()
    hq = input("HQ location (optional, press Enter to skip): ").strip() or None
    
    return {
        'company': company,
        'sector': sector,
        'region': region,
        'website': website,
        'hq': hq
    }


def save_report(report: dict, output_path: str, as_json: bool = False):
    """Save report to file"""
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    if as_json:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Report saved to: {output_path}")
    else:
        agent = DeepResearchAgent()
        text_report = agent.format_report_as_text(report)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_report)
        print(f"\n✅ Report saved to: {output_path}")


def main():
    """Main execution function"""
    args = parse_arguments()
    
    # Get input either from command line or interactively
    if args.company and args.sector and args.region and args.website:
        company_name = args.company
        sector = args.sector
        region = args.region
        website = args.website
        hq_location = args.hq
    else:
        if any([args.company, args.sector, args.region, args.website]):
            print("\n⚠️  Please provide all required arguments: --company, --sector, --region, --website")
            print("Or run without arguments for interactive mode.\n")
            return
        
        # Interactive mode
        inputs = get_interactive_input()
        company_name = inputs['company']
        sector = inputs['sector']
        region = inputs['region']
        website = inputs['website']
        hq_location = inputs['hq']
    
    # Validate inputs
    if not all([company_name, sector, region, website]):
        print("\n❌ Error: All fields are required (company, sector, region, website)")
        return
    
    try:
        # Initialize agent
        agent = DeepResearchAgent()
        
        # Generate report
        report = agent.generate_full_report(
            company_name=company_name,
            website=website,
            sector=sector,
            region=region,
            hq_location=hq_location
        )
        
        # Output report
        if args.output:
            save_report(report, args.output, args.json)
        else:
            # Print to console
            if args.json:
                print(json.dumps(report, indent=2, ensure_ascii=False))
            else:
                text_report = agent.format_report_as_text(report)
                print(text_report)
        
        print("\n✨ Deep Research completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

