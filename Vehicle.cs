using System;

namespace AccidentPreventionGame
{
    public class Vehicle
    {
        public string Id { get; private set; }
        public Vector2 Position { get; private set; }
        public Vector2 Velocity { get; private set; }
        public float Speed { get; private set; }
        public float MaxSpeed { get; private set; }
        
        // Sensors
        private GPSSensor gps = new GPSSensor();
        private LidarSensor lidar = new LidarSensor();
        private IMUSensor imu = new IMUSensor();
        private SpeedSensor speedSensor = new SpeedSensor();
        
        // Communication
        private V2VCommunication communicator;
        private AlertSystem alertSystem = new AlertSystem();
        
        // AI Data
        public CollisionRisk RiskLevel { get; private set; }
        public string RecommendedAction { get; private set; }
        
        // Statistics
        public int WarningCount { get; private set; }
        public int EmergencyCount { get; private set; }
        
        public Vehicle(string id, Vector2 position, Vector2 direction, float speed, V2VCommunication comm)
        {
            Id = id;
            Position = position;
            Velocity = direction;
            Speed = speed;
            MaxSpeed = 100f;
            communicator = comm;
            
            RiskLevel = CollisionRisk.Low;
            RecommendedAction = "Maintain current speed";
            
            WarningCount = 0;
            EmergencyCount = 0;
        }
        
        public void Update()
        {
            // Update position based on velocity and speed
            Position += Velocity * (Speed / 36f);
            
            // Boundary checking
            if (Position.X < 0 || Position.X > 100 || Position.Y < 0 || Position.Y > 100)
            {
                Velocity = new Vector2(-Velocity.X, -Velocity.Y);
            }
            
            // Collect sensor data
            SensorData data = CollectSensorData();
            
            // Process sensor data
            ProcessSensorData(data);
            
            // Check for alerts
            CheckAlerts();
        }
        
        private SensorData CollectSensorData()
        {
            return new SensorData
            {
                Position = gps.GetPosition(Position),
                Speed = speedSensor.GetSpeed(Speed),
                Acceleration = imu.GetAcceleration(),
                Rotation = imu.GetRotation(),
                NearbyObjects = lidar.ScanEnvironment(Position, 15f)
            };
        }
        
        private void ProcessSensorData(SensorData data)
        {
            if (data.Speed > 70f && data.NearbyObjects.Count > 0)
            {
                RiskLevel = CollisionRisk.Medium;
                RecommendedAction = "Reduce speed to 50 km/h";
            }
            else if (data.Speed > 80f && data.NearbyObjects.Count > 1)
            {
                RiskLevel = CollisionRisk.High;
                RecommendedAction = "EMERGENCY: Brake immediately!";
            }
            else if (data.Speed > 90f)
            {
                RiskLevel = CollisionRisk.High;
                RecommendedAction = "DANGER: Excessive speed!";
            }
            else
            {
                RiskLevel = CollisionRisk.Low;
                RecommendedAction = "Maintain current speed";
            }
        }
        
        private void CheckAlerts()
        {
            if (RiskLevel == CollisionRisk.High)
            {
                alertSystem.TriggerEmergencyAlert(RecommendedAction);
                EmergencyCount++;
                Speed = Math.Max(Speed * 0.7f, 30f);
            }
            else if (RiskLevel == CollisionRisk.Medium)
            {
                alertSystem.TriggerWarningAlert(RecommendedAction);
                WarningCount++;
                Speed = Math.Max(Speed * 0.9f, 40f);
            }
        }
        
        public void ReceiveV2VMessage(V2VMessage message)
        {
            Console.WriteLine($"   📨 {Id} received V2V: {message.Content}");
            
            if (message.IsEmergency)
            {
                Speed = Math.Max(Speed * 0.5f, 20f);
                alertSystem.TriggerEmergencyAlert("Emergency alert from nearby vehicle!");
                EmergencyCount++;
            }
            else if (message.Content.Contains("reduce speed"))
            {
                Speed = Math.Max(Speed * 0.8f, 30f);
            }
        }
        
        public void DisplayStatus()
        {
            string riskColor = RiskLevel == CollisionRisk.High ? "🔴" : 
                              RiskLevel == CollisionRisk.Medium ? "🟡" : "🟢";
            
            Console.WriteLine($"{riskColor} {Id} | Pos: {Position} | Speed: {Speed:F0}km/h | Risk: {RiskLevel}");
            Console.WriteLine($"   Action: {RecommendedAction}");
            Console.WriteLine($"   Stats: Warnings: {WarningCount} | Emergencies: {EmergencyCount}");
        }
    }

    public enum CollisionRisk
    {
        Low,
        Medium,
        High
    }
}