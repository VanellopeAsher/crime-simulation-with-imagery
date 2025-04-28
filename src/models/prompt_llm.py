
def build_prompt(criminal, crime_rate, cbg, environment, target_str, police_count):
    prompt = f"""You are an expert criminologist specializing in predicting the decision-making processes of potential criminal agents. Based on the following agent attributes and contextual parameters, simulate a detailed internal reasoning process about whether or not the agent is likely to commit a crime, and provide a response that reflects this process. Low environmental safety score may encourage crime motivation. 

    Agent Attributes:
        - ID: {criminal['agent_id']}
        - Gender: {criminal['gender']}
        - Race: {criminal['race']}
        - Residence: {criminal['residence']}
        - Historical Trajectory: {criminal['historical_trajectory']}
        - Criminal Record: {criminal['criminal_record']}
        - Current Location: {criminal['current_location']}
    
    Temporal Parameters:
        - Potential Targets: {target_str}
        - Number of Patrolling Police Officers: {police_count}

    Your response should be in the form of a JSON object with no additional text.
    """+"""If a crime is predicted, output:
    {
        "status": true,
        "reasoning": "{Detailed explanation of the reasoning process leading to the decision to commit a crime. Include relevant factors such as the agent’s past actions, environmental conditions, motivations, and any perceived opportunities or risks.}",
        "objective_id": "{ID of the chosen target}"
    }

    If no crime is predicted, output:
    {
        "status": false,
        "reasoning": "{Reason for not committing the crime. Consider factors like deterrents, risks, changes in motivation, or other factors that may have influenced the agent's decision not to commit a crime.}"
    }

    Remember to output ONLY the JSON with no additional text."""
    return prompt