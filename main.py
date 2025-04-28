import os
import shutil
import yaml
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import numpy as np
from tqdm import tqdm
from shapely.geometry import box
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from src.environment.map import Map
from src.models.EPR import EPRModel
from src.models.crime import CrimeDecisionModel
from utils.utils import LLM
from src.agents.resident import ResidentAgent
from src.agents.criminal import CriminalAgent
from src.agents.police import PoliceAgent
from constant import MAP_SCOPE, MAP_DATA_PATH
import csv
RESULTS_P = f"results_safety_{datetime.now().strftime('%Y%m%d')}/"

class CrimeSimulation:
    """犯罪模拟类"""
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化犯罪模拟"""
        try:
            # 加载配置
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)

            self.map = Map(
                data_cache=MAP_DATA_PATH,
                map_scope=MAP_SCOPE[self.config['environment']['city']]
            )
            self.continual = True

            # 使用pathlib处理路径
            district_path = 'agent_initialization/district'
            dic = {}
            for i in range(1, 26):
                district_file = district_path + f'/district{i}.csv'
                district_file = Path(district_file)
                if district_file.exists():
                    with open(district_file, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        dic[i] = [row[0] for row in reader]
            self.districts = dic

            # 初始化模型
            self.epr_model = EPRModel()
            self.llm = LLM(model_name=self.config['llm']['model_name'], platform=self.config['llm']['platform'], api_key=self.config['llm']['api_key'])
            self.crime_model = CrimeDecisionModel(self.llm)
            
            # 初始化Agent列表
            self.residents = []
            self.criminals = []
            self.police = []
            
            # 初始化犯罪记录
            self.crime_records = []
            self.last_crime_steps = {}  # 记录每个犯罪者最后一次犯罪的步数
            
            # 初始化步数参数
            self.total_steps = self.config['simulation']['total_steps']
            self.current_step = 0
            
            # 添加线程锁
            self.residents_lock = threading.Lock()
            self.criminals_lock = threading.Lock()
            self.police_lock = threading.Lock()
            self.crime_records_lock = threading.Lock()
            
            # 创建轨迹保存目录
            results_path = Path(RESULTS_P)
            results_path.mkdir(exist_ok=True)
            (results_path / 'trajectories').mkdir(exist_ok=True)

        except FileNotFoundError as e:
            print(f"Error: Required file not found: {e.filename}")
            raise
        except yaml.YAMLError as e:
            print(f"Error reading config file: {str(e)}")
            raise
        except Exception as e:
            print(f"Initialization error: {str(e)}")
            raise

    def initialize_agents(self):
        """初始化所有Agent"""
        # 创建市民
        with open("./agent_initialization/citizens.json", "r", encoding="utf-8") as f:
            citizens_data = json.load(f)
        i=0
        for citizen_data in citizens_data:
            agent_id = 'R' + str(i)
            resident = ResidentAgent(
                agent_id=agent_id,
                gender=citizen_data["gender"],
                race=citizen_data["race"],
                residence=str(citizen_data["residence"]),
                income_level=citizen_data["income_level"],
                current_location=str(citizen_data["residence"]),
                historical_trajectory=[(0, str(citizen_data["residence"]))],
                visited_locations={str(citizen_data["residence"]): 1}
            )
            self.residents.append(resident)
            i += 1
            
        # 创建犯罪者
        with open(f"./agent_initialization/HRIs.json", "r", encoding="utf-8") as f:
            criminals_data = json.load(f)
        i=0
        for criminal_data in criminals_data:
            agent_id = 'C' + str(i)
            criminal = CriminalAgent(
                agent_id=agent_id,
                gender=criminal_data["gender"],
                race=criminal_data["race"],
                residence=str(criminal_data["residence"]),
                criminal_record=[(-1, str(criminal_data['residence']))],
                current_location=str(criminal_data["residence"]),
                historical_trajectory=[(0, str(criminal_data["residence"]))],
                visited_locations={str(criminal_data["residence"]): 1}
            )
            self.criminals.append(criminal)
            i += 1
            
        # 创建警察
        i=0
        with open("./agent_initialization/police_agents.json", "r", encoding="utf-8") as f:
            police_data = json.load(f)
        for police_data in police_data:
            agent_id = 'P' + str(i)
            police = PoliceAgent(
                agent_id=agent_id,
                station_district=police_data["district"],
                police_station=police_data["residence"]
            )
            self.police.append(police)
            i += 1

    def _update_agent_locations(self):
        """更新所有Agent的位置"""
        def update_resident(resident):
            new_loc = self.epr_model.generate_new_loc(
                resident=resident,
                aois=list(self.map.aois.keys()),
                start_place=resident.current_location,
                map=self.map,
                current_step=self.current_step
            )
            resident.current_location = new_loc
            resident.visited_locations[new_loc] = resident.visited_locations.get(new_loc, 0) + 1
            resident.historical_trajectory.append((len(resident.historical_trajectory),new_loc))

        def update_criminal(criminal):
            new_loc = self.epr_model.generate_new_loc(
                resident=criminal,
                aois=list(self.map.aois.keys()),
                start_place=criminal.residence,
                map=self.map,
                current_step=self.current_step
            )
            criminal.current_location = new_loc
            criminal.visited_locations[new_loc] = criminal.visited_locations.get(new_loc, 0) + 1
            criminal.historical_trajectory.append((len(criminal.historical_trajectory),new_loc))

        def update_police(police):
            next_location = self.map.pois[str(random.choice(self.districts[int(police.station_district)]))]['poi_cbg']
            police.update_location(next_location)

        with ThreadPoolExecutor(max_workers=200) as executor:
            executor.map(update_resident, self.residents)
            executor.map(update_criminal, self.criminals)
            executor.map(update_police, self.police)

    def _check_crime_opportunity_multithreaded(self):
        """使用多线程检查犯罪机会"""
        def check_crime(criminal):
            self._check_crime_opportunity(criminal)

        with ThreadPoolExecutor(max_workers=200) as executor:
            executor.map(check_crime, self.criminals)

    def _check_crime_opportunity(self, criminal: CriminalAgent) -> bool:
        """检查是否有可能发生犯罪"""
        # await asyncio.gather(*[make_decision(criminal) for criminal in self.criminals])
        try:
            print(criminal.agent_id)   
            # 获取当前位置的潜在目标
            current_location = str(criminal.get_current_location())
            potential_targets = [
                resident for resident in self.residents
                if str(resident.get_current_location()) == current_location
            ]
            
            # 获取附近的警察数量
            nearby_police = [
                police for police in self.police
                if str(police.get_current_location()) == current_location
            ]
            if not potential_targets:
                print("No potential targets")
                return False
            
            try:
                criminal_attrs = criminal.get_attributes()
                target_attrs = [target.get_attributes() for target in potential_targets]
                print("making decisions......")
                decision = self.crime_model.make_decision(
                    criminal=criminal_attrs,
                    potential_targets=target_attrs,
                    police_count=len(nearby_police)
                )
                if isinstance(decision, dict) and decision.get('status', False):
                    with self.crime_records_lock:
                        self.crime_records.append({
                            'step': self.current_step,
                            'criminal_id': criminal.agent_id,
                            'location': current_location,
                            'target_id': decision.get('objective_id'),
                            'reasoning': decision.get('reasoning', 'No reasoning provided')
                        })
                        self.last_crime_steps[criminal.agent_id] = self.current_step
                    criminal.add_criminal_record(
                        step=self.current_step,
                        location=current_location
                    )
                    return True
                return False
                        
            except Exception as e:
                    print(f"Error in crime decision model for {criminal.agent_id}: {str(e)}")
                    return False
                
        except Exception as e:
            print(f"Error processing crime opportunity for {criminal.agent_id}: {str(e)}")
            return False

    def _record_positions(self):
        """记录所有Agent的当前位置并保存到对应step的文件中"""
        try:
            for c in self.criminals:
                trajectory_path = Path(RESULTS_P+'trajectories')
                trajectory_file = trajectory_path / f"{c.agent_id}.json"
                trajectory_path.mkdir(parents=True, exist_ok=True)
                data = c.historical_trajectory
                with open(trajectory_file, "w", encoding="utf-8") as f1:
                    json.dump(data, f1, ensure_ascii=False, indent=4)
                visited_path = Path(RESULTS_P+'visited')
                visited_file = visited_path / f"{c.agent_id}.json"
                visited_path.mkdir(parents=True, exist_ok=True)
                data = c.visited_locations
                with open(visited_file, "w", encoding="utf-8") as f2:
                    json.dump(data, f2, ensure_ascii=False, indent=4)
                
            for r in self.residents:
                trajectory_path = Path(RESULTS_P+'trajectories')
                trajectory_file = trajectory_path / f"{r.agent_id}.json"
                trajectory_path.mkdir(parents=True, exist_ok=True)
                data = r.historical_trajectory
                with open(trajectory_file, "w", encoding="utf-8") as f1:
                    json.dump(data, f1, ensure_ascii=False, indent=4)
                visited_path = Path(RESULTS_P+'visited')
                visited_file = visited_path / f"{r.agent_id}.json"
                visited_path.mkdir(parents=True, exist_ok=True)
                data = r.visited_locations
                with open(visited_file, "w", encoding="utf-8") as f2:
                    json.dump(data, f2, ensure_ascii=False, indent=4)

            for p in self.police:
                trajectory_path = Path(RESULTS_P+'trajectories')
                trajectory_file = trajectory_path / f"{p.agent_id}.json"
                trajectory_path.mkdir(parents=True, exist_ok=True)
                if not trajectory_file.exists():
                    with open(trajectory_file, "w", encoding="utf-8") as f:
                        json.dump([], f, ensure_ascii=False, indent=4)
                with open(trajectory_file, "r+", encoding="utf-8") as f:
                    data = json.load(f)
                    data.append(str(p.get_current_location()))
                    f.seek(0)
                    json.dump(data, f, ensure_ascii=False, indent=4)
                    f.truncate()
        except Exception as e:
            print(f"Error recording positions for step {self.current_step}: {str(e)}")
            raise

    def _save_crime_records(self, step=None):
        """保存所有犯罪记录到文件"""
        try:
            results_path = Path(RESULTS_P)
            
            # 保存总的犯罪记录
            with open(results_path / "crime_records.json", "w", encoding="utf-8") as f:
                json.dump(self.crime_records, f, ensure_ascii=False, indent=4)
                
            # 创建individual_records目录
            individual_records_path = results_path / "individual_records"
            individual_records_path.mkdir(exist_ok=True)
            
            # 按criminal分组并保存各自的记录
            criminal_records = {}
            for record in self.crime_records:
                criminal_id = record['criminal_id']
                if criminal_id not in criminal_records:
                    criminal_records[criminal_id] = []
                criminal_records[criminal_id].append({
                    'step': record['step'],
                    'location': record['location'],
                    'target_id': record['target_id'],
                    'reasoning': record['reasoning'],
                })
            
            # 保存每个criminal的记录到单独的文件
            for criminal_id, records in criminal_records.items():
                with open(individual_records_path / f"{criminal_id}_records.json", "w", encoding="utf-8") as f:
                    json.dump({
                        'total_crimes': len(records),
                        'records': records
                    }, f, ensure_ascii=False, indent=4)
                    
        except Exception as e:
            print(f"Error saving crime records: {str(e)}")
            raise

    def run_simulation(self):
        print("开始犯罪模拟...")
        
        # 初始化Agent
        self.initialize_agents()
        print("初始化Agent完成")
        
        # 运行模拟
        for step in tqdm(range(self.total_steps)):
            self.current_step = step
            # 更新Agent位置
            print("更新Agent位置...")
            self._update_agent_locations()
            
            # 记录当前位置
            self._record_positions()
            
            print("检查犯罪机会...")
            # 检查犯罪机会
            self._check_crime_opportunity_multithreaded()
            
            # 每个step结束后保存crime_records
            self._save_crime_records(step)
        
        # 最后保存完整的crime_records
        self._save_crime_records()
        
        print("模拟完成。可视化结果保存在results目录中")

if __name__ == "__main__":
    try:
        os.remove("llm_responses.txt")
        shutil.rmtree(RESULTS_P)
    except:
        pass
    # 创建结果目录    
    os.makedirs(RESULTS_P, exist_ok=True) 
    simulation = CrimeSimulation()
    simulation.run_simulation()