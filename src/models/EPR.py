import random
from datetime import datetime, timedelta
import powerlaw
from typing import List, Dict, Any, Tuple
from src.environment.map import Map
from src.agents import resident
import pyproj

class EPRModel:
    """基于CBG的EPR移动模型类"""
    
    def __init__(self):
        # EPR模型参数
        self.rho = 0.6    # 探索新位置的倾向
        self.gamma = 0.21 # 探索意愿随访问地点数量的衰减系数
        self.beta = 0.8   # 等待时间分布的幂律指数
        self.alpha = 0.55 # 距离分布的幂律指数
        

    def generate_new_loc(
        self, 
        resident,
        aois: List[str],
        start_place: str,
        map: Map,
        current_step: int
    ) -> str:
        """
        生成下一个CBG位置
        
        Args:
            resident: Agent对象
            aois: 可访问的CBG ID列表
            start_place: 起始CBG ID
            map: 地图对象
            current_step: 当前步数
            
        Returns:
            str: end（目标CBG）
        """
        # 如果已经有下一步计划，直接返回
        param = [self.rho, self.gamma, self.beta]
        
        # 使用EPR模型生成轨迹
        visit_history = resident.get_visited_locations()
        S = len(visit_history)  # 已访问的不同位置数量
        
        # 决定是探索新位置还是返回已访问位置
        pro_explore = self.rho * (S ** (-self.gamma))
        
        if random.random() < pro_explore or S <= 1:
            # 探索新位置
            current_cbg = map.get_aoi(str(start_place))
            if not current_cbg:
                return start_place                   
            # 获取当前CBG的质心
            current_centroid = current_cbg['shapely_xy'].centroid
            # 计算到其他CBG的距离并根据距离加权选择
            unexplored_cbgs = [cbg for cbg in aois if cbg not in visit_history]
            if not unexplored_cbgs:
                unexplored_cbgs = aois  # 如果所有CBG都访问过，允许重复访问
            if current_centroid.is_empty:
                return random.choice(unexplored_cbgs)
            distances = []
            sampled_cbg = random.sample(unexplored_cbgs, min(100, len(unexplored_cbgs)))
            for cbg_id in sampled_cbg:
                target_cbg = map.get_aoi(cbg_id)
                if target_cbg:
                    target_centroid = target_cbg['shapely_xy'].centroid
                    
                    if target_centroid.is_empty:
                        continue
                    distance = ((current_centroid.x-target_centroid.x)**2 + (current_centroid.y-target_centroid.y)**2)**0.5
                    distances.append((distance, cbg_id))
             
            # 根据距离计算权重
            epsilon = 0.0001  # 避免除零
            weights = [(d[0] + epsilon) ** (-self.alpha - 1) for d in distances]
            new_location = random.choices([d[1] for d in distances], weights=weights, k=1)[0]
        else:
            # 返回已访问位置
            visit_counts = list(visit_history.values())
            prob_weights = [p / sum(visit_counts) for p in visit_counts]
            new_location = random.choices(list(visit_history.keys()), weights=prob_weights, k=1)[0]
        
        return new_location