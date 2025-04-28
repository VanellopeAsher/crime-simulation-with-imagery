import random
import json
import csv
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.environment.map import Map
from constant import MAP_SCOPE
import numpy as np
import pandas as pd
import math
import json
from constant import MAP_DATA_PATH

map = Map(
    data_cache=MAP_DATA_PATH, 
    map_scope=MAP_SCOPE['Chicago']
    )

#arrest_data比例依据：Chicago Police Department, 2021 Annual Report
arrest_data = {
    "District 1": {
        "gender": {"Female": 15.4, "Male": 84.6},
        "race": {
            "Black": 80.3,
            "White": 8.2,
            "Asian": 0.8,
            "others": 10.56  # 0.96 + 9.5 + 0.1
        }
    },
    "District 2": {
        "gender": {"Female": 19.0, "Male": 81.0},
        "race": {
            "Black": 93.8,
            "White": 2.2,
            "Asian": 0.16,
            "others": 3.68  # 0.4 + 3.2 + 0.08
        }
    },
    "District 3": {
        "gender": {"Female": 16.8, "Male": 83.2},
        "race": {
            "Black": 95.0,
            "White": 1.2,
            "Asian": 0.06,
            "others": 1.45  # 0.45 + 1.0 + 0.0
        }
    },
    "District 4": {
        "gender": {"Female": 16.3, "Male": 83.7},
        "race": {
            "Black": 85.7,
            "White": 2.6,
            "Asian": 0.06,
            "others": 10.9  # 0.6 + 10.3 + 0.0
        }
    },
    "District 5": {
        "gender": {"Female": 17.3, "Male": 82.7},
        "race": {
            "Black": 95.8,
            "White": 1.2,
            "Asian": 0.2,
            "others": 2.25  # 0.15 + 2.1 + 0.0
        }
    },
    "District 6": {
        "gender": {"Female": 16.5, "Male": 83.5},
        "race": {
            "Black": 97.0,
            "White": 1.0,
            "Asian": 0.08,
            "others": 1.32  # 0.28 + 1.1 + 0.04
        }
    },
    "District 7": {
        "gender": {"Female": 14.9, "Male": 85.1},
        "race": {
            "Black": 96.7,
            "White": 1.6,
            "Asian": 0.0,
            "others": 4.72  # 0.32 + 4.4 + 0.0
        }
    },
    "District 8": {
        "gender": {"Female": 13.3, "Male": 86.7},
        "race": {
            "Black": 47.7,
            "White": 8.8,
            "Asian": 0.3,
            "others": 43.01  # 0.86 + 42.1 + 0.05
        }
    },
    "District 9": {
        "gender": {"Female": 14.8, "Male": 85.2},
        "race": {
            "Black": 43.0,
            "White": 8.8,
            "Asian": 1.16,
            "others": 45.8  # 0.7 + 45.1 + 0.0
        }
    },
    "District 10": {
        "gender": {"Female": 12.0, "Male": 88.0},
        "race": {
            "Black": 67.3,
            "White": 2.8,
            "Asian": 0.09,
            "others": 29.67  # 0.53 + 29.1 + 0.04
        }
    },
    "District 11": {
        "gender": {"Female": 13.0, "Male": 87.0},
        "race": {
            "Black": 83.1,
            "White": 6.3,
            "Asian": 0.11,
            "others": 10.44  # 0.8 + 9.6 + 0.04
        }
    },
    "District 12": {
        "gender": {"Female": 14.9, "Male": 85.1},
        "race": {
            "Black": 62.5,
            "White": 10.7,
            "Asian": 1.54,
            "others": 25.0  # 0.8 + 24.2 + 0.0
        }
    },
    "District 14": {
        "gender": {"Female": 14.0, "Male": 86.0},
        "race": {
            "Black": 34.7,
            "White": 15.4,
            "Asian": 1.7,
            "others": 47.64  # 2.8 + 44.5 + 0.34
        }
    },
    "District 15": {
        "gender": {"Female": 13.6, "Male": 86.4},
        "race": {
            "Black": 91.2,
            "White": 1.4,
            "Asian": 0.05,
            "others": 5.82  # 0.27 + 5.5 + 0.05
        }
    },
    "District 16": {
        "gender": {"Female": 15.6, "Male": 84.4},
        "race": {
            "Black": 28.2,
            "White": 35.8,
            "Asian": 2.0,
            "others": 33.2  # 1.0 + 31.9 + 0.3
        }
    },
    "District 17": {
        "gender": {"Female": 13.7, "Male": 86.3},
        "race": {
            "Black": 20.0,
            "White": 24.7,
            "Asian": 3.9,
            "others": 50.8  # 1.1 + 49.7 + 0.0
        }
    },
    "District 18": {
        "gender": {"Female": 15.5, "Male": 84.5},
        "race": {
            "Black": 73.9,
            "White": 14.7,
            "Asian": 2.0,
            "others": 9.85  # 0.68 + 9.1 + 0.07
        }
    },
    "District 19": {
        "gender": {"Female": 14.2, "Male": 85.8},
        "race": {
            "Black": 49.4,
            "White": 25.3,
            "Asian": 3.9,
            "others": 20.87  # 0.88 + 19.9 + 0.09
        }
    },
    "District 20": {
        "gender": {"Female": 18.6, "Male": 81.4},
        "race": {
            "Black": 40.0,
            "White": 27.1,
            "Asian": 5.0,
            "others": 28.25  # 0.92 + 27.1 + 0.23
        }
    },
    "District 22": {
        "gender": {"Female": 13.6, "Male": 86.4},
        "race": {
            "Black": 94.6,
            "White": 4.8,
            "Asian": 0.18,
            "others": 1.68  # 0.58 + 1.1 + 0.0
        }
    },
    "District 24": {
        "gender": {"Female": 13.7, "Male": 86.3},
        "race": {
            "Black": 59.5,
            "White": 13.7,
            "Asian": 7.0,
            "others": 19.4  # 1.05 + 18.0 + 0.35
        }
    },
    "District 25": {
        "gender": {"Female": 15.6, "Male": 84.4},
        "race": {
            "Black": 39.6,
            "White": 7.9,
            "Asian": 0.28,
            "others": 50.74  # 2.6 + 48.6 + 0.14
        }
    }
}

def generate_agents(arrest_data, district_agent_counts):
    agents = []
    for district, data in arrest_data.items():
        N = district_agent_counts.get(district, 0)  
        for _ in range(N):
            gender = random.choices(
                population=list(data["gender"].keys()),
                weights=list(data["gender"].values()),
                k=1
            )[0]
            race = random.choices(
                population=list(data["race"].keys()),
                weights=list(data["race"].values()),
                k=1
            )[0]
            residence_file = f"./agent_initialization/district/district{district.split()[-1]}.csv"
            with open(residence_file, "r") as csvfile:
                reader = csv.reader(csvfile)
                residences = [row[0] for row in reader]
                while True:
                    residence = random.choice(residences)
                    if residence in map.aois.keys():
                        print(f"Residence {residence} found")
                        break
                    else:
                        print(f"Residence {residence} not found in map.aois.keys()")
                        residences.remove(residence)
                
            agents.append({"district": district, "gender": gender, "race": race, "residence": residence})
    return agents

district_agent_counts = {
    "District 1": 53,
    "District 2": 33,
    "District 3": 41,
    "District 4": 44,
    "District 5": 50,
    "District 6": 68,
    "District 7": 64,
    "District 8": 51,
    "District 9": 43,
    "District 10": 60,
    "District 11": 140,
    "District 12": 36,
    "District 14": 24,
    "District 15": 48,
    "District 16": 35,
    "District 17": 17,
    "District 18": 39,
    "District 19": 30,
    "District 20": 12,
    "District 22": 33,
    "District 24": 23,
    "District 25": 56
}

agents = generate_agents(arrest_data, district_agent_counts)

with open("agent_initialization/HRIs.json", "w") as f:
    json.dump(agents, f, indent=4)
    # Calculate total gender and race distribution
    total_gender = {"Female": 0, "Male": 0}
    total_race = {"Black": 0, "White": 0, "Asian": 0, "others": 0}

    for agent in agents:
        total_gender[agent["gender"]] += 1
        total_race[agent["race"]] += 1

    print("Total Gender Distribution:", total_gender)
    print("Total Race Distribution:", total_race)