import pygame
import sys
import random
import math
from datetime import datetime

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
ROAD_WIDTH = 400
LANE_COUNT = 3
LANE_WIDTH = ROAD_WIDTH // LANE_COUNT

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
ORANGE = (255, 165, 0)
DARK_RED = (139, 0, 0)
LIGHT_BLUE = (173, 216, 230)
DARK_GREEN = (0, 100, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Dr. Driving Style Colors
DR_DRIVING_BLUE = (0, 100, 255)
DR_DRIVING_GREEN = (0, 200, 100)
DR_DRIVING_RED = (255, 50, 50)
DR_DRIVING_ORANGE = (255, 150, 0)
DR_DRIVING_YELLOW = (255, 255, 0)
DR_DRIVING_BACKGROUND = (20, 20, 30)

class Car:
    def __init__(self, x, y, width=40, height=70, color=DR_DRIVING_BLUE, is_player=False, car_id=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.speed = 0
        self.max_speed = 120
        self.acceleration = 0.5
        self.deceleration = 0.8
        self.is_player = is_player
        self.lane = 1
        self.id = car_id
        self.v2v_connected = True
        self.emergency_braking = False
        self.collision_warning = False
        self.ai_risk_level = 0
        
    def draw(self, screen):
        # Car body (Dr. Driving style - simplified top-down view)
        car_rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)
        
        # Main car body with gradient
        pygame.draw.rect(screen, self.color, car_rect, border_radius=5)
        
        # Car details
        if self.is_player:
            # Player car has special styling
            pygame.draw.rect(screen, LIGHT_BLUE, 
                           (self.x - self.width//3, self.y - self.height//3, 
                            self.width//1.5, self.height//3), border_radius=3)
        else:
            # NPC cars
            pygame.draw.rect(screen, BLACK, 
                           (self.x - self.width//3, self.y - self.height//3, 
                            self.width//1.5, self.height//3), border_radius=3)
        
        # Headlights (front)
        pygame.draw.circle(screen, YELLOW, (self.x - self.width//4, self.y - self.height//2 + 5), 3)
        pygame.draw.circle(screen, YELLOW, (self.x + self.width//4, self.y - self.height//2 + 5), 3)
        
        # Brake lights
        brake_color = DR_DRIVING_RED if self.emergency_braking else DARK_RED
        pygame.draw.circle(screen, brake_color, (self.x - self.width//4, self.y + self.height//2 - 5), 3)
        pygame.draw.circle(screen, brake_color, (self.x + self.width//4, self.y + self.height//2 - 5), 3)
        
        # V2V indicator (small green dot on roof)
        if self.v2v_connected:
            pygame.draw.circle(screen, DR_DRIVING_GREEN, (self.x, self.y - self.height//4), 3)
            
        # Collision warning (flashing red circle)
        if self.collision_warning and random.random() > 0.5:
            pygame.draw.circle(screen, DR_DRIVING_RED, (self.x, self.y), 10, 2)
        
    def move(self, dx=0, dy=0):
        self.x += dx
        self.y += dy
        
    def change_lane(self, direction):
        new_lane = self.lane + direction
        if 0 <= new_lane < LANE_COUNT:
            self.lane = new_lane
            return True
        return False
        
    def get_lane_x(self):
        road_center = SCREEN_WIDTH // 2
        lane_offset = (self.lane - 1) * LANE_WIDTH
        return road_center - ROAD_WIDTH//2 + LANE_WIDTH//2 + lane_offset

class Obstacle:
    def __init__(self, lane, obstacle_type="car", car_id=None):
        self.lane = lane
        self.type = obstacle_type
        self.x = SCREEN_WIDTH // 2 - ROAD_WIDTH//2 + LANE_WIDTH//2 + lane * LANE_WIDTH
        self.y = -50
        self.speed = random.randint(2, 5)
        self.width = 40
        self.height = 70
        self.car_id = car_id
        self.v2v_enabled = obstacle_type == "car"
        self.collision_alert_sent = False
        
        if obstacle_type == "car":
            self.color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
            self.symbol = "🚗"
        elif obstacle_type == "construction":
            self.color = DR_DRIVING_ORANGE
            self.symbol = "🚧"
            self.width = 60
            self.height = 60
        elif obstacle_type == "accident":
            self.color = DR_DRIVING_RED
            self.symbol = "💥"
            self.width = 60
            self.height = 60
        elif obstacle_type == "pedestrian":
            self.color = BLUE
            self.symbol = "🚶"
            self.width = 30
            self.height = 50
            
    def draw(self, screen):
        if self.type == "car":
            # Draw NPC car
            car_rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)
            pygame.draw.rect(screen, self.color, car_rect, border_radius=5)
            
            # Car details
            pygame.draw.rect(screen, BLACK, 
                           (self.x - self.width//3, self.y - self.height//3, 
                            self.width//1.5, self.height//3), border_radius=3)
            
            # V2V indicator
            if self.v2v_enabled:
                pygame.draw.circle(screen, DR_DRIVING_GREEN, (self.x, self.y - self.height//4), 3)
        else:
            # Draw obstacle with symbol
            font = pygame.font.SysFont('segoeuiemoji', 24)
            text = font.render(self.symbol, True, self.color)
            text_rect = text.get_rect(center=(self.x, self.y))
            screen.blit(text, text_rect)
            
    def move(self, player_speed):
        self.y += (player_speed * 0.1) + self.speed

class AISystem:
    def __init__(self):
        self.risk_threshold = 70
        self.prediction_accuracy = 85
        
    def predict_collision_risk(self, player_car, obstacles):
        risk_score = 0
        
        for obstacle in obstacles:
            distance_x = abs(obstacle.x - player_car.x)
            distance_y = abs(obstacle.y - player_car.y)
            
            if distance_x < 50 and distance_y < 100:
                proximity_risk = max(0, 100 - (distance_y))
                risk_score = max(risk_score, proximity_risk)
                
            speed_risk = min(100, player_car.speed * 0.8)
            risk_score = max(risk_score, speed_risk * 0.7)
                
            if obstacle.lane == player_car.lane:
                risk_score += 20
                
        if random.random() > 0.85:
            risk_score = random.randint(0, 100)
            
        return min(100, risk_score)
    
    def get_recommendation(self, risk_level, current_speed, obstacle_type):
        if risk_level < 30:
            return "Safe driving", DR_DRIVING_GREEN
        elif risk_level < 70:
            if current_speed > 60:
                return "Reduce speed", DR_DRIVING_ORANGE
            else:
                return "Keep distance", DR_DRIVING_ORANGE
        else:
            if obstacle_type == "car":
                return "BRAKE NOW!", DR_DRIVING_RED
            elif obstacle_type == "pedestrian":
                return "STOP! Pedestrian", DR_DRIVING_RED
            else:
                return "AVOID OBSTACLE!", DR_DRIVING_RED

class Alert:
    def __init__(self, message, alert_type="info", urgent=False, source="AI"):
        self.message = message
        self.type = alert_type
        self.urgent = urgent
        self.source = source
        self.timestamp = datetime.now()
        self.duration = 4000
        
    def is_expired(self):
        return (datetime.now() - self.timestamp).total_seconds() * 1000 > self.duration

class V2VSystem:
    def __init__(self):
        self.connected_vehicles = []
        self.messages = []
        
    def connect_vehicle(self, vehicle):
        if vehicle not in self.connected_vehicles:
            self.connected_vehicles.append(vehicle)
            vehicle.v2v_connected = True
            
    def broadcast_alert(self, sender, message, alert_type="warning"):
        for vehicle in self.connected_vehicles:
            if vehicle != sender:
                vehicle.collision_warning = True
                self.messages.append({
                    'from': sender.id if hasattr(sender, 'id') else 'Unknown',
                    'message': message,
                    'type': alert_type,
                    'timestamp': datetime.now()
                })
                
    def send_emergency_brake(self, sender):
        for vehicle in self.connected_vehicles:
            if vehicle != sender and hasattr(vehicle, 'emergency_braking'):
                vehicle.emergency_braking = True
                if hasattr(vehicle, 'speed'):
                    vehicle.speed = max(0, vehicle.speed - 20)

class DrDrivingUI:
    def __init__(self):
        self.components = {
            "AI Prediction": "ACTIVE",
            "V2V Network": "ACTIVE",
            "GPS Tracking": "ACTIVE",
            "Collision Avoidance": "ACTIVE"
        }
        
    def draw(self, screen, game_data):
        # Main game UI (Dr. Driving style)
        
        # Speedometer (top left)
        self.draw_speedometer(screen, game_data['speed'])
        
        # Score (top center)
        self.draw_score(screen, game_data['score'])
        
        # AI Risk Indicator (top right)
        self.draw_risk_indicator(screen, game_data['ai_risk'])
        
        # Alerts (bottom center)
        self.draw_alerts(screen, game_data['alerts'])
        
        # Controls help (bottom)
        self.draw_controls(screen)
        
    def draw_speedometer(self, screen, speed):
        # Speedometer background
        speed_x, speed_y = 80, 50
        pygame.draw.circle(screen, DARK_GRAY, (speed_x, speed_y), 40)
        pygame.draw.circle(screen, WHITE, (speed_x, speed_y), 40, 2)
        
        # Speed text
        font = pygame.font.Font(None, 24)
        speed_text = font.render(f"{speed}", True, WHITE)
        screen.blit(speed_text, (speed_x - speed_text.get_width()//2, speed_y - 8))
        
        # km/h label
        label_font = pygame.font.Font(None, 16)
        label_text = label_font.render("km/h", True, LIGHT_GRAY)
        screen.blit(label_text, (speed_x - label_text.get_width()//2, speed_y + 12))
        
        # Speed warning if too high
        if speed > 80:
            warning_font = pygame.font.Font(None, 18)
            warning_text = warning_font.render("SLOW DOWN!", True, DR_DRIVING_RED)
            screen.blit(warning_text, (speed_x - warning_text.get_width()//2, speed_y + 35))
    
    def draw_score(self, screen, score):
        score_x, score_y = SCREEN_WIDTH // 2, 40
        
        # Score background
        pygame.draw.rect(screen, DARK_GRAY, (score_x - 60, score_y - 25, 120, 50), border_radius=10)
        pygame.draw.rect(screen, WHITE, (score_x - 60, score_y - 25, 120, 50), 2, border_radius=10)
        
        # Score title
        title_font = pygame.font.Font(None, 18)
        title_text = title_font.render("SAFETY SCORE", True, LIGHT_GRAY)
        screen.blit(title_text, (score_x - title_text.get_width()//2, score_y - 15))
        
        # Score value
        score_font = pygame.font.Font(None, 28)
        score_color = DR_DRIVING_GREEN if score >= 80 else DR_DRIVING_ORANGE if score >= 60 else DR_DRIVING_RED
        score_text = score_font.render(f"{score}", True, score_color)
        screen.blit(score_text, (score_x - score_text.get_width()//2, score_y + 5))
    
    def draw_risk_indicator(self, screen, risk_level):
        risk_x, risk_y = SCREEN_WIDTH - 80, 50
        
        # Risk circle
        risk_color = DR_DRIVING_GREEN if risk_level < 30 else DR_DRIVING_ORANGE if risk_level < 70 else DR_DRIVING_RED
        pygame.draw.circle(screen, DARK_GRAY, (risk_x, risk_y), 40)
        pygame.draw.circle(screen, risk_color, (risk_x, risk_y), 40, 3)
        
        # Risk percentage
        font = pygame.font.Font(None, 24)
        risk_text = font.render(f"{risk_level}%", True, risk_color)
        screen.blit(risk_text, (risk_x - risk_text.get_width()//2, risk_y - 8))
        
        # Risk label
        label_font = pygame.font.Font(None, 16)
        label_text = label_font.render("AI RISK", True, LIGHT_GRAY)
        screen.blit(label_text, (risk_x - label_text.get_width()//2, risk_y + 12))
        
        # Warning if high risk
        if risk_level > 70:
            warning_font = pygame.font.Font(None, 18)
            warning_text = warning_font.render("DANGER!", True, DR_DRIVING_RED)
            screen.blit(warning_text, (risk_x - warning_text.get_width()//2, risk_y + 35))
    
    def draw_alerts(self, screen, alerts):
        if alerts:
            latest_alert = alerts[-1]
            
            # Alert background
            alert_width = 400
            alert_height = 60
            alert_x = SCREEN_WIDTH // 2 - alert_width // 2
            alert_y = SCREEN_HEIGHT - 80
            
            # Color based on alert type
            if latest_alert.type == "emergency":
                bg_color = DR_DRIVING_RED
            elif latest_alert.type == "warning":
                bg_color = DR_DRIVING_ORANGE
            else:
                bg_color = DR_DRIVING_BLUE
                
            pygame.draw.rect(screen, bg_color, (alert_x, alert_y, alert_width, alert_height), border_radius=10)
            pygame.draw.rect(screen, WHITE, (alert_x, alert_y, alert_width, alert_height), 2, border_radius=10)
            
            # Alert text
            font = pygame.font.Font(None, 20)
            alert_text = font.render(latest_alert.message, True, WHITE)
            screen.blit(alert_text, (alert_x + alert_width//2 - alert_text.get_width()//2, alert_y + 15))
            
            # Source
            source_font = pygame.font.Font(None, 16)
            source_text = source_font.render(f"From: {latest_alert.source}", True, WHITE)
            screen.blit(source_text, (alert_x + alert_width//2 - source_text.get_width()//2, alert_y + 35))
    
    def draw_controls(self, screen):
        controls_y = SCREEN_HEIGHT - 30
        font = pygame.font.Font(None, 16)
        
        controls = "← → Change Lane | ↑ ↓ Speed | V: V2V Alert | E: Emergency | SPACE: Brake"
        controls_text = font.render(controls, True, LIGHT_GRAY)
        screen.blit(controls_text, (SCREEN_WIDTH//2 - controls_text.get_width()//2, controls_y))

class Road:
    def __init__(self):
        self.markings = []
        self.marking_height = 40
        self.marking_width = 4
        self.marking_gap = 20
        self.initialize_markings()
        
    def initialize_markings(self):
        y = -self.marking_height
        while y < SCREEN_HEIGHT + self.marking_height:
            self.markings.append(y)
            y += self.marking_height + self.marking_gap
            
    def draw(self, screen, speed):
        # Draw road
        road_rect = pygame.Rect((SCREEN_WIDTH - ROAD_WIDTH) // 2, 0, ROAD_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(screen, DARK_GRAY, road_rect)
        
        # Draw lane markings
        for y in self.markings:
            for i in range(LANE_COUNT - 1):
                x = (SCREEN_WIDTH - ROAD_WIDTH) // 2 + (i + 1) * LANE_WIDTH
                marking_rect = pygame.Rect(x - self.marking_width//2, y, self.marking_width, self.marking_height)
                pygame.draw.rect(screen, YELLOW, marking_rect)
            
        # Draw road borders
        pygame.draw.rect(screen, WHITE, ((SCREEN_WIDTH - ROAD_WIDTH) // 2, 0, 5, SCREEN_HEIGHT))
        pygame.draw.rect(screen, WHITE, ((SCREEN_WIDTH + ROAD_WIDTH) // 2 - 5, 0, 5, SCREEN_HEIGHT))
        
        # Move markings for road animation
        for i in range(len(self.markings)):
            self.markings[i] += speed * 0.2
            if self.markings[i] > SCREEN_HEIGHT + self.marking_height:
                self.markings[i] = -self.marking_height

class AccidentPredictionGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Accident Prediction & Prevention System - Dr. Driving Style")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Game state
        self.game_state = "menu"
        self.score = 100
        self.time_elapsed = 0
        self.speed = 40
        self.distance = 0
        
        # Game objects
        self.player_car = Car(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, color=DR_DRIVING_BLUE, is_player=True, car_id=1)
        self.road = Road()
        self.obstacles = []
        self.alerts = []
        self.ui = DrDrivingUI()
        self.v2v_system = V2VSystem()
        self.ai_system = AISystem()
        
        # Game metrics
        self.obstacle_timer = 0
        self.alert_timer = 0
        self.collision_cooldown = 0
        self.npc_car_id = 2
        
        # Connect player to V2V
        self.v2v_system.connect_vehicle(self.player_car)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if self.game_state == "menu":
                    if event.key == pygame.K_RETURN:
                        self.start_game()
                    elif event.key == pygame.K_i:
                        self.game_state = "instructions"
                        
                elif self.game_state == "instructions":
                    if event.key == pygame.K_RETURN:
                        self.start_game()
                    elif event.key == pygame.K_m:
                        self.game_state = "menu"
                        
                elif self.game_state == "playing":
                    if event.key == pygame.K_LEFT:
                        if self.player_car.change_lane(-1):
                            self.add_alert("Lane change to LEFT", "system", False, "Driver")
                    elif event.key == pygame.K_RIGHT:
                        if self.player_car.change_lane(1):
                            self.add_alert("Lane change to RIGHT", "system", False, "Driver")
                    elif event.key == pygame.K_UP:
                        self.speed = min(self.speed + 10, 120)
                        self.add_alert(f"Speed increased to {self.speed} km/h", "system", False, "Driver")
                    elif event.key == pygame.K_DOWN:
                        self.speed = max(self.speed - 10, 0)
                        self.add_alert(f"Speed decreased to {self.speed} km/h", "system", False, "Driver")
                    elif event.key == pygame.K_SPACE:
                        self.speed = max(0, self.speed - 20)
                        self.add_alert("Emergency braking!", "warning", True, "Driver")
                    elif event.key == pygame.K_v:
                        self.send_v2v_alert()
                    elif event.key == pygame.K_e:
                        self.activate_emergency()
                    elif event.key == pygame.K_p:
                        self.game_state = "paused"
                        
                elif self.game_state == "paused":
                    if event.key == pygame.K_p:
                        self.game_state = "playing"
                    elif event.key == pygame.K_m:
                        self.game_state = "menu"
                        
                elif self.game_state == "game_over":
                    if event.key == pygame.K_r:
                        self.start_game()
                    elif event.key == pygame.K_m:
                        self.game_state = "menu"
                        
        return True
    
    def start_game(self):
        self.game_state = "playing"
        self.score = 100
        self.time_elapsed = 0
        self.speed = 40
        self.distance = 0
        self.player_car = Car(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, color=DR_DRIVING_BLUE, is_player=True, car_id=1)
        self.obstacles = []
        self.alerts = [
            Alert("AI System: Accident prediction active", "info", False, "AI"),
            Alert("V2V Network: Connected to nearby vehicles", "info", False, "V2V"),
            Alert("Drive safely and follow AI recommendations", "info", False, "System")
        ]
        self.v2v_system.connect_vehicle(self.player_car)
    
    def add_alert(self, message, alert_type="info", urgent=False, source="AI"):
        self.alerts.append(Alert(message, alert_type, urgent, source))
        if len(self.alerts) > 5:
            self.alerts.pop(0)
    
    def send_v2v_alert(self):
        messages = [
            "V2V: Emergency braking ahead",
            "V2V: Road hazard detected",
            "V2V: Accident scene ahead",
            "V2V: Construction zone ahead"
        ]
        message = random.choice(messages)
        self.add_alert(message, "v2v", False, "V2V")
        self.v2v_system.broadcast_alert(self.player_car, message)
        self.score = min(100, self.score + 2)
    
    def activate_emergency(self):
        self.add_alert("EMERGENCY: All safety systems activated!", "emergency", True, "System")
        self.v2v_system.broadcast_alert(self.player_car, "EMERGENCY BRAKING - COLLISION IMMINENT")
        self.v2v_system.send_emergency_brake(self.player_car)
        self.speed = max(0, self.speed - 30)
    
    def spawn_obstacle(self):
        obstacle_types = [
            ("car", "Vehicle detected ahead", False),
            ("construction", "CONSTRUCTION ZONE AHEAD", True),
            ("accident", "ACCIDENT SCENE AHEAD", True),
            ("pedestrian", "PEDESTRIAN CROSSING", True)
        ]
        
        obstacle_type, message, urgent = random.choice(obstacle_types)
        lane = random.randint(0, LANE_COUNT - 1)
        
        if obstacle_type == "car":
            car_id = self.npc_car_id
            self.npc_car_id += 1
            obstacle = Obstacle(lane, obstacle_type, car_id)
            # Connect NPC car to V2V
            npc_car = Car(obstacle.x, obstacle.y, color=obstacle.color, car_id=car_id)
            self.v2v_system.connect_vehicle(npc_car)
        else:
            obstacle = Obstacle(lane, obstacle_type)
            
        self.obstacles.append(obstacle)
        
        if urgent:
            self.add_alert(message, "warning", True, "AI")
    
    def run_ai_prediction(self):
        road_conditions = {"wet": random.random() < 0.2}
        
        risk_level = self.ai_system.predict_collision_risk(
            self.player_car, self.obstacles
        )
        
        self.player_car.ai_risk_level = risk_level
        
        # Get AI recommendation
        current_obstacle = self.obstacles[0] if self.obstacles else None
        obstacle_type = current_obstacle.type if current_obstacle else "clear"
        recommendation, color = self.ai_system.get_recommendation(risk_level, self.speed, obstacle_type)
        
        return risk_level, recommendation, color
    
    def check_collisions(self):
        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1
            return
            
        for obstacle in self.obstacles[:]:
            distance_x = abs(obstacle.x - self.player_car.x)
            distance_y = abs(obstacle.y - self.player_car.y)
            
            if distance_x < 35 and distance_y < 60:
                # Collision detected
                self.add_alert("COLLISION DETECTED! Emergency response activated!", "emergency", True, "AI")
                self.v2v_system.broadcast_alert(self.player_car, "VEHICLE COLLISION - SEND EMERGENCY SERVICES")
                
                self.score = max(0, self.score - 25)
                self.obstacles.remove(obstacle)
                self.collision_cooldown = 60
                
                # Auto-emergency response
                self.activate_emergency()
                break
            elif distance_x < 50 and distance_y < 100 and not obstacle.collision_alert_sent:
                # Potential collision warning
                self.add_alert("Collision warning! Adjust speed and lane", "warning", True, "AI")
                obstacle.collision_alert_sent = True
    
    def update_game(self):
        if self.game_state != "playing":
            return (0, "System offline", DR_DRIVING_GREEN)
            
        self.time_elapsed += 1
        self.distance += self.speed * 0.01
        
        # Update player car position based on lane
        target_x = self.player_car.get_lane_x()
        self.player_car.x += (target_x - self.player_car.x) * 0.1
        
        # Spawn obstacles
        self.obstacle_timer += 1
        obstacle_chance = 0.02 + (self.speed / 2000)
        if self.obstacle_timer > 30 and random.random() < obstacle_chance:
            self.spawn_obstacle()
            self.obstacle_timer = 0
        
        # Move obstacles
        for obstacle in self.obstacles[:]:
            obstacle.move(self.speed)
            if obstacle.y > SCREEN_HEIGHT + 100:
                self.obstacles.remove(obstacle)
        
        # Run AI prediction
        ai_risk, ai_recommendation, rec_color = self.run_ai_prediction()
        
        # Random AI alerts
        self.alert_timer += 1
        if self.alert_timer > 100 and random.random() < 0.3:
            messages = [
                "Maintain safe following distance",
                "Road conditions normal",
                "Weather conditions clear",
                "Traffic flow optimal"
            ]
            self.add_alert(random.choice(messages), "info", False, "AI")
            self.alert_timer = 0
        
        # Check collisions
        self.check_collisions()
        
        # Update score based on driving behavior
        if self.time_elapsed % 30 == 0:
            score_change = -1
            
            # Bonus for safe speed
            if 40 <= self.speed <= 80:
                score_change += 1
            
            # Penalty for dangerous speed
            if self.speed > 100:
                score_change -= 2
                if random.random() < 0.3:
                    self.add_alert("Speed too high! Reduce speed", "warning", True, "AI")
            
            self.score = max(0, min(100, self.score + score_change))
        
        # Remove expired alerts
        self.alerts = [alert for alert in self.alerts if not alert.is_expired()]
        
        # Check game over conditions
        if self.score <= 0 or self.time_elapsed >= 1800:
            self.game_state = "game_over"
            
        return ai_risk, ai_recommendation, rec_color
    
    def draw_menu(self):
        # Background
        self.screen.fill(DR_DRIVING_BACKGROUND)
        
        # Title
        title_font = pygame.font.Font(None, 64)
        title = title_font.render("ACCIDENT PREDICTION SYSTEM", True, DR_DRIVING_BLUE)
        subtitle = self.font.render("Dr. Driving Style", True, DR_DRIVING_GREEN)
        
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 170))
        
        # Features
        features = [
            "🚗 AI-Powered Collision Prediction",
            "📡 Vehicle-to-Vehicle Communication", 
            "🚨 Real-time Emergency Alerts",
            "🛡️ Proactive Accident Prevention"
        ]
        
        for i, feature in enumerate(features):
            text = self.font.render(feature, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 250 + i * 50))
        
        # Start button
        pygame.draw.rect(self.screen, DR_DRIVING_GREEN, (SCREEN_WIDTH//2 - 100, 500, 200, 50), border_radius=10)
        start_text = self.font.render("START DRIVING", True, BLACK)
        self.screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, 515))
        
        # Instructions button
        pygame.draw.rect(self.screen, DR_DRIVING_BLUE, (SCREEN_WIDTH//2 - 100, 570, 200, 40), border_radius=8)
        inst_text = self.font.render("INSTRUCTIONS (I)", True, WHITE)
        self.screen.blit(inst_text, (SCREEN_WIDTH//2 - inst_text.get_width()//2, 580))
    
    def draw_instructions(self):
        self.screen.fill(DR_DRIVING_BACKGROUND)
        
        title = self.font.render("GAME INSTRUCTIONS", True, DR_DRIVING_GREEN)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        instructions = [
            "CONTROLS:",
            "← → Arrow Keys: Change lanes",
            "↑ ↓ Arrow Keys: Increase/decrease speed", 
            "SPACE: Emergency brake",
            "V: Send V2V alert to other vehicles",
            "E: Activate emergency protocol",
            "P: Pause game",
            "",
            "GAME OBJECTIVE:",
            "• Maintain high safety score",
            "• Follow AI recommendations",
            "• Avoid collisions with obstacles",
            "• Use V2V communication for safety"
        ]
        
        for i, instruction in enumerate(instructions):
            text = pygame.font.Font(None, 24).render(instruction, True, WHITE)
            self.screen.blit(text, (100, 120 + i * 30))
        
        # Back button
        pygame.draw.rect(self.screen, DR_DRIVING_BLUE, (SCREEN_WIDTH//2 - 100, 500, 200, 50), border_radius=10)
        back_text = self.font.render("START GAME (ENTER)", True, WHITE)
        self.screen.blit(back_text, (SCREEN_WIDTH//2 - back_text.get_width()//2, 515))
        
        menu_text = pygame.font.Font(None, 20).render("Press M for Main Menu", True, LIGHT_GRAY)
        self.screen.blit(menu_text, (SCREEN_WIDTH//2 - menu_text.get_width()//2, 570))
    
    def draw_playing(self, ai_data):
        # Draw background
        self.screen.fill((40, 40, 50))
        
        # Draw road
        self.road.draw(self.screen, self.speed)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        # Draw player car
        self.player_car.draw(self.screen)
        
        # Draw UI
        ui_data = {
            'speed': self.speed,
            'score': self.score,
            'ai_risk': ai_data[0],
            'alerts': self.alerts
        }
        self.ui.draw(self.screen, ui_data)
        
        # Draw distance
        dist_font = pygame.font.Font(None, 20)
        dist_text = dist_font.render(f"Distance: {self.distance:.1f} km", True, WHITE)
        self.screen.blit(dist_text, (SCREEN_WIDTH - 120, 20))
        
        # Draw AI recommendation
        if ai_data[0] > 30:
            rec_font = pygame.font.Font(None, 22)
            rec_text = rec_font.render(f"AI: {ai_data[1]}", True, ai_data[2])
            self.screen.blit(rec_text, (SCREEN_WIDTH//2 - rec_text.get_width()//2, 100))
    
    def draw_paused(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Paused text
        paused_font = pygame.font.Font(None, 72)
        paused_text = paused_font.render("GAME PAUSED", True, DR_DRIVING_YELLOW)
        self.screen.blit(paused_text, (SCREEN_WIDTH//2 - paused_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        # Instructions
        inst_font = pygame.font.Font(None, 24)
        inst_text = inst_font.render("Press P to resume or M for Main Menu", True, WHITE)
        self.screen.blit(inst_text, (SCREEN_WIDTH//2 - inst_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
    
    def draw_game_over(self):
        self.screen.fill(DR_DRIVING_BACKGROUND)
        
        # Game over text
        game_over_font = pygame.font.Font(None, 72)
        game_over_text = game_over_font.render("GAME OVER", True, DR_DRIVING_RED)
        self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 100))
        
        # Score
        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(f"Final Safety Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 200))
        
        # Distance
        dist_font = pygame.font.Font(None, 36)
        dist_text = dist_font.render(f"Distance Traveled: {self.distance:.1f} km", True, LIGHT_GRAY)
        self.screen.blit(dist_text, (SCREEN_WIDTH//2 - dist_text.get_width()//2, 260))
        
        # Rating
        if self.score >= 90:
            rating = "🏆 EXPERT DRIVER - PERFECT SAFETY!"
            color = DR_DRIVING_GREEN
        elif self.score >= 70:
            rating = "👍 GOOD DRIVER - SAFE JOURNEY!"
            color = DR_DRIVING_YELLOW
        elif self.score >= 50:
            rating = "⚠️ AVERAGE - NEEDS IMPROVEMENT"
            color = DR_DRIVING_ORANGE
        else:
            rating = "🚨 POOR - PRACTICE REQUIRED"
            color = DR_DRIVING_RED
            
        rating_font = pygame.font.Font(None, 32)
        rating_text = rating_font.render(rating, True, color)
        self.screen.blit(rating_text, (SCREEN_WIDTH//2 - rating_text.get_width()//2, 320))
        
        # Restart button
        pygame.draw.rect(self.screen, DR_DRIVING_GREEN, (SCREEN_WIDTH//2 - 100, 400, 200, 50), border_radius=10)
        restart_text = self.font.render("RESTART (R)", True, BLACK)
        self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 415))
        
        # Menu button
        pygame.draw.rect(self.screen, DR_DRIVING_BLUE, (SCREEN_WIDTH//2 - 100, 470, 200, 50), border_radius=10)
        menu_text = self.font.render("MAIN MENU (M)", True, WHITE)
        self.screen.blit(menu_text, (SCREEN_WIDTH//2 - menu_text.get_width()//2, 485))
    
    def draw(self):
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "instructions":
            self.draw_instructions()
        elif self.game_state == "playing":
            ai_data = self.update_game()
            self.draw_playing(ai_data)
        elif self.game_state == "paused":
            ai_data = self.update_game()
            self.draw_playing(ai_data)
            self.draw_paused()
        elif self.game_state == "game_over":
            self.draw_game_over()
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = AccidentPredictionGame()
    game.run()