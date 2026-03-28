"""
Test script for alerts.py module
"""

from alerts import AlertsManager, AlertLevel

def test_alerts():
    """Run all alert tests"""
    
    print("=" * 60)
    print("Testing Alerts Module")
    print("=" * 60)
    
    manager = AlertsManager()
    
    # Test cities
    test_cities = ["Bhopal", "Nashik", "Navi Mumbai"]
    
    for city in test_cities:
        print(f"\n{'='*60}")
        print(f"Testing Alerts for: {city}")
        print(f"{'='*60}\n")
        
        # Get all alerts
        alerts = manager.get_all_alerts(city)
        
        if not alerts:
            print(f"✓ No alerts for {city}")
        else:
            print(f"Found {len(alerts)} alert(s):\n")
            
            for i, alert in enumerate(alerts, 1):
                alert_dict = alert.to_dict()
                severity_emoji = {
                    "critical": "🚨",
                    "warning": "⚠️",
                    "info": "ℹ️"
                }
                emoji = severity_emoji.get(alert.level.value, "")
                
                print(f"{i}. {emoji} [{alert.level.value.upper()}] {alert.title}")
                print(f"   Message: {alert.message}")
                print(f"   Timestamp: {alert.timestamp}\n")
    
    # Test custom prices
    print(f"{'='*60}")
    print("Testing Price Drop Alerts with Custom Prices")
    print(f"{'='*60}\n")
    
    custom_prices = {
        "Rice": 2500,      # Below threshold (3000)
        "Wheat": 2800,     # Below threshold (2500) - but increased, still ok
        "Soybean": 3800,   # Below threshold (4500)
        "Onion": 800,      # Below threshold (1500)
        "Cotton": 6200     # Above threshold (5500)
    }
    
    price_alerts = manager.check_price_drop_alerts(custom_prices)
    
    if not price_alerts:
        print("✓ No price alerts")
    else:
        print(f"Found {len(price_alerts)} price alert(s):\n")
        for i, alert in enumerate(price_alerts, 1):
            print(f"{i}. {alert.title}")
            print(f"   {alert.message}\n")
    
    print(f"\n{'='*60}")
    print("✓ Alerts Module Test Complete!")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_alerts()
