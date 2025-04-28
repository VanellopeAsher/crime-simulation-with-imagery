from typing import Dict, List, Any
import os
import sys
import datetime
import logging  # 新增日志模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.utils import LLM
import random
import time
import pickle
import json
from models.prompt_safety import build_prompt 
from src.environment.map import Map
from constant import MAP_SCOPE, MAP_DATA_PATH

class CrimeDecisionModel:
    """犯罪决策模型类"""
    
    def __init__(self, llm: LLM):
        """
        初始化犯罪决策模型
        
        Args:
            llm: LLM实例
        """
        self.llm = llm
        
        # 初始化日志配置
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        
        # 创建文件handler
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = f'logs/crime_decisions_{timestamp}.log'
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # 创建控制台handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 定义日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 添加handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # 加载数据文件
        with open('cache/cbg_attributes.pkl', 'rb') as f:
            self.cbg_attributes = pickle.load(f)
        with open('cache/crime_rate.pkl', 'rb') as f:
            self.crime_rate = pickle.load(f)
        self.map = Map(
            data_cache=MAP_DATA_PATH,
            map_scope=MAP_SCOPE['Chicago']
        )

    def _log_decision_context(self, criminal: Dict):
        """记录决策上下文信息"""
        context_msg = [
            f"Agent Profile [ID:{criminal['agent_id']}]",
            f"Current Location: {criminal['current_location']}",
            f"Criminal Record: {criminal['criminal_record']}",
            "--- Context End ---"
        ]
        self.logger.debug('\n'.join(context_msg))
    def make_decision(
        self,
        criminal: Dict[str, Any],
        potential_targets: List[Dict[str, Any]],
        police_count: int
    ) -> Dict[str, Any]:
        """
        基于当前状态做出犯罪决策
        
        Args:
            criminal: 犯罪者属性
            potential_targets: 潜在目标列表，每个目标包含其所在CBG的属性
            police_count: 附近警察数量
            
        Returns:
            Dict[str, Any]: 决策结果
        """
        self.logger.info(f"Start decision process for agent {criminal['agent_id']}")
        self._log_decision_context(criminal)
        # 如果没有潜在目标，直接返回不犯罪
        if not potential_targets:
            print("No potential target")
            return {
                'status': False,
                'objective_id': None,
                'reasoning': "No potential targets in the area",
            }
        target_str = "- Number: {}\n     - Attribute Matrix: [\n".format(len(potential_targets))
        for target in potential_targets:
            target_str += "  {{Target ID: {}, Gender: {}, Race: {}, Income Level: {}}},\n".format(
                target['agent_id'],
                target['gender'],
                target['race'],
                target['income_level']
            )
        target_str += "]"
        
        # PROMPT部分
        # 3.LLM组：无cbg_attributes
        # 4.static组：无environmental safety score和current CBG description
        # 5.description组：无environmental safety score
        # 6. safety组：完整prompt
        
        crime_rate = self.crime_rate[criminal['current_location']]   
        cbg = self.map.aois.get(criminal['current_location'], None)
        environment = self.cbg_attributes.get(criminal['current_location'], None)
        # 构建决策提示
        prompt = build_prompt(criminal, crime_rate, cbg, environment, target_str, police_count)
        while True:
            try:
                self.logger.debug(f"Generated prompt:\n{prompt}")
                response = self.llm.generate(prompt) 
                self.logger.debug(f"Raw LLM response:\n{response}")
                try:
                    import json
                    response = json.loads(response)
                    if isinstance(response, dict):
                        status = response.get('Status', response.get('status', 'Undefined'))
                        objective_id = response.get('Objective ID', response.get('objective_id', 'None'))
                        reasoning = response.get('Reasoning', response.get('reasoning', 'No reasoning provided'))
                                               
                        print(status)
                        return {
                            'status': status, 
                            'objective_id': objective_id,
                            'reasoning': reasoning,
                        }
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error: {str(e)}, Response text: {response}")
            except Exception as e:
                print(f"LLM error: {str(e)}")
                time.sleep(random.uniform(5, 10))

                continue