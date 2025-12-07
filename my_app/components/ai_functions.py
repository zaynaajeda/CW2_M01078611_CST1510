#Function that returns system prompt for a certain domain
def get_system_prompt(domain):
    #System prompts for each domain
    #System prompt for general AI Assistant
    if domain == "General":
        system_prompt = "You are a helpful assistant."

    #System prompt for Cyber Security specialised AI Assistant
    elif domain == "Cyber Security":
        system_prompt = """
                        You are a cybersecurity expert assistant.

                        - Analyze incidents and threats
                        - Provide technical guidance
                        - Explain attack vectors & mitigations
                        - Use standard terminology (MITRE, CVE)
                        - Prioritize actionable recommendations
                        """
        
    #System prompt for Data Science specialised AI Assistant
    elif domain == "Data Science":
        system_prompt = """
                        You are a senior data science assistant.

                        - Clarify objectives, constraints, and data context
                        - Recommend statistical tests, ML models, and feature engineering steps
                        - Provide python/pandas/scikit-learn code when helpful
                        - Justify trade-offs between accuracy, interpretability, and compute cost
                        - Highlight data quality, bias, and validation considerations
                        """

    #System prompt for IT Operations specialised AI Assistant
    elif domain == "IT Operations":
        system_prompt = """
                        You are an IT operations command-center assistant.

                        - Triage incidents and service tickets quickly
                        - Recommend troubleshooting steps and escalation paths
                        - Call out monitoring, automation, and reliability improvements
                        - Translate impact in terms of SLAs and business services
                        - Communicate clearly for support engineers and stakeholders
                        """
    else:
        #Basic system prompt(unsupported domain)
        system_prompt = "You are a helpful assistant."

    #Prompt message is returned
    return system_prompt

#Function that returns prompt for inguiry(incident/dataset/ticket) in a certain domain
#Based on the domain selected from dashboard, the appropriate prompt retrieves insights about its corresponding inquiry
def get_ai_prompt(domain, inquiry):
    #Prompt for incident in cyber security domain
    if domain == "Cyber Security":
        prompt = f"""
                You are a cybersecurity expert assistant.

                Analyse the following incident and explain the following:
                -Analysis of the root cause
                -Immediate actions
                -Provide technical guidance
                -Preventive measures
                -Risk level with explanation

                Incident details:
                -Type: {inquiry['incident_type']}
                -Severity: {inquiry['severity']}
                -Status: {inquiry['status']}
                -Description: {inquiry['description']}
            """
        
    #Prompt for dataset in data science domain
    elif domain == "Data Science":
        prompt = f"""
                You are a senior data science assistant.

                Review the following dataset metadata and provide:
                -Primary business problems or analyses this dataset can support
                -Recommended data quality checks or integrity issues to watch
                -Feature engineering or transformation ideas
                -Appropriate modelling or visualisation approaches
                -Operational considerations (refresh cadence, owners, monitoring)

                Dataset details:
                -Name: {inquiry['dataset_name']}
                -Category: {inquiry['category']}
                -Source: {inquiry['source']}
                -Last Updated: {inquiry['last_updated']}
                -Record Count: {inquiry['record_count']}
                -Column Count: {inquiry['column_count']}
                -File Size (MB): {inquiry['file_size_mb']}
            """
        
    #Prompt for IT ticket in IT operations domain
    elif domain == "IT Operations":
        prompt = f"""
                You are an IT operations command-center assistant.

                Review the following ticket and provide:
                -Likely root cause or impacted services
                -Immediate triage steps and tooling/logs required
                -Escalation or collaboration recommendations
                -Preventive automation or monitoring improvements
                -Risk level / SLA considerations with justification

                Ticket details:
                -Subject: {inquiry['subject']}
                -Priority: {inquiry['priority']}
                -Status: {inquiry['status']}
                -Category: {inquiry['category']}
                -Assigned To: {inquiry['assigned_to']}
                -Created Date: {inquiry['created_date']}
                -Resolved Date: {inquiry['resolved_date']}
                -Description: {inquiry['description']}
            """
    else:
        #General prompt on provided inquiry(unsupported domain)
        prompt = "Provide an expert analysis based on the supplied information."

    #Prompt message is returned
    return prompt

def get_chart_prompt(domain, insights):
    chart_prompt = f"""
                Review the following {domain} dashboard chart data and provide a concise analysis 
                covering notable trends, anomalies, and recommended actions.
                Chart data:{insights}               
                """
    return chart_prompt
