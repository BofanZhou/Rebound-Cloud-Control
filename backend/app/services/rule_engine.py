"""
规则推荐引擎
基于材质、壁厚等参数计算推荐补偿值
（第一阶段使用规则引擎，后续可替换为 ML 模型）
"""
from typing import Dict, Any
from datetime import datetime


class RuleEngine:
    """
    基于规则的回弹补偿推荐引擎
    
    规则说明：
    - 普通钢：基础补偿 +2.0°
    - 高强钢：基础补偿 +3.0°
    - 不锈钢：基础补偿 +2.5°
    - 铝合金：基础补偿 +1.5°
    
    壁厚修正：
    - 壁厚 > 10mm：补偿 -0.5°（厚壁回弹小）
    - 壁厚 < 3mm：补偿 +0.5°（薄壁回弹大）
    
    管径修正：
    - 管径 > 200mm：补偿 -0.3°（大管径回弹小）
    """
    
    # 材质基础补偿值映射
    MATERIAL_BASE_OFFSET: Dict[str, float] = {
        "普通钢": 2.0,
        "高强钢": 3.0,
        "不锈钢": 2.5,
        "铝合金": 1.5,
    }
    
    # 默认材质补偿（未知材质）
    DEFAULT_OFFSET = 2.0
    
    @classmethod
    def calculate_recommendation(
        cls,
        diameter: float,
        thickness: float,
        material: str,
        target_angle: float
    ) -> Dict[str, Any]:
        """
        计算推荐参数
        
        Args:
            diameter: 管径 (mm)
            thickness: 壁厚 (mm)
            material: 材质
            target_angle: 目标角度 (度)
            
        Returns:
            包含推荐角度、补偿值和说明的字典
        """
        # 1. 获取材质基础补偿
        base_offset = cls.MATERIAL_BASE_OFFSET.get(material, cls.DEFAULT_OFFSET)
        
        # 2. 壁厚修正
        thickness_adjustment = 0.0
        if thickness > 10:
            thickness_adjustment = -0.5
        elif thickness < 3:
            thickness_adjustment = 0.5
        
        # 3. 管径修正
        diameter_adjustment = 0.0
        if diameter > 200:
            diameter_adjustment = -0.3
        
        # 4. 计算总补偿值
        total_offset = base_offset + thickness_adjustment + diameter_adjustment
        
        # 5. 计算推荐角度（目标角度 + 补偿值）
        recommended_angle = target_angle + total_offset
        
        # 6. 生成说明
        explanation = cls._generate_explanation(
            material, base_offset, 
            thickness, thickness_adjustment,
            diameter, diameter_adjustment,
            total_offset
        )
        
        return {
            "recommended_angle": round(recommended_angle, 2),
            "recommended_offset": round(total_offset, 2),
            "explanation": explanation,
            "timestamp": datetime.now().isoformat(),
        }
    
    @classmethod
    def _generate_explanation(
        cls,
        material: str,
        base_offset: float,
        thickness: float,
        thickness_adj: float,
        diameter: float,
        diameter_adj: float,
        total_offset: float
    ) -> str:
        """生成推荐说明文字"""
        parts = [f"基于{material}材质，基础补偿值为+{base_offset}°"]
        
        if thickness_adj != 0:
            adj_text = "增加" if thickness_adj > 0 else "减少"
            parts.append(f"壁厚{thickness}mm，{adj_text}补偿{abs(thickness_adj)}°")
        
        if diameter_adj != 0:
            parts.append(f"管径{diameter}mm较大，减少补偿{abs(diameter_adj)}°")
        
        parts.append(f"综合补偿值为{total_offset:+.2f}°")
        
        return "。".join(parts)
