from tools.vision_tool import count_cars

'''
class VisionAgent:
    def __init__(self, lane_cfg):
        self.source = lane_cfg["source"]
        self.roi = lane_cfg.get("roi")

    def observe(self):
        return count_cars(self.source, self.roi)
'''

# VisionAgent with Emergency Detection
from tools.vision_tool import detect_vehicles

class VisionAgent:
    def __init__(self, lane_cfg):
        self.source = lane_cfg["source"]
        self.roi = lane_cfg.get("roi")

    def observe(self):
        result = detect_vehicles(self.source, self.roi)
        return {
            "counts": result["car_count"],
            "emergency": result["emergency_detected"]
        }
