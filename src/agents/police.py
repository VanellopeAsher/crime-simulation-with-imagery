from datetime import datetime, time
from typing import List, Dict, Any, Optional
import random

class PoliceAgent:
    """警察Agent类"""
    
    def __init__(
        self,
        agent_id: str,
        station_district: str,
        police_station: str
    ):
        """
        初始化警察Agent
        
        Args:
            agent_id: 唯一标识符
            police_station: 警察局AOI ID
            patrol_route: 巡逻路线AOI ID列表
        """
        self.agent_id = agent_id
        self.police_station = police_station
        self.station_district = station_district
        
        # 动态属性
        self.current_location = police_station
        self.crimes_responded = 0
        self.crimes_prevented = 0
        
    def update_location(self, new_location: str) -> None:
        """
        更新警察位置
        
        Args:
            new_location: 新的位置AOI ID
        """
        self.current_location = new_location
        
    def get_current_location(self) -> str:
        """获取当前位置"""
        return self.current_location

    def get_statistics(self) -> Dict[str, int]:
        """获取统计信息"""
        return {
            'crimes_responded': self.crimes_responded,
            'crimes_prevented': self.crimes_prevented,
            'response_rate': self.crimes_prevented / max(1, self.crimes_responded)
        }
    
    def get_attributes(self) -> Dict[str, Any]:
        """获取Agent的所有属性"""
        return {
            'agent_id': self.agent_id,
            'police_station': self.police_station,
            'current_location': self.current_location,
            'statistics': self.get_statistics()
        }