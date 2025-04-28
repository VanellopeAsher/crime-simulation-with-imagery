from datetime import datetime, timedelta
import random
from typing import List, Dict, Any, Optional
from .resident import ResidentAgent

class CriminalAgent(ResidentAgent):
    """犯罪者Agent类，继承自ResidentAgent"""
    
    def __init__(
        self,
        agent_id: str,
        gender: str,
        race: str,
        residence: str,
        criminal_record: List[tuple],
        current_location: Optional[str] = None,
        historical_trajectory: Optional[List[tuple]] = None,
        visited_locations: Optional[Dict[str, int]] = None,
    ):
        """
        初始化犯罪者Agent
        
        Args:
            agent_id: 唯一标识符
            gender: 性别 (M/F/O)
            race: 种族
            residence: 居住地AOI ID
            criminal_record: 犯罪记录列表，每个记录是(step, location)的元组
        """
        super().__init__(
            agent_id=agent_id,
            gender=gender,
            race=race,
            residence=residence,
            current_location=current_location,
            historical_trajectory=historical_trajectory,
            visited_locations=visited_locations,
            income_level=0
        )
        self.criminal_record = criminal_record
    
    def add_criminal_record(self, step: int, location: str
                            ) -> None:
        """
        添加犯罪记录
        
        Args:
            step: 犯罪步数
            location: 犯罪地点
        """
        self.criminal_record.append((step, location))
            
    def get_criminal_record(self) -> List[tuple]:
        """获取犯罪记录"""
        return self.criminal_record
    
    def get_attributes(self) -> Dict[str, Any]:
        """获取Agent的所有属性"""
        attributes = super().get_attributes()
        attributes.update({
            'criminal_record': self.criminal_record,
        })
        return attributes