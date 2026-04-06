class WeatherInput:
    """
    DonkeyCar part that provides current weather condition as input
    """
    def __init__(self, default_weather=0):
        """
        default_weather: 0=sunny, 1=cloudy, 2=light_rain, 3=heavy_rain
        """
        self.weather_code = default_weather
        self.weather_names = {
            0: "sunny",
            1: "cloudy", 
            2: "light_rain",
            3: "heavy_rain"
        }
        print(f"Weather initialized: {self.weather_names[self.weather_code]}")
    
    def set_weather(self, code):
        """
        Change the weather code
        """
        if code in self.weather_names:
            self.weather_code = code
            print(f"Weather changed to: {self.weather_names[code]}")
        else:
            print(f"Invalid weather code: {code}. Valid codes: 0-3")
    
    def run(self):
        """
        Return current weather code
        """
        return self.weather_code
    
    def run_threaded(self):
        """
        Return current weather code (same as run)
        """
        return self.weather_code
    
    def shutdown(self):
        pass