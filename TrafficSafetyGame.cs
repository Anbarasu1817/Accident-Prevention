using System;
using System.Collections.Generic;
using System.Threading;

namespace AccidentPreventionGame
{
    public class TrafficSafetyGame
    {
        private List<Vehicle> vehicles = new List<Vehicle>();
        private List<EmergencyService> emergencyServices = new List<EmergencyService>();
        private AIPredictionEngine aiEngine = new AIPredictionEngine();
        private V2VCommunication v2vSystem = new V2VCommunication();
        private GameWorld world = new GameWorld();
        private int gameTick;
        
        public TrafficSafetyGame()
        {
            InitializeGame();
        }
        
        private void InitializeGame()
        {
            gameTick = 0;
            CreateSampleVehicles();
            CreateEmergencyServices();
            
            Console.WriteLine("✅ Game initialized with 3 vehicles and emergency services");
        }
        
        public void RunGame()
        {
            Console.WriteLine("\n🎮 Game Started! Press 'Q' to quit, 'R' to reset\n");
            Thread.Sleep(1000);
            
            while (true)
            {
                if (Console.KeyAvailable)
                {
                    var key = Console.ReadKey(true).Key;
                    if (key == ConsoleKey.Q) break;
                    if (key == ConsoleKey.R) ResetGame();
                }
                
                UpdateGameState();
                RenderGame();
                gameTick++;
                
                Thread.Sleep(200);
            }
            
            Console.WriteLine("\n🎯 Game Over! Final Statistics:");
            DisplayFinalStats();
        }
        
        private void UpdateGameState()
        {
            foreach (var vehicle in vehicles)
            {
                vehicle.Update();
            }
            
            if (gameTick % 5 == 0)
            {
                aiEngine.AnalyzeTraffic(vehicles);
            }
            
            v2vSystem.ProcessMessages();
            CheckCollisions();
        }
        
        private void RenderGame()
        {
            Console.Clear();
            Console.WriteLine($"🚦 Accident Prediction & Prevention System - Tick: {gameTick}");
            Console.WriteLine("======================================================");
            
            world.Render(vehicles);
            DisplaySystemStatus();
        }
        
        private void DisplaySystemStatus()
        {
            Console.WriteLine("\n=== SYSTEM STATUS ===");
            foreach (var vehicle in vehicles)
            {
                vehicle.DisplayStatus();
            }
            
            Console.WriteLine("\n=== EMERGENCY SERVICES ===");
            foreach (var service in emergencyServices)
            {
                Console.WriteLine($"{service.Id} | Position: {service.Position} | Responding: {service.IsResponding}");
            }
            Console.WriteLine("=====================");
        }
        
        private void CheckCollisions()
        {
            for (int i = 0; i < vehicles.Count; i++)
            {
                for (int j = i + 1; j < vehicles.Count; j++)
                {
                    float distance = Vector2.Distance(vehicles[i].Position, vehicles[j].Position);
                    if (distance < 3.0f)
                    {
                        HandleCollision(vehicles[i], vehicles[j]);
                    }
                }
            }
        }
        
        private void HandleCollision(Vehicle v1, Vehicle v2)
        {
            Console.WriteLine($"\n💥 COLLISION DETECTED between {v1.Id} and {v2.Id}!");
            v2vSystem.BroadcastEmergencyAlert(v1, v2);
            
            foreach (var service in emergencyServices)
            {
                service.ReceiveEmergencyAlert(v1.Position);
            }
            
            ResetGame();
        }
        
        private void CreateSampleVehicles()
        {
            vehicles.Add(new Vehicle("V001", new Vector2(10, 50), new Vector2(1, 0), 80f, v2vSystem));
            vehicles.Add(new Vehicle("V002", new Vector2(50, 10), new Vector2(0, 1), 80f, v2vSystem));
            vehicles.Add(new Vehicle("V003", new Vector2(90, 50), new Vector2(-1, 0), 60f, v2vSystem));
        }
        
        private void CreateEmergencyServices()
        {
            emergencyServices.Add(new EmergencyService("EMS_001", new Vector2(25, 25)));
            emergencyServices.Add(new EmergencyService("POLICE_001", new Vector2(75, 75)));
        }
        
        private void ResetGame()
        {
            Console.WriteLine("\n🔄 Resetting game...");
            vehicles.Clear();
            CreateSampleVehicles();
            Thread.Sleep(1000);
        }
        
        private void DisplayFinalStats()
        {
            int totalWarnings = 0;
            int totalEmergencies = 0;
            
            foreach (var vehicle in vehicles)
            {
                totalWarnings += vehicle.WarningCount;
                totalEmergencies += vehicle.EmergencyCount;
            }
            
            Console.WriteLine($"Total Warnings: {totalWarnings}");
            Console.WriteLine($"Total Emergencies: {totalEmergencies}");
            Console.WriteLine($"Game Duration: {gameTick} ticks");
        }
    }
}