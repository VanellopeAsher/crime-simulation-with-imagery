import csv
import json
import random
import time
import sys
import os
from tqdm import tqdm  # Import tqdm for progress bars
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path
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

def load_police_stations():
    try:
        station_file = "./cache/Police_Stations.csv"
        with open(station_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            next(reader)  # Skip header if needed
            data = [(row['DISTRICT'], row["LATITUDE"], row['LONGITUDE'], row['PERSON']) 
                   for row in tqdm(reader, desc="Loading police stations")]
            
        # 保存为JSON文件
        output_file = Path("agent_initialization") / "police_stations.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        return data
    except FileNotFoundError as e:
        print(f"Error: Could not find file {e.filename}")
        raise
    except csv.Error as e:
        print(f"Error reading CSV file: {str(e)}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error writing JSON file: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise

def initialize_police_agents(police_stations, num_agents=500):
    try:
        # 构建name到（latitude, longitude）的字典
        name = []
        latitude = []
        longitude = []
        personnel = []
        
        for police_station in tqdm(police_stations, desc="Processing police stations"):
            name.append(police_station[0])
            latitude.append(float(police_station[1]))
            longitude.append(float(police_station[2]))
            personnel.append(int(police_station[3]))

        name_to_coordinates = dict(zip(name, zip(latitude, longitude)))
        
        # 按personnel比例分配警察
        total_personnel = sum(personnel)
        name_probabilities = [p / total_personnel for p in personnel]
        assigned_names = random.choices(name, weights=name_probabilities, k=num_agents)
        
        # 生成警察agent数据
        police_agents = []
        for i, name in enumerate(tqdm(assigned_names, desc="Generating police agents")):
            agent_id = f"police_{i}"
            latitude, longitude = name_to_coordinates[name]
            police_agents.append({
                "agent_id": agent_id,
                "district": name,
                "residence": map.get_cbg(latitude, longitude)
            })
        
        # 保存结果
        output_file = Path("agent_initialization") / "police_agents.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(police_agents, f, ensure_ascii=False, indent=4)
            
        return police_agents
    except ValueError as e:
        print(f"Error converting data types: {str(e)}")
        raise
    except Exception as e:
        print(f"Error generating police agents: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        police_stations = load_police_stations()
        time.sleep(1)  # Wait for file operations to complete
        initialize_police_agents(police_stations)
    except Exception as e:
        print(f"Failed to initialize police agents: {str(e)}")
        raise