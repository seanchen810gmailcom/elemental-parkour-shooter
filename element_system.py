######################載入套件######################
from config import *

######################屬性剋制系統######################


class ElementSystem:
    """
    元素屬性剋制系統 - 管理所有屬性相關的計算和效果\n
    \n
    負責：\n
    1. 計算屬性剋制傷害\n
    2. 管理狀態效果應用\n
    3. 提供屬性相關的視覺效果\n
    4. 平衡性調整和數值計算\n
    """

    # 屬性剋制關係表
    WEAKNESS_MAP = {
        # 攻擊者屬性: [被剋制的目標屬性列表]
        "water": ["lava_monster"],
        "thunder": ["water_monster"],
        "fire": ["water_monster"],
        "ice": ["tornado_monster"],  # 冰對風怪的減速效果特別強
    }

    # 抗性關係表
    RESISTANCE_MAP = {
        # 攻擊者屬性: [有抗性的目標屬性列表]
        "fire": ["lava_monster"]  # 火攻擊對岩漿怪有抗性
    }

    # 狀態效果觸發條件
    STATUS_EFFECT_MAP = {
        "ice": {
            "effect_type": "slow",
            "base_duration": SLOW_EFFECT_DURATION,
            "base_intensity": 0.5,
            "enhanced_targets": ["tornado_monster"],  # 對這些目標效果更強
            "enhanced_intensity": 0.8,
            "enhanced_duration_multiplier": 1.5,
        },
        "thunder": {
            "effect_type": "paralysis",
            "base_duration": PARALYSIS_EFFECT_DURATION,
            "base_intensity": 1.0,
            "enhanced_targets": ["water_monster"],
            "enhanced_intensity": 1.0,
            "enhanced_duration_multiplier": 1.2,
        },
    }

    @staticmethod
    def calculate_damage(base_damage, attacker_element, target_type):
        """
        計算考慮屬性剋制後的最終傷害\n
        \n
        參數:\n
        base_damage (int): 基礎傷害值\n
        attacker_element (str): 攻擊者的元素屬性\n
        target_type (str): 目標的怪物類型\n
        \n
        回傳:\n
        int: 最終傷害值\n
        """
        final_damage = base_damage

        # 檢查弱點攻擊
        if (
            attacker_element in ElementSystem.WEAKNESS_MAP
            and target_type in ElementSystem.WEAKNESS_MAP[attacker_element]
        ):
            final_damage = int(final_damage * WEAKNESS_MULTIPLIER)

        # 檢查抗性攻擊
        elif (
            attacker_element in ElementSystem.RESISTANCE_MAP
            and target_type in ElementSystem.RESISTANCE_MAP[attacker_element]
        ):
            final_damage = int(final_damage * RESISTANCE_MULTIPLIER)

        # 火屬性對水怪的額外傷害（不算弱點但有bonus）
        elif attacker_element == "fire" and target_type == "water_monster":
            final_damage = int(final_damage * 1.5)

        return max(1, final_damage)  # 確保至少造成1點傷害

    @staticmethod
    def get_status_effect(attacker_element, target_type):
        """
        獲取應該施加的狀態效果\n
        \n
        參數:\n
        attacker_element (str): 攻擊者的元素屬性\n
        target_type (str): 目標的怪物類型\n
        \n
        回傳:\n
        dict or None: 狀態效果資訊，沒有效果時回傳 None\n
        """
        if attacker_element not in ElementSystem.STATUS_EFFECT_MAP:
            return None

        effect_config = ElementSystem.STATUS_EFFECT_MAP[attacker_element]

        # 計算效果強度和持續時間
        duration = effect_config["base_duration"]
        intensity = effect_config["base_intensity"]

        # 檢查是否對特定目標有增強效果
        if target_type in effect_config.get("enhanced_targets", []):
            intensity = effect_config["enhanced_intensity"]
            duration *= effect_config["enhanced_duration_multiplier"]

        return {
            "type": effect_config["effect_type"],
            "duration": duration,
            "intensity": intensity,
        }

    @staticmethod
    def get_damage_type_description(attacker_element, target_type):
        """
        獲取傷害類型的描述文字\n
        \n
        參數:\n
        attacker_element (str): 攻擊者的元素屬性\n
        target_type (str): 目標的怪物類型\n
        \n
        回傳:\n
        str: 傷害類型描述\n
        """
        if (
            attacker_element in ElementSystem.WEAKNESS_MAP
            and target_type in ElementSystem.WEAKNESS_MAP[attacker_element]
        ):
            return "弱點攻擊!"

        elif (
            attacker_element in ElementSystem.RESISTANCE_MAP
            and target_type in ElementSystem.RESISTANCE_MAP[attacker_element]
        ):
            return "抗性傷害"

        elif attacker_element == "fire" and target_type == "water_monster":
            return "額外傷害"

        else:
            return "普通傷害"

    @staticmethod
    def get_element_color(element_type):
        """
        獲取元素對應的顏色\n
        \n
        參數:\n
        element_type (str): 元素類型\n
        \n
        回傳:\n
        tuple: RGB 顏色值\n
        """
        color_map = {
            "water": WATER_BULLET_COLOR,
            "ice": ICE_BULLET_COLOR,
            "thunder": THUNDER_BULLET_COLOR,
            "fire": FIRE_BULLET_COLOR,
        }
        return color_map.get(element_type, WHITE)

    @staticmethod
    def get_element_name(element_type):
        """
        獲取元素的中文名稱\n
        \n
        參數:\n
        element_type (str): 元素類型\n
        \n
        回傳:\n
        str: 中文名稱\n
        """
        name_map = {"water": "水", "ice": "冰", "thunder": "雷", "fire": "火"}
        return name_map.get(element_type, "未知")

    @staticmethod
    def get_monster_weakness(monster_type):
        """
        獲取怪物的弱點屬性\n
        \n
        參數:\n
        monster_type (str): 怪物類型\n
        \n
        回傳:\n
        list: 對該怪物有效的屬性列表\n
        """
        weaknesses = []

        for element, targets in ElementSystem.WEAKNESS_MAP.items():
            if monster_type in targets:
                weaknesses.append(element)

        return weaknesses

    @staticmethod
    def get_monster_resistance(monster_type):
        """
        獲取怪物的抗性屬性\n
        \n
        參數:\n
        monster_type (str): 怪物類型\n
        \n
        回傳:\n
        list: 該怪物抗性的屬性列表\n
        """
        resistances = []

        for element, targets in ElementSystem.RESISTANCE_MAP.items():
            if monster_type in targets:
                resistances.append(element)

        return resistances

    @staticmethod
    def get_effectiveness_rating(attacker_element, target_type):
        """
        獲取攻擊效果等級\n
        \n
        參數:\n
        attacker_element (str): 攻擊者的元素屬性\n
        target_type (str): 目標的怪物類型\n
        \n
        回傳:\n
        int: 效果等級 (0: 抗性, 1: 普通, 2: 有效, 3: 弱點)\n
        """
        if (
            attacker_element in ElementSystem.WEAKNESS_MAP
            and target_type in ElementSystem.WEAKNESS_MAP[attacker_element]
        ):
            return 3  # 弱點攻擊

        elif (
            attacker_element in ElementSystem.RESISTANCE_MAP
            and target_type in ElementSystem.RESISTANCE_MAP[attacker_element]
        ):
            return 0  # 抗性

        elif attacker_element == "fire" and target_type == "water_monster":
            return 2  # 有效

        else:
            return 1  # 普通

    @staticmethod
    def create_damage_popup_info(base_damage, attacker_element, target_type):
        """
        創建傷害數字顯示的資訊\n
        \n
        參數:\n
        base_damage (int): 基礎傷害值\n
        attacker_element (str): 攻擊者的元素屬性\n
        target_type (str): 目標的怪物類型\n
        \n
        回傳:\n
        dict: 傷害顯示資訊\n
        """
        final_damage = ElementSystem.calculate_damage(
            base_damage, attacker_element, target_type
        )
        effectiveness = ElementSystem.get_effectiveness_rating(
            attacker_element, target_type
        )

        # 根據效果等級決定顯示顏色和大小
        if effectiveness == 3:  # 弱點攻擊
            color = YELLOW
            size_multiplier = 1.5
        elif effectiveness == 2:  # 有效攻擊
            color = GREEN
            size_multiplier = 1.2
        elif effectiveness == 0:  # 抗性攻擊
            color = GRAY
            size_multiplier = 0.8
        else:  # 普通攻擊
            color = WHITE
            size_multiplier = 1.0

        return {
            "damage": final_damage,
            "color": color,
            "size_multiplier": size_multiplier,
            "description": ElementSystem.get_damage_type_description(
                attacker_element, target_type
            ),
        }
