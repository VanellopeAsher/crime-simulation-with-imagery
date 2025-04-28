
def build_prompt(criminal, crime_rate, cbg, environment, target_str, police_count):
    if environment == None:
        env = ''
    else:
        env=f"""
        - Environmental Safety Score(1-10): {environment.get('rating', '-')}.Environmental safety score is a measure of the safety and security of the area, with 1 being very unsafe & lack of guardianship & suitable for crime, and 10 being very safe & fully under guardianship & unsuiable for crime.
        - Current CBG Description: {environment.get('description', '-')}
        """
    if cbg == None:
        print('cbg is None')
    if 'Total population' in cbg['data'].columns:
        population = cbg['data'].get('Total population','-').iloc[0].item()
    else:
        population = '-'
    if 'average_income' in cbg['data'].columns:
        income = cbg['data'].get('average_income','-').iloc[0].item()
    else:
        income = '-'
    if 'poverty_ratio' in cbg['data'].columns:
        poverty_ratio = cbg['data'].get('poverty_ratio','-').iloc[0].item()
    else:
        poverty_ratio = '-'
    if 'housing_value' in cbg['data'].columns:
        housing_value = cbg['data'].get('housing_value','-').iloc[0].item()
    else:
        housing_value = '-'
    if crime_rate.empty == False:
        crime_rate = crime_rate.iloc[0].item()
    else:
        crime_rate = '-'

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

        CBG Attributes:
            """+ env +f"""
        - Number of POIs: {len(cbg['poi'])}
        Points of Interest (POIs) reflect the density and diversity of activity in an area.   A high number of POIs could indicate a lively, monitored      environment.
        - Total population: {population}
        - A higher population may increase the likelihood of social interaction and surveillance, but could also mean less individual attention, potentially creating opportunities for crime in more crowded areas.
        - average_income(＄): {income}
        Higher average income can be an indicator of affluence.
        - poverty_ratio: {poverty_ratio}
        A higher poverty ratio is often linked to economic desperation, lack of resources, and social instability, which may create an environment where crime is perceived as a necessary means of survival.
        - housing_value（＄）: {housing_value}
        Housing value can indicate the affluence of an area.   High housing values may suggest a wealthier community with greater resources for surveillance.
        - Crime Rate in the past year (crime number / population): {crime_rate}
        The recent crime rate provides direct insight into the area's current safety level.   A higher crime rate can suggest a lack of law enforcement, economic instability, or environmental factors that encourage criminal activity.

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