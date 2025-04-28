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

total_population = 3046946
citizen_num = 8760
p = 0

# 初始化全局容器
all_agents = pd.DataFrame()

# 添加小量防止除零
EPSILON = 1e-8

for i in range(len(list(map.aois.keys()))):
    # 当前AOI数据提取
    aoi_key = list(map.aois.keys())[i]
    aoi_data = map.aois[aoi_key]['data'].iloc[0]
    
    # 计算当前AOI的Agent数量
    N = int((aoi_data['Total population'] / total_population) * citizen_num)
    print(f"AOI: {aoi_key}, Population: {N}")
    if N <= 0:  # 跳过没有Agent的区域
        continue
    p += N

    # ----------------------------------
    # 性别分布（强制归一化）
    # ----------------------------------
    female_ratio = aoi_data['female_ratio']
    male_ratio = 1 - female_ratio
    # 处理浮点误差
    gender_probs = np.array([female_ratio, male_ratio])
    gender_probs = np.clip(gender_probs, 0, 1)  # 保证概率在[0,1]之间
    gender_probs /= (gender_probs.sum() + EPSILON)
    GENDER_DIST = {
        'Female': gender_probs[0],
        'Male': gender_probs[1]
    }

    # ----------------------------------
    # 种族分布（强制归一化+防止负数）
    # ----------------------------------
    white = aoi_data['white_ratio']
    asian = aoi_data['asian_ratio']
    black = aoi_data['black_ratio']
    others = max(0.0, 1 - white - asian - black)  # 防止负数
    
    race_probs = np.array([white, asian, black, others])
    race_probs = np.clip(race_probs, 0, 1)  # 保证概率在[0,1]之间
    race_probs /= (race_probs.sum() + EPSILON)  # 归一化
    RACE_DIST = {
        'White': race_probs[0],
        'Asian': race_probs[1],
        'Black': race_probs[2],
        'Others': race_probs[3]
    }

    INCOME_DIST = {
        'Low': 0.2,
        'Lower_Middle': 0.3,
        'Middle': 0.35,
        'Upper_Middle': 0.12,
        'High': 0.03
    }

    # ----------------------------------
    # 年龄组分布（注释保持原样）
    # ----------------------------------
    '''
    young = aoi_data['population_young_ratio']
    middle = aoi_data['population_middle_ratio']
    old = aoi_data['population_old_ratio']
    
    age_probs = np.array([young, middle, old])
    age_probs = np.clip(age_probs, 0, 1)
    age_probs /= (age_probs.sum() + EPSILON)
    AGE_DIST = {
        '<30': age_probs[0],
        '30-50': age_probs[1],
        '≥50': age_probs[2]
    }'''

    # ----------------------------------
    # 其余参数保持不变
    # ----------------------------------
    UNEMPLOYMENT_RATE = aoi_data['unemployed_ratio']
    COMMUTE_MEAN = aoi_data['average_commuting_time']
    COMMUTE_STD = 3
    COMMUTE_MIN = 5
    COMMUTE_MAX = 60

    def generate_agents(num_agents):
        # 保持原有生成逻辑不变
        genders = np.random.choice(
            list(GENDER_DIST.keys()), 
            num_agents, 
            p=list(GENDER_DIST.values())
        )
        
        races = np.random.choice(
            list(RACE_DIST.keys()), 
            num_agents, 
            p=list(RACE_DIST.values())
        )
        
        residence = np.random.choice(
            [aoi_key],
            num_agents
        )
        
        incomes = np.random.choice(
            list(INCOME_DIST.keys()),
            num_agents,
            p=list(INCOME_DIST.values())
        )

        return pd.DataFrame({
            "gender": genders,
            "race": races,
            "residence": residence,
            "income_level": incomes
        })

    # 生成并合并数据
    agents_df = generate_agents(N)
    all_agents = pd.concat([all_agents, agents_df], ignore_index=True)

all_agents.to_json("agent_initialization/citizens.json", orient="records", indent=2)
print(f"Total agents generated: {len(all_agents)}")