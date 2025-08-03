from mcp.server.fastmcp import FastMCP
from pydantic import Field
import os
import requests
import logging
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP instance
mcp = FastMCP("weather-service")

class WeatherService:
    def __init__(self):
        self.accuweather_api_key = os.getenv('ACCUWEATHER_API_KEY')
        
        # Kandugula location key from AccuWeather
        self.location_key = "2828381"
        self.base_url = "http://dataservice.accuweather.com"
        
        if not self.accuweather_api_key:
            raise ValueError("Please set ACCUWEATHER_API_KEY environment variable")
    
    def get_weather_data(self):
        """
        Fetch weather data from AccuWeather API for Kandugula
        """
        try:
            # AccuWeather Current Conditions API endpoint
            current_conditions_url = f"{self.base_url}/currentconditions/v1/{self.location_key}"
            
            params = {
                'apikey': self.accuweather_api_key,
                'details': 'true'  # Get detailed information
            }
            
            logger.info(f"Fetching current conditions for Kandugula (Location Key: {self.location_key})")
            response = requests.get(current_conditions_url, params=params, timeout=10)
            response.raise_for_status()
            
            current_data = response.json()
            
            if not current_data:
                logger.warning("No current weather data received from AccuWeather")
                return None
            
            # Get location name to confirm
            location_url = f"{self.base_url}/locations/v1/{self.location_key}"
            location_params = {'apikey': self.accuweather_api_key}
            
            location_response = requests.get(location_url, params=location_params, timeout=10)
            location_info = location_response.json() if location_response.status_code == 200 else {}
            
            # Extract weather information
            weather_info = current_data[0]  # Current conditions returns an array
            
            weather_data = {
                'location_name': location_info.get('LocalizedName', 'Kandugula'),
                'observation_time': weather_info.get('LocalObservationDateTime'),
                'condition': weather_info['WeatherText'],
                'weather_icon': weather_info.get('WeatherIcon'),
                'is_day_time': weather_info.get('IsDayTime'),
                'has_precipitation': weather_info.get('HasPrecipitation'),
                'precipitation_type': weather_info.get('PrecipitationType'),
                
                # Temperature data
                'temperature': weather_info['Temperature']['Metric']['Value'],
                'temperature_unit': weather_info['Temperature']['Metric']['Unit'],
                'realfeel_temp': weather_info['RealFeelTemperature']['Metric']['Value'],
                'realfeel_phrase': weather_info['RealFeelTemperature']['Metric'].get('Phrase'),
                'realfeel_shade': weather_info.get('RealFeelTemperatureShade', {}).get('Metric', {}).get('Value'),
                'realfeel_shade_phrase': weather_info.get('RealFeelTemperatureShade', {}).get('Metric', {}).get('Phrase'),
                'apparent_temp': weather_info.get('ApparentTemperature', {}).get('Metric', {}).get('Value'),
                'windchill_temp': weather_info.get('WindChillTemperature', {}).get('Metric', {}).get('Value'),
                'wetbulb_temp': weather_info.get('WetBulbTemperature', {}).get('Metric', {}).get('Value'),
                'wetbulb_globe_temp': weather_info.get('WetBulbGlobeTemperature', {}).get('Metric', {}).get('Value'),
                
                # Humidity and dew point
                'humidity': weather_info.get('RelativeHumidity'),
                'indoor_humidity': weather_info.get('IndoorRelativeHumidity'),
                'dew_point': weather_info.get('DewPoint', {}).get('Metric', {}).get('Value'),
                
                # Wind data
                'wind_speed': weather_info.get('Wind', {}).get('Speed', {}).get('Metric', {}).get('Value'),
                'wind_direction': weather_info.get('Wind', {}).get('Direction', {}).get('Localized'),
                'wind_degrees': weather_info.get('Wind', {}).get('Direction', {}).get('Degrees'),
                'wind_gust': weather_info.get('WindGust', {}).get('Speed', {}).get('Metric', {}).get('Value'),
                
                # Atmospheric data
                'pressure': weather_info.get('Pressure', {}).get('Metric', {}).get('Value'),
                'pressure_tendency': weather_info.get('PressureTendency', {}).get('LocalizedText'),
                'visibility': weather_info.get('Visibility', {}).get('Metric', {}).get('Value'),
                'cloud_cover': weather_info.get('CloudCover'),
                'ceiling': weather_info.get('Ceiling', {}).get('Metric', {}).get('Value'),
                
                # UV data
                'uv_index': weather_info.get('UVIndex'),
                'uv_index_float': weather_info.get('UVIndexFloat'),
                'uv_text': weather_info.get('UVIndexText'),
                
                # Precipitation data
                'precip_1hr': weather_info.get('Precip1hr', {}).get('Metric', {}).get('Value'),
                'precip_past_hour': weather_info.get('PrecipitationSummary', {}).get('PastHour', {}).get('Metric', {}).get('Value'),
                'precip_past_3hrs': weather_info.get('PrecipitationSummary', {}).get('Past3Hours', {}).get('Metric', {}).get('Value'),
                'precip_past_6hrs': weather_info.get('PrecipitationSummary', {}).get('Past6Hours', {}).get('Metric', {}).get('Value'),
                'precip_past_12hrs': weather_info.get('PrecipitationSummary', {}).get('Past12Hours', {}).get('Metric', {}).get('Value'),
                'precip_past_24hrs': weather_info.get('PrecipitationSummary', {}).get('Past24Hours', {}).get('Metric', {}).get('Value'),
                
                # Temperature ranges
                'temp_6hr_min': weather_info.get('TemperatureSummary', {}).get('Past6HourRange', {}).get('Minimum', {}).get('Metric', {}).get('Value'),
                'temp_6hr_max': weather_info.get('TemperatureSummary', {}).get('Past6HourRange', {}).get('Maximum', {}).get('Metric', {}).get('Value'),
                'temp_12hr_min': weather_info.get('TemperatureSummary', {}).get('Past12HourRange', {}).get('Minimum', {}).get('Metric', {}).get('Value'),
                'temp_12hr_max': weather_info.get('TemperatureSummary', {}).get('Past12HourRange', {}).get('Maximum', {}).get('Metric', {}).get('Value'),
                'temp_24hr_min': weather_info.get('TemperatureSummary', {}).get('Past24HourRange', {}).get('Minimum', {}).get('Metric', {}).get('Value'),
                'temp_24hr_max': weather_info.get('TemperatureSummary', {}).get('Past24HourRange', {}).get('Maximum', {}).get('Metric', {}).get('Value'),
                'temp_24hr_departure': weather_info.get('Past24HourTemperatureDeparture', {}).get('Metric', {}).get('Value'),
                
                # Links
                'mobile_link': weather_info.get('MobileLink'),
                'web_link': weather_info.get('Link')
            }
            
            logger.info(f"Successfully fetched weather data for {weather_data['location_name']}")
            return weather_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching AccuWeather API data: {e}")
            return None
        except KeyError as e:
            logger.error(f"Error parsing AccuWeather API response: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    def format_weather_message(self, weather_data):
        """Format comprehensive weather data into a stunning message"""
        if not weather_data:
            return "❌ Unable to fetch weather data for Kandugula from AccuWeather"
        
        try:
            # Get weather emoji based on condition
            weather_emoji = self.get_weather_emoji(weather_data.get('condition', ''))
            location_name = weather_data.get('location_name', 'Kandugula')
            
            # Create dynamic header based on time of day
            current_hour = datetime.now().hour
            if 5 <= current_hour < 12:
                greeting = "🌅 Good Morning!"
                time_emoji = "🌄"
            elif 12 <= current_hour < 17:
                greeting = "☀️ Good Afternoon!"
                time_emoji = "🏙️"
            elif 17 <= current_hour < 21:
                greeting = "🌆 Good Evening!"
                time_emoji = "🌇"
            else:
                greeting = "🌙 Good Night!"
                time_emoji = "🌃"
            
            # Temperature analysis
            temp = weather_data.get('temperature', 'N/A')
            temp_unit = weather_data.get('temperature_unit', 'C')
            realfeel = weather_data.get('realfeel_temp')
            realfeel_phrase = weather_data.get('realfeel_phrase', '')
            
            # Start building the comprehensive message
            message = f"""🌍 ══════════════════════════════
{time_emoji} **{greeting}**
🏘️ **{location_name.upper()} VILLAGE**
📊 **COMPREHENSIVE WEATHER REPORT**
══════════════════════════════

{weather_emoji} **CURRENT CONDITIONS** {weather_emoji}
├─ Weather: **{weather_data.get('condition', 'N/A')}**
├─ Time: **{'☀️ Daytime' if weather_data.get('is_day_time') else '🌙 Nighttime'}**
└─ Precipitation: **{'🌧️ Yes' if weather_data.get('has_precipitation') else '🌤️ None'}**

🌡️ **TEMPERATURE READINGS**
├─ Current: **{temp}°{temp_unit}**
├─ RealFeel: **{realfeel}°{temp_unit}** ({realfeel_phrase})"""
            
            # Add additional temperature readings if available
            if weather_data.get('realfeel_shade'):
                message += f"\n├─ RealFeel Shade: **{weather_data.get('realfeel_shade')}°{temp_unit}** ({weather_data.get('realfeel_shade_phrase', '')})"
            
            if weather_data.get('apparent_temp'):
                message += f"\n├─ Apparent: **{weather_data.get('apparent_temp')}°{temp_unit}**"
            
            if weather_data.get('windchill_temp'):
                message += f"\n├─ Wind Chill: **{weather_data.get('windchill_temp')}°{temp_unit}**"
            
            if weather_data.get('wetbulb_temp'):
                message += f"\n├─ Wet Bulb: **{weather_data.get('wetbulb_temp')}°{temp_unit}**"
            
            if weather_data.get('dew_point'):
                message += f"\n└─ Dew Point: **{weather_data.get('dew_point')}°{temp_unit}**"
            
            # Temperature trends
            temp_24hr_min = weather_data.get('temp_24hr_min')
            temp_24hr_max = weather_data.get('temp_24hr_max')
            temp_departure = weather_data.get('temp_24hr_departure')
            
            if temp_24hr_min and temp_24hr_max:
                message += f"""

📈 **24-HOUR TEMPERATURE RANGE**
├─ Minimum: **{temp_24hr_min}°{temp_unit}**
├─ Maximum: **{temp_24hr_max}°{temp_unit}**"""
                if temp_departure:
                    trend = "🔺" if temp_departure > 0 else "🔻" if temp_departure < 0 else "➡️"
                    message += f"\n└─ vs Yesterday: **{trend} {abs(temp_departure)}°{temp_unit}**"
            
            # Humidity section
            humidity = weather_data.get('humidity')
            indoor_humidity = weather_data.get('indoor_humidity')
            
            message += f"""

💧 **HUMIDITY & MOISTURE**
├─ Outdoor: **{humidity}%**"""
            
            if indoor_humidity and indoor_humidity != humidity:
                message += f"\n├─ Indoor: **{indoor_humidity}%**"
            
            # Humidity context
            if humidity:
                if humidity >= 80:
                    humidity_context = "🌊 Very humid - sticky conditions!"
                elif humidity >= 60:
                    humidity_context = "😌 Comfortable moisture level"
                elif humidity >= 40:
                    humidity_context = "🌬️ Moderate - slightly dry"
                else:
                    humidity_context = "🏜️ Very dry air!"
                message += f"\n└─ Comfort: {humidity_context}"
            
            # Wind section
            wind_speed = weather_data.get('wind_speed')
            wind_direction = weather_data.get('wind_direction')
            wind_degrees = weather_data.get('wind_degrees')
            wind_gust = weather_data.get('wind_gust')
            
            if wind_speed:
                wind_context = ""
                if wind_speed >= 50:
                    wind_icon = "💨💨💨"
                    wind_context = "Dangerous winds!"
                elif wind_speed >= 30:
                    wind_icon = "💨💨"
                    wind_context = "Very windy!"
                elif wind_speed >= 15:
                    wind_icon = "💨"
                    wind_context = "Breezy conditions"
                elif wind_speed >= 5:
                    wind_icon = "🍃"
                    wind_context = "Light breeze"
                else:
                    wind_icon = "🌿"
                    wind_context = "Calm conditions"
                
                message += f"""

🌬️ **WIND CONDITIONS**
├─ Speed: **{wind_speed} km/h** {wind_icon}
├─ Direction: **{wind_direction}** ({wind_degrees}°)"""
                
                if wind_gust and wind_gust > wind_speed:
                    message += f"\n├─ Gusts: **{wind_gust} km/h** 💨💨"
                
                message += f"\n└─ Conditions: {wind_context}"
            
            # Atmospheric pressure
            pressure = weather_data.get('pressure')
            pressure_tendency = weather_data.get('pressure_tendency')
            
            if pressure:
                if pressure >= 1020:
                    pressure_icon = "📈"
                    pressure_context = "High pressure - stable weather"
                elif pressure >= 1000:
                    pressure_icon = "📊"
                    pressure_context = "Normal pressure"
                else:
                    pressure_icon = "📉"
                    pressure_context = "Low pressure - unsettled weather"
                
                message += f"""

🏔️ **ATMOSPHERIC PRESSURE**
├─ Current: **{pressure} mb** {pressure_icon}"""
                
                if pressure_tendency:
                    tendency_emoji = "📈" if pressure_tendency == "Rising" else "📉" if pressure_tendency == "Falling" else "➡️"
                    message += f"\n├─ Trend: **{tendency_emoji} {pressure_tendency}**"
                
                message += f"\n└─ Conditions: {pressure_context}"
            
            # Visibility and clouds
            visibility = weather_data.get('visibility')
            cloud_cover = weather_data.get('cloud_cover')
            ceiling = weather_data.get('ceiling')
            
            message += f"""

👁️ **VISIBILITY & CLOUDS**"""
            
            if visibility:
                if visibility >= 10:
                    vis_context = "🌟 Excellent visibility!"
                elif visibility >= 5:
                    vis_context = "👀 Good visibility"
                elif visibility >= 2:
                    vis_context = "🌫️ Moderate visibility"
                else:
                    vis_context = "🌁 Poor visibility"
                message += f"\n├─ Visibility: **{visibility} km** {vis_context}"
            
            if cloud_cover is not None:
                if cloud_cover >= 90:
                    cloud_context = "☁️ Overcast skies"
                elif cloud_cover >= 70:
                    cloud_context = "🌥️ Mostly cloudy"
                elif cloud_cover >= 30:
                    cloud_context = "⛅ Partly cloudy"
                else:
                    cloud_context = "☀️ Clear skies"
                message += f"\n├─ Cloud Cover: **{cloud_cover}%** {cloud_context}"
            
            if ceiling:
                message += f"\n└─ Cloud Ceiling: **{ceiling} m**"
            
            # UV Index
            uv_index = weather_data.get('uv_index')
            uv_index_float = weather_data.get('uv_index_float')
            uv_text = weather_data.get('uv_text', 'N/A')
            
            if uv_index is not None:
                uv_emoji = self.get_uv_emoji(uv_index)
                
                if uv_index >= 11:
                    uv_advice = "🚨 EXTREME - Avoid sun exposure!"
                elif uv_index >= 8:
                    uv_advice = "🧴 Very High - Sunscreen essential!"
                elif uv_index >= 6:
                    uv_advice = "🕶️ High - Protection recommended"
                elif uv_index >= 3:
                    uv_advice = "☂️ Moderate - Some protection needed"
                else:
                    uv_advice = "😌 Low - Minimal protection needed"
                
                message += f"""

☀️ **UV INDEX & SUN PROTECTION**
├─ UV Level: **{uv_index}** ({uv_text}) {uv_emoji}"""
                
                if uv_index_float and uv_index_float != uv_index:
                    message += f"\n├─ Precise: **{uv_index_float}**"
                
                message += f"\n└─ Advice: {uv_advice}"
            
            # Precipitation data
            has_precip_data = any([
                weather_data.get('precip_1hr'),
                weather_data.get('precip_past_hour'),
                weather_data.get('precip_past_24hrs')
            ])
            
            if has_precip_data:
                message += f"""

🌧️ **PRECIPITATION SUMMARY**"""
                
                if weather_data.get('precip_past_hour'):
                    message += f"\n├─ Past Hour: **{weather_data.get('precip_past_hour')} mm**"
                
                if weather_data.get('precip_past_3hrs'):
                    message += f"\n├─ Past 3 Hours: **{weather_data.get('precip_past_3hrs')} mm**"
                
                if weather_data.get('precip_past_6hrs'):
                    message += f"\n├─ Past 6 Hours: **{weather_data.get('precip_past_6hrs')} mm**"
                
                if weather_data.get('precip_past_12hrs'):
                    message += f"\n├─ Past 12 Hours: **{weather_data.get('precip_past_12hrs')} mm**"
                
                if weather_data.get('precip_past_24hrs'):
                    message += f"\n└─ Past 24 Hours: **{weather_data.get('precip_past_24hrs')} mm**"
            
            # Footer with timestamp and links
            current_time = datetime.now().strftime('%H:%M')
            current_date = datetime.now().strftime('%d %B %Y')
            
            # Weather tips based on conditions
            weather_tips = []
            if weather_data.get('temperature', 0) > 35:
                weather_tips.append("🥤 Stay hydrated!")
            if weather_data.get('humidity', 0) > 80:
                weather_tips.append("💨 Use fans for comfort!")
            if weather_data.get('wind_speed', 0) > 30:
                weather_tips.append("🏠 Secure loose objects!")
            if weather_data.get('uv_index', 0) > 7:
                weather_tips.append("🧴 Apply sunscreen!")
            if weather_data.get('has_precipitation'):
                weather_tips.append("☂️ Carry an umbrella!")
            
            if not weather_tips:
                weather_tips = ["🌟 Perfect weather for outdoor activities!"]
            
            message += f"""

══════════════════════════════
📅 **{current_date}**
⏰ **Last Update:** {current_time}
💡 **Weather Tips:** {' '.join(weather_tips[:2])}
══════════════════════════════

🏘️ **Kandugula Village Weather Station**
📡 *Powered by AccuWeather API*
🤖 *Fresh updates every hour*
🔗 *Full details: {weather_data.get('mobile_link', 'AccuWeather.com')}*"""
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting comprehensive weather message: {e}")
            return f"❌ Error formatting weather data: {str(e)}"
    
    def get_weather_emoji(self, condition):
        """Get appropriate emoji for weather condition"""
        condition_lower = condition.lower()
        
        if 'sunny' in condition_lower:
            return '☀️'
        elif 'clear' in condition_lower:
            return '🌞' if datetime.now().hour < 18 else '🌙'
        elif 'partly cloudy' in condition_lower:
            return '⛅'
        elif 'mostly cloudy' in condition_lower:
            return '🌥️'
        elif 'cloudy' in condition_lower:
            return '☁️'
        elif 'rain' in condition_lower:
            return '🌧️'
        elif 'shower' in condition_lower:
            return '🚿'
        elif 'thunder' in condition_lower:
            return '⛈️'
        elif 'snow' in condition_lower:
            return '❄️'
        elif 'fog' in condition_lower or 'mist' in condition_lower:
            return '🌫️'
        elif 'hazy' in condition_lower:
            return '🌫️'
        elif 'windy' in condition_lower:
            return '💨'
        else:
            return '🌤️'
    
    def get_uv_emoji(self, uv_index):
        """Get appropriate emoji for UV index"""
        if uv_index <= 2:
            return '🟢'  # Low
        elif uv_index <= 5:
            return '🟡'  # Moderate
        elif uv_index <= 7:
            return '🟠'  # High
        elif uv_index <= 10:
            return '🔴'  # Very High
        else:
            return '🟣'  # Extreme

# Create weather service instance
weather_service = WeatherService()

@mcp.tool(
    name='get_current_weather',
    description="Get comprehensive current weather conditions for Kandugula village from AccuWeather"
)
def get_current_weather() -> str:
    """Get current weather conditions with detailed information"""
    try:
        weather_data = weather_service.get_weather_data()
        if weather_data:
            return weather_service.format_weather_message(weather_data)
        else:
            return "❌ Failed to fetch weather data from AccuWeather API"
    except Exception as e:
        logger.error(f"Error in get_current_weather: {e}")
        return f"❌ Error getting weather data: {str(e)}"

@mcp.tool(
    name='get_weather_summary',
    description="Get a brief weather summary for Kandugula village"
)
def get_weather_summary() -> str:
    """Get a brief weather summary"""
    try:
        weather_data = weather_service.get_weather_data()
        if not weather_data:
            return "❌ Failed to fetch weather data from AccuWeather API"
        
        temp = weather_data.get('temperature', 'N/A')
        temp_unit = weather_data.get('temperature_unit', 'C')
        condition = weather_data.get('condition', 'N/A')
        humidity = weather_data.get('humidity', 'N/A')
        wind_speed = weather_data.get('wind_speed', 'N/A')
        
        weather_emoji = weather_service.get_weather_emoji(condition)
        
        summary = f"""🌤️ **KANDUGULA WEATHER SUMMARY**
        
{weather_emoji} **Current:** {condition}
🌡️ **Temperature:** {temp}°{temp_unit}
💧 **Humidity:** {humidity}%
💨 **Wind:** {wind_speed} km/h
        
⏰ **Updated:** {datetime.now().strftime('%H:%M')}"""
        
        return summary
        
    except Exception as e:
        logger.error(f"Error in get_weather_summary: {e}")
        return f"❌ Error getting weather summary: {str(e)}"

@mcp.tool(
    name='get_weather_by_location',
    description="Get weather data for a specific location using AccuWeather location key"
)
def get_weather_by_location(location_key: str = Field(description="AccuWeather location key")) -> str:
    """Get weather data for a specific location"""
    try:
        # Temporarily override the location key
        original_key = weather_service.location_key
        weather_service.location_key = location_key
        
        weather_data = weather_service.get_weather_data()
        
        # Restore original location key
        weather_service.location_key = original_key
        
        if weather_data:
            return weather_service.format_weather_message(weather_data)
        else:
            return f"❌ Failed to fetch weather data for location key: {location_key}"
            
    except Exception as e:
        logger.error(f"Error in get_weather_by_location: {e}")
        return f"❌ Error getting weather data for location {location_key}: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='sse')
