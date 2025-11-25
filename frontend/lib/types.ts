export interface CompanyInfo {
  company_name: string;
  website: string;
  sector: string;
  region: string;
  hq_location?: string;
}

export interface Section {
  section: string;
  content: string;
  timestamp: string;
}

export interface Report {
  company_name: string;
  website: string;
  sector: string;
  region: string;
  generated_at: string;
  sections: Section[];
}

export interface ResearchResponse {
  report_id: string;
  status: string;
  message: string;
  company_info: CompanyInfo;
}

export interface StatusResponse {
  report_id: string;
  status: "queued" | "processing" | "completed" | "failed";
  message: string;
  company_info?: CompanyInfo;
}

export interface ReportResponse {
  report_id: string;
  status: string;
  report?: Report;
}

