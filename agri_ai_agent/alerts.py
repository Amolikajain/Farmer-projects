"""
Alerts Module for Smart AI Farming Assistant
Handles: Rain Alerts, Pest Outbreak Warnings, Price Drop Alerts
"""

import requests
import os
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class Alert:
    """Alert data structure"""
    def __init__(self, alert_type: str, level: AlertLevel, title: str, message: str, timestamp: str):
        self.alert_type = alert_type
        self.level = level
        self.title = title
        self.message = message
        self.timestamp = timestamp
    
    def to_dict(self):
        return {
            "type": self.alert_type,
            "level": self.level.value,
            "title": self.title,
            "message": self.message,
            "timestamp": self.timestamp
        }

class AlertsManager:
    """Main class to manage all agricultural alerts"""
    
    def __init__(self, weather_api_key: Optional[str] = None):
        self.weather_api_key = weather_api_key or os.getenv("WEATHER_API_KEY", "b898b54a25487a86734efde5a7c63da0")
        self.alerts = []
        
        # Price thresholds for price drop alerts (sample values)
        self.price_thresholds = {
            "Rice": 3000,
            "Wheat": 2500,
            "Soybean": 4500,
            "Onion": 1500,
            "Cotton": 5500
        }
        
        # Market price data (mock - can be replaced with real API)
        self.current_prices = {
            "Rice": 3200,
            "Wheat": 2800,
            "Soybean": 4200,
            "Onion": 1200,
            "Cotton": 5800
        }
        
        # Pest conditions based on weather
        self.pest_conditions = {
            "Armyworm": {"min_temp": 20, "max_temp": 30, "min_humidity": 60},
            "Stem borer": {"min_temp": 22, "max_temp": 28, "min_humidity": 80},
            "Leaf hopper": {"min_temp": 25, "max_temp": 32, "min_humidity": 50},
            "Powdery mildew": {"min_temp": 15, "max_temp": 26, "min_humidity": 40},
        }
    
    def get_weather(self, city: str) -> Optional[Dict]:
        """Fetch weather data from OpenWeatherMap API"""
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_api_key}&units=metric"
        
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if "main" not in data or "weather" not in data:
                return None
            
            return {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"],
                "rain": data.get("rain", {}).get("1h", 0)
            }
        except Exception as e:
            print(f"Error fetching weather: {str(e)}")
            return None
    
    def check_rain_alerts(self, city: str) -> List[Alert]:
        """Check for rain alerts based on weather data"""
        rain_alerts = []
        weather = self.get_weather(city)
        
        if not weather:
            return rain_alerts
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        condition = weather["description"].lower()
        humidity = weather["humidity"]
        
        # Check for heavy rain
        if "heavy rain" in condition or weather["rain"] > 10:
            alert = Alert(
                alert_type="rain",
                level=AlertLevel.CRITICAL,
                title="⚠️ Heavy Rain Alert",
                message=f"Heavy rain expected in {city}. Rain: {weather['rain']}mm. Avoid field operations and protect crops.",
                timestamp=timestamp
            )
            rain_alerts.append(alert)
        
        # Check for moderate rain
        elif "rain" in condition or weather["rain"] > 2:
            alert = Alert(
                alert_type="rain",
                level=AlertLevel.WARNING,
                title="🌧️ Rain Warning",
                message=f"Rain expected in {city}. Rain: {weather['rain']}mm. Plan irrigation accordingly.",
                timestamp=timestamp
            )
            rain_alerts.append(alert)
        
        # Check for high humidity (potential waterlogging)
        if humidity > 85:
            alert = Alert(
                alert_type="rain",
                level=AlertLevel.WARNING,
                title="💧 High Humidity Alert",
                message=f"High humidity ({humidity}%) detected in {city}. Risk of fungal diseases. Ensure proper drainage.",
                timestamp=timestamp
            )
            rain_alerts.append(alert)
        
        # Check for no rain (drought warning)
        elif humidity < 30:
            alert = Alert(
                alert_type="rain",
                level=AlertLevel.WARNING,
                title="🏜️ Drought Warning",
                message=f"Low humidity ({humidity}%) in {city}. Water stress risk. Increase irrigation frequency.",
                timestamp=timestamp
            )
            rain_alerts.append(alert)
        
        return rain_alerts
    
    def check_pest_outbreak_warnings(self, city: str) -> List[Alert]:
        """Check for pest outbreak risks based on weather conditions"""
        pest_alerts = []
        weather = self.get_weather(city)
        
        if not weather:
            return pest_alerts
        
        temp = weather["temperature"]
        humidity = weather["humidity"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check each pest condition
        for pest, conditions in self.pest_conditions.items():
            min_temp = conditions["min_temp"]
            max_temp = conditions["max_temp"]
            min_humidity = conditions["min_humidity"]
            
            # If current conditions match pest breeding conditions
            if (min_temp <= temp <= max_temp and humidity >= min_humidity):
                alert = Alert(
                    alert_type="pest",
                    level=AlertLevel.WARNING,
                    title=f"🐛 Pest Outbreak Warning: {pest}",
                    message=f"Weather conditions in {city} are favorable for {pest} outbreak. "
                            f"Current: {temp}°C, {humidity}% humidity. "
                            f"Consider preventive measures and apply neem oil or recommended pesticides.",
                    timestamp=timestamp
                )
                pest_alerts.append(alert)
        
        # Check for extreme temperature (heat/cold stress on crops)
        if temp > 35:
            alert = Alert(
                alert_type="pest",
                level=AlertLevel.WARNING,
                title="🌡️ Heat Stress Alert",
                message=f"Extreme heat ({temp}°C) in {city}. Crops at heat stress risk. Increase irrigation and provide shade.",
                timestamp=timestamp
            )
            pest_alerts.append(alert)
        
        elif temp < 10:
            alert = Alert(
                alert_type="pest",
                level=AlertLevel.WARNING,
                title="❄️ Cold Stress Alert",
                message=f"Low temperature ({temp}°C) in {city}. Crops at cold stress risk. Protect seedlings and use mulching.",
                timestamp=timestamp
            )
            pest_alerts.append(alert)
        
        return pest_alerts
    
    def check_price_drop_alerts(self, crop_prices: Optional[Dict] = None) -> List[Alert]:
        """Check for price drop alerts in market"""
        price_alerts = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Use provided prices or default current prices
        prices = crop_prices or self.current_prices
        
        for crop, threshold in self.price_thresholds.items():
            if crop in prices:
                current_price = prices[crop]
                price_drop_percentage = ((threshold - current_price) / threshold) * 100
                
                # Check if price has dropped below threshold
                if current_price < threshold:
                    if price_drop_percentage > 20:
                        alert = Alert(
                            alert_type="price",
                            level=AlertLevel.CRITICAL,
                            title=f"📉 Price Drop Alert: {crop}",
                            message=f"{crop} price has dropped significantly to ₹{current_price}/quintal "
                                   f"({price_drop_percentage:.1f}% below threshold). "
                                   f"Consider storing for future sale or diversifying crops.",
                            timestamp=timestamp
                        )
                        price_alerts.append(alert)
                    elif price_drop_percentage > 10:
                        alert = Alert(
                            alert_type="price",
                            level=AlertLevel.WARNING,
                            title=f"📊 Price Decline: {crop}",
                            message=f"{crop} price declining to ₹{current_price}/quintal ({price_drop_percentage:.1f}% drop). "
                                   f"Monitor market trends before selling.",
                            timestamp=timestamp
                        )
                        price_alerts.append(alert)
                else:
                    # Price is good
                    price_increase = ((current_price - threshold) / threshold) * 100
                    if price_increase > 15:
                        alert = Alert(
                            alert_type="price",
                            level=AlertLevel.INFO,
                            title=f"📈 Good Price: {crop}",
                            message=f"{crop} price is favorable at ₹{current_price}/quintal ({price_increase:.1f}% above threshold). "
                                   f"Good time to sell if ready.",
                            timestamp=timestamp
                        )
                        price_alerts.append(alert)
        
        return price_alerts
    
    def get_all_alerts(self, city: str, crop_prices: Optional[Dict] = None) -> List[Alert]:
        """Get all alerts for a city"""
        all_alerts = []
        
        # Get all types of alerts
        all_alerts.extend(self.check_rain_alerts(city))
        all_alerts.extend(self.check_pest_outbreak_warnings(city))
        all_alerts.extend(self.check_price_drop_alerts(crop_prices))
        
        # Sort by severity (critical > warning > info)
        severity_order = {AlertLevel.CRITICAL: 0, AlertLevel.WARNING: 1, AlertLevel.INFO: 2}
        all_alerts.sort(key=lambda x: severity_order[x.level])
        
        return all_alerts
    
    def get_alerts_as_dicts(self, city: str, crop_prices: Optional[Dict] = None) -> List[Dict]:
        """Get all alerts as dictionary for API response"""
        alerts = self.get_all_alerts(city, crop_prices)
        return [alert.to_dict() for alert in alerts]
    
    def update_current_prices(self, prices: Dict):
        """Update current market prices"""
        self.current_prices.update(prices)
    
    def update_price_thresholds(self, thresholds: Dict):
        """Update price thresholds for alerts"""
        self.price_thresholds.update(thresholds)

# Helper function for easy integration
def get_alerts(city: str, weather_api_key: Optional[str] = None, crop_prices: Optional[Dict] = None) -> List[Dict]:
    """Convenient function to get all alerts for a city"""
    manager = AlertsManager(weather_api_key)
    return manager.get_alerts_as_dicts(city, crop_prices)
