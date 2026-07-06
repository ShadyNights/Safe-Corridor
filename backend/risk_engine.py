import numpy as np

import math

class RiskEngine:
    def __init__(self):
        self.risk_score = 0.0

        
        self.MAX_RISK = 100.0
        self.DECAY_RATE = 0.5
        
        self.MAJOR_CORRIDOR_M = 100.0
        self.MINOR_CORRIDOR_M = 20.0
        self.MAX_SPEED_MPS = 30.0
        self.ELEVATED_SPEED_MPS = 20.0

        self.window_size = 5
        self.location_window = [] 

    def _cross_track_error(self, start_loc, end_loc, curr_lat, curr_lon):
        R = 6371000
        
        lat1 = math.radians(start_loc['lat'])
        lon1 = math.radians(start_loc['lon'])
        lat2 = math.radians(end_loc['lat'])
        lon2 = math.radians(end_loc['lon'])
        lat3 = math.radians(curr_lat)
        lon3 = math.radians(curr_lon)
        
        y = math.sin(lon2 - lon1) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
        bearing12 = math.atan2(y, x)
        
        y3 = math.sin(lon3 - lon1) * math.cos(lat3)
        x3 = math.cos(lat1) * math.sin(lat3) - math.sin(lat1) * math.cos(lat3) * math.cos(lon3 - lon1)
        bearing13 = math.atan2(y3, x3)
        
        d13 = math.acos(math.sin(lat1) * math.sin(lat3) + math.cos(lat1) * math.cos(lat3) * math.cos(lon3 - lon1))
        
        d_xt = math.asin(math.sin(d13) * math.sin(bearing13 - bearing12)) * R
        return abs(d_xt)

    def calculate_risk(self, session_state, telemetry):
        risk_delta = 0.0
        reasons = []

        self.location_window.append((telemetry.location.lat, telemetry.location.lon))
        if len(self.location_window) > self.window_size:
            self.location_window.pop(0)

        if len(self.location_window) >= 3:
            locs = np.array(self.location_window)
            current_lat = np.median(locs[:, 0])
            current_lon = np.median(locs[:, 1])
        else:
            current_lat = telemetry.location.lat
            current_lon = telemetry.location.lon

        accuracy = getattr(telemetry, 'accuracy', 0.0)
        is_trusted_location = accuracy <= 50.0
        
        if is_trusted_location:
            start_loc = session_state.get('start_loc')
            if start_loc:
                xt_error = self._cross_track_error(start_loc, session_state['end_loc'], current_lat, current_lon)
                if xt_error > self.MAJOR_CORRIDOR_M:
                    risk_delta += 1.6
                    reasons.append(f"Major route deviation (+{int(xt_error)}m)")
                elif xt_error > self.MINOR_CORRIDOR_M:
                    risk_delta += 0.8
                    reasons.append(f"Minor route deviation (+{int(xt_error)}m)")
            
            if telemetry.speed >= 40.0:
                risk_delta += 2.0
                reasons.append(f"Critical speed ({int(telemetry.speed*3.6)} km/h)")
            elif telemetry.speed > self.MAX_SPEED_MPS:
                risk_delta += 1.0
                reasons.append(f"Unsafe speed ({int(telemetry.speed*3.6)} km/h)")
            elif telemetry.speed > self.ELEVATED_SPEED_MPS:
                risk_delta += 0.6
                reasons.append(f"Speed increasing ({int(telemetry.speed*3.6)} km/h)")
            
            if telemetry.speed < 2.0 and session_state.get('consecutive_stops', 0) > 4: 
                 risk_delta += 1.5
                 reasons.append(f"Unexpected prolonged stop ({session_state['consecutive_stops']}s)")

            curr_dist = np.sqrt((current_lat - session_state['end_loc']['lat'])**2 + 
                                (current_lon - session_state['end_loc']['lon'])**2)
            last_dist = session_state.get('last_dist', curr_dist)
            if curr_dist > (last_dist + 0.0001) and session_state.get('bad_trend_count', 0) > 3:
                 risk_delta += 1.2
                 reasons.append("Moving away from destination")

        else:
             if risk_delta == 0:
                reasons.append(f"Low confidence GPS ({accuracy}m) - Monitoring paused")

        if session_state.get('is_overdue', False):
             risk_delta += 2.0
             reasons.append("Ride overdue")

        if risk_delta > 0:
            self.risk_score = min(self.MAX_RISK, self.risk_score + risk_delta)
        else:
            self.risk_score = max(0.0, self.risk_score - self.DECAY_RATE)

        # Interpolated probability mapping
        def get_probability(score):
            points = [(0,0.0), (15,0.08), (30,0.18), (45,0.35), (60,0.60), (75,0.82), (90,0.96), (100,0.99)]
            for i in range(len(points)-1):
                if points[i][0] <= score <= points[i+1][0]:
                    x0, y0 = points[i]
                    x1, y1 = points[i+1]
                    return y0 + (y1 - y0) * (score - x0) / (x1 - x0)
            return 0.99

        probability = get_probability(self.risk_score)
        
        severity = "NORMAL"
        if self.risk_score > 75: severity = "ESCALATED"
        elif self.risk_score > 50: severity = "MONITORING"
        elif self.risk_score > 25: severity = "ELEVATED"

        return {
            "score": round(self.risk_score, 1),
            "probability": round(probability, 4),
            "severity": severity,
            "reasons": list(set(reasons)) # dedup
        }
