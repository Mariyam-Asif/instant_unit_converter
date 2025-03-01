import streamlit as st
import pint
import speech_recognition as sr
from dotenv import load_dotenv
import pyaudio

load_dotenv()
ureg = pint.UnitRegistry()

st.set_page_config(page_title="Instant Unit Converter", page_icon="🔁", layout="wide")
if "history" not in st.session_state:
    st.session_state.history = []
if "from_unit" not in st.session_state:
    st.session_state.from_unit = "meters" # Default value
if "to_unit" not in st.session_state:
    st.session_state.to_unit = "kilometers" # Default value

# Custom CSS for styling
def load_css():
    st.markdown(
        """
    <style>
        body { background-color: #1E1E1E; color: white; font-family: Arial, sans-serif; }
        .main-title { font-size: 36px; font-weight: bold; text-align: center; color: white; }
        .tagline { font-size: 20px; text-align: center; color: #B0B0B0; margin-bottom: 20px; }
        .stButton>button { background-color: #007BFF; color: white; border-radius: 20px; font-size: 18px; transition: all 0.3s ease-in-out; border:none;}
        .stButton>button:hover {
            background-color: #0056b3 !important;
            border-color: #0056b3 !important;
            color: white !important;
            transform: scale(1.05); 
            box-shadow: 0px 0px 10px rgba(0, 123, 255, 0.7) !important;
        }
        .conversion-history { 
            background: #222;
            color: white;
            padding: 10px;
            border-radius: 10px;
            margin-top: 10px;
            font-size: 18px;
        }
        select, input {
            background: #333;
            color: white;
            font-size:18px;
            border-radius: 20px;
            border: 1px solid #007BFF;
            padding: 5px;
            outline:none;
        }
        select:hover, input:hover {
            border-color: #0056b3;
        }
        select:focus, input:focus {
            border-color: #007BFF;
            background: #333;
            color: white;
        }
        .success-message {
            background: linear-gradient(90deg, #005f9e, #0096c7);
            color: white;
            font-size: 20px;
            padding: 12px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            box-shadow: 0px 0px 15px rgba(0, 150, 199, 0.5);
            animation: glow 2s infinite alternate;
        }
        @keyframes glow {
            0% {
                box-shadow: 0px 0px 10px rgba(0, 150, 199, 0.3);
            }
            100% {
                box-shadow: 0px 0px 20px rgab(0, 150, 199, 0.6);
            }
        }
    </style>
    
        """,
        unsafe_allow_html=True,
    )

load_css()

st.markdown("<h1 class='main-title'><span style='color: #007BFF;'>Instant</span> Unit Converter</h1>", unsafe_allow_html=True)
st.markdown("<p class='tagline'>Precision, speed, and seamless tracking— all in one powerful tool.<br>Convert smarter, not harder! </p>", unsafe_allow_html=True)

unit_options = {
    "Length": ["meters", "kilometers", "miles", "feet", "inches", "centimeters", "millimeters", "yards"],
    "Weight": ["grams", "kilograms", "pounds", "ounces", "stones", "milligrams"],
    "Volume": ["liters", "milliliters", "gallons", "cubic meters", "cubic feet"],
    "Speed": ["meter/second", "kilometer/hour", "mile/hour", "foot/second"],
    "Time": ["seconds", "minutes", "hours", "days", "weeks", "months", "years"],
    "Temperature": ["celsius", "fahrenheit", "kelvin"],
    "Energy": ["joules", "kilojoules", "calories", "kilocalories", "watt-hours"],
    "Power": ["watts", "kilowatts", "horsepower"],
    "Pressure": ["pascals", "kilopascals", "bar", "atm", "psi"],
    "Data": ["bit", "byte", "kilobyte", "megabyte", "gigabyte", "terabyte"],
    "Fuel Economy": ["mpg", "km/l", "1/100km"],
    "Angle": ["degrees", "radians"]
}

selected_category = st.selectbox("Choose a category:", list(unit_options.keys()))
units = unit_options[selected_category]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.session_state.from_unit = st.selectbox("From", units, index=units.index(st.session_state.from_unit) if st.session_state.from_unit in units else 0)
with col2:
    st.session_state.to_unit = st.selectbox("To", units, index=units.index(st.session_state.to_unit) if st.session_state.to_unit in units else 1)
with col3:
    value = st.number_input("Enter value to convert:", min_value=0.0, format="%.2f", key="value", value=st.session_state.get("spoken_value", 0.0))
with col4:
#Speech Recognition
    if st.button("Voice Input"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Adjusting for ambient noise, please wait...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            st.info("Listening...Speak now.")
            try:
                audio = recognizer.listen(source, timeout=6)
                spoken_value = recognizer.recognize_google(audio)
                st.session_state.spoken_value = float(spoken_value)
                st.rerun()
                st.success(f"Recognized: {st.session_state.spoken_value}")
            except sr.UnknownValueError:
                st.error("Could not understand speech. Try speaking more clearly.")
            except sr.RequestError:
                st.error("Could not request results from Google Speech Recognition. Check your internet connection.")
            except ValueError:
                st.error("Could not convert speech to a number. Try again.")

# Conversion Logic 
def convert_units(value, from_unit, to_unit, category):
    try:
        if category == "Temperature":
            conversions = {
                ("celsius", "fahrenheit"): lambda x: (x * 9/5) + 32,
                ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
                ("celsius", "kelvin"): lambda x: x + 273.15,
                ("kelvin", "celsius"): lambda x: x - 273.15,
                ("fahrenheit", "kelvin"): lambda x: (x - 32) * 5/9 + 273.15,
                ("kelvin", "fahrenheit"): lambda x: (x - 273.15) * 9/5 + 32,
            }
            return conversions.get((from_unit, to_unit), lambda x: x)(value)
        return value * ureg(from_unit).to(to_unit).magnitude
    except:
        return "Conversion Error"

col3, col4 = st.columns([3,1])
with col3:
# Conversion Button
    if st.button("Convert", key="convert", help="Convert units", use_container_width=True):
        try:
            result = convert_units(value, st.session_state.from_unit, st.session_state.to_unit, selected_category)
            success_message = f"<p class='success-message'>{value} {st.session_state.from_unit} = {result:.2f} {st.session_state.to_unit}</p>"
            st.markdown(success_message, unsafe_allow_html=True)
            st.session_state.history.append((value, st.session_state.from_unit, result, st.session_state.to_unit))
            
        except Exception as e:
            st.error(f"Error: {e}")
    
with col4:
    if st.button("Swap Units"):
        st.session_state.from_unit, st.session_state.to_unit = st.session_state.to_unit, st.session_state.from_unit
        st.rerun()

st.markdown("### Conversion History")
for item in st.session_state.history[-5:]: # Shows last 5 conversions
    st.markdown(
        f"<div class='conversion-history'>{item[0]} {item[1]} = {item[2]:.2f} {item[3]}</div>", unsafe_allow_html=True,
    )

