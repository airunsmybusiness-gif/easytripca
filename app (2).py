import streamlit as st
import streamlit.components.v1 as components
import csv
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="EasyTrip Canada 🇨🇦 | Facebook-First Trip Planner",
    page_icon="🍁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'unlocked' not in st.session_state:
    st.session_state.unlocked = False
if 'email_submitted' not in st.session_state:
    st.session_state.email_submitted = False
if 'show_itinerary' not in st.session_state:
    st.session_state.show_itinerary = False

# Destination data with deterministic itineraries
DESTINATIONS = {
    "Banff, Alberta": {
        "emoji": "🏔️",
        "activities": ["Lake Louise sunrise", "Banff Gondola ride", "Johnston Canyon hike", "Hot springs soak", "Bow Falls walk", "Cave and Basin NHS", "Vermilion Lakes sunset", "Moraine Lake visit", "Sunshine Meadows hike", "Wildlife safari"],
        "food": ["Grizzly House fondue", "Park Distillery lunch", "Maple bacon poutine", "Rocky Mountain breakfast", "Elk steak dinner"],
        "tips": ["Book Lake Louise parking early", "Bring layers - weather changes fast", "Wildlife is everywhere - keep distance"]
    },
    "Jasper, Alberta": {
        "emoji": "🦌",
        "activities": ["Maligne Lake cruise", "Columbia Icefield skywalk", "Athabasca Falls", "Pyramid Lake kayak", "Jasper SkyTram", "Miette Hot Springs", "Valley of Five Lakes", "Stargazing at Dark Sky Preserve", "Wildlife watching", "Sunwapta Falls"],
        "food": ["Evil Dave's Grill", "Downstream Restaurant", "Bear's Paw Bakery", "Jasper Brewing Co", "Olive Bistro"],
        "tips": ["Gas up before leaving town", "Dark Sky Preserve is magical", "Elk roam downtown - be careful"]
    },
    "Vancouver, BC": {
        "emoji": "🌊",
        "activities": ["Stanley Park seawall", "Granville Island market", "Capilano Suspension Bridge", "Gastown steam clock", "English Bay sunset", "Grouse Mountain", "Science World", "VanDusen Gardens", "Chinatown tour", "Seabus to North Van"],
        "food": ["Japadog on Robson", "Salmon n' Bannock", "Miku for sushi", "Tacofino tacos", "Revolver coffee"],
        "tips": ["Bring an umbrella always", "Transit is excellent", "Book Capilano tickets online"]
    },
    "Victoria, BC": {
        "emoji": "🌸",
        "activities": ["Butchart Gardens", "Inner Harbour walk", "Royal BC Museum", "Fisherman's Wharf", "Craigdarroch Castle", "Beacon Hill Park", "Whale watching tour", "Afternoon tea at Empress", "Chinatown walk", "Oak Bay village"],
        "food": ["Red Fish Blue Fish", "10 Acres Bistro", "Jam Cafe brunch", "Pagliacci's", "Murchie's Tea"],
        "tips": ["Ferry fills up - book ahead", "Rent bikes for the seawall", "Butchart is worth the drive"]
    },
    "Whistler, BC": {
        "emoji": "⛷️",
        "activities": ["Peak 2 Peak Gondola", "Village stroll", "Lost Lake trails", "Scandinave Spa", "Zipline adventure", "Mountain biking", "Brandywine Falls", "Bungee jumping", "Golf at Fairmont", "Train Wreck hike"],
        "food": ["Peaked Pies", "Splitz Grill burgers", "Araxi Restaurant", "Purebread bakery", "Longhorn Saloon"],
        "tips": ["Sea to Sky Highway is stunning", "Book spa in advance", "Village is walkable"]
    },
    "Toronto, Ontario": {
        "emoji": "🏙️",
        "activities": ["CN Tower EdgeWalk", "Kensington Market", "Distillery District", "ROM museum", "Toronto Islands", "St. Lawrence Market", "Graffiti Alley", "Hockey Hall of Fame", "High Park", "AGO art gallery"],
        "food": ["Peameal bacon sandwich", "Pai Northern Thai", "Canoe for views", "St. Lawrence peameal", "Carousel Bakery"],
        "tips": ["Get a Presto card", "Islands are car-free paradise", "Weekends at markets are busy"]
    },
    "Niagara Falls, Ontario": {
        "emoji": "💧",
        "activities": ["Journey Behind the Falls", "Hornblower cruise", "Niagara-on-the-Lake", "Whirlpool Aero Car", "Clifton Hill games", "Wine tour", "Butterfly Conservatory", "Skylon Tower dinner", "White Water Walk", "Floral Clock"],
        "food": ["Weinkeller restaurant", "Treadwell winery", "AG Inspired Cuisine", "Tide & Vine", "Benchmark Restaurant"],
        "tips": ["Canadian side has best views", "Wine country is 20min away", "Falls are lit at night"]
    },
    "Montreal, Quebec": {
        "emoji": "🥐",
        "activities": ["Old Montreal walk", "Mount Royal hike", "Notre-Dame Basilica", "Jean-Talon Market", "Mile End murals", "Plateau stroll", "La Ronde", "Biodome visit", "Underground City", "Lachine Canal bike"],
        "food": ["Schwartz's smoked meat", "Fairmount bagels", "Poutine at La Banquise", "Joe Beef", "Olive et Gourmando"],
        "tips": ["Everyone speaks French first", "Metro is fast and clean", "Bagel debate is real"]
    },
    "Quebec City, Quebec": {
        "emoji": "🏰",
        "activities": ["Château Frontenac", "Old Quebec walls walk", "Montmorency Falls", "Petit Champlain shops", "Plains of Abraham", "Île d'Orléans drive", "Toboggan run", "Ferry to Lévis", "Citadelle tour", "Quartier Petit Champlain"],
        "food": ["Aux Anciens Canadiens", "Chez Ashton poutine", "Le Clocher Penché", "Paillard cafe", "Restaurant Légende"],
        "tips": ["Most European city in NA", "Winter is magical here", "Wear good walking shoes"]
    },
    "Halifax, Nova Scotia": {
        "emoji": "⚓",
        "activities": ["Peggy's Cove", "Halifax Citadel", "Waterfront boardwalk", "Maritime Museum", "Public Gardens", "Alexander Keith's tour", "Fisherman's Cove", "Point Pleasant Park", "Art Gallery of NS", "Dartmouth ferry"],
        "food": ["Lobster at Bicycle Thief", "Fish and chips at John's", "Donairs downtown", "Cheese curds at Stubborn Goat", "Oysters at Five Fishermen"],
        "tips": ["Donairs are Halifax invention", "Peggy's Cove waves are dangerous", "East Coast time is 1hr ahead"]
    },
    "Calgary, Alberta": {
        "emoji": "🤠",
        "activities": ["Calgary Tower", "Stephen Avenue walk", "Heritage Park", "Calgary Zoo", "Prince's Island Park", "Studio Bell music centre", "Inglewood shops", "Peace Bridge", "TELUS Spark", "Fish Creek Park"],
        "food": ["Charcut Roast House", "River Cafe", "Clive Burger", "OEB Breakfast", "Native Tongues tacos"],
        "tips": ["Chinooks change weather fast", "Gateway to Rockies", "Stampede is in July"]
    },
    "Ottawa, Ontario": {
        "emoji": "🍁",
        "activities": ["Parliament Hill tour", "Rideau Canal walk", "ByWard Market", "National Gallery", "Canadian War Museum", "Gatineau Park hike", "Changing of the Guard", "Museum of History", "Tulip Festival", "Sparks Street"],
        "food": ["BeaverTails pastry", "Beckta Dining", "Play Food & Wine", "Whalesbone oysters", "Supply and Demand"],
        "tips": ["Canal freezes for skating", "Gatineau is in Quebec", "Tulip Festival in May"]
    }
}

TRAVELER_TIPS = {
    "Solo": ["Join free walking tours to meet people", "Hostels have great social vibes", "Solo dining at bars is totally normal here"],
    "Couple": ["Book sunset experiences", "Spa days are romantic here", "Ask about couples' packages"],
    "Family": ["Many attractions have family passes", "Pack snacks - kids get hungry", "Check for kid-free hours at pools"],
    "Group": ["Book group rates in advance", "Designate a meeting spot daily", "Split bills with apps like Splitwise"]
}


def save_email(email, source="landing_page"):
    """Save email to CSV file"""
    file_exists = os.path.isfile('emails.csv')
    with open('emails.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['email', 'source', 'timestamp'])
        writer.writerow([email, source, datetime.now().isoformat()])


def generate_itinerary(destination, days, traveler_type):
    """Generate deterministic itinerary based on inputs"""
    dest_data = DESTINATIONS.get(destination, list(DESTINATIONS.values())[0])
    itinerary = []
    
    activities = dest_data["activities"]
    foods = dest_data["food"]
    tips = dest_data["tips"]
    
    times = ["8:00 AM", "10:30 AM", "1:00 PM", "3:30 PM", "6:00 PM", "8:00 PM"]
    
    for day in range(1, days + 1):
        day_activities = []
        
        activity_idx = (day - 1) % len(activities)
        day_activities.append({"time": times[0], "activity": activities[activity_idx], "type": "activity"})
        
        activity_idx = (day + 1) % len(activities)
        day_activities.append({"time": times[1], "activity": activities[activity_idx], "type": "activity"})
        
        food_idx = (day - 1) % len(foods)
        day_activities.append({"time": times[2], "activity": f"Lunch at {foods[food_idx]}", "type": "food"})
        
        activity_idx = (day + 3) % len(activities)
        day_activities.append({"time": times[3], "activity": activities[activity_idx], "type": "activity"})
        
        activity_idx = (day + 5) % len(activities)
        day_activities.append({"time": times[4], "activity": activities[activity_idx], "type": "activity"})
        
        food_idx = (day) % len(foods)
        day_activities.append({"time": times[5], "activity": f"Dinner at {foods[food_idx]}", "type": "food"})
        
        tip_idx = (day - 1) % len(tips)
        traveler_tip_idx = (day - 1) % len(TRAVELER_TIPS[traveler_type])
        
        itinerary.append({
            "day": day,
            "activities": day_activities,
            "tip": tips[tip_idx],
            "traveler_tip": TRAVELER_TIPS[traveler_type][traveler_tip_idx]
        })
    
    return itinerary


# Inject base CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

* { font-family: 'Plus Jakarta Sans', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0f0f23 100%);
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0f0f23 100%);
}

[data-testid="stHeader"] {
    background: transparent;
}

.stTextInput > div > div > input {
    background: rgba(255,255,255,0.1) !important;
    border: 2px solid rgba(255,255,255,0.2) !important;
    border-radius: 12px !important;
    color: white !important;
    padding: 15px 20px !important;
}

.stTextInput > div > div > input:focus {
    border-color: #4ecdc4 !important;
}

.stButton > button {
    background: linear-gradient(135deg, #ff6b6b, #ff8e8e) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 15px 40px !important;
    font-weight: 700 !important;
    width: 100% !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 30px rgba(255,107,107,0.4) !important;
}

.stSelectbox > div > div {
    background: rgba(255,255,255,0.1) !important;
    border: 2px solid rgba(255,255,255,0.2) !important;
    border-radius: 12px !important;
}

.stSelectbox label, .stSlider label, .stRadio label {
    color: white !important;
}

div[data-testid="stMarkdownContainer"] p {
    color: rgba(255,255,255,0.8);
}

h1, h2, h3 { color: white !important; }

.stRadio > div {
    background: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 12px;
}

.stSlider > div > div > div > div {
    background: #4ecdc4 !important;
}
</style>
""", unsafe_allow_html=True)

# HERO SECTION using components.html for reliable rendering
components.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
* { font-family: 'Plus Jakarta Sans', sans-serif; margin: 0; padding: 0; box-sizing: border-box; }
body { background: transparent; }
</style>

<div style="text-align: center; padding: 40px 20px;">
    <!-- Animated mesh gradient -->
    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; pointer-events: none;
        background: radial-gradient(ellipse at 20% 20%, rgba(255, 107, 107, 0.15) 0%, transparent 50%),
                    radial-gradient(ellipse at 80% 20%, rgba(78, 205, 196, 0.15) 0%, transparent 50%),
                    radial-gradient(ellipse at 40% 80%, rgba(199, 125, 255, 0.15) 0%, transparent 50%);
        animation: meshMove 15s ease-in-out infinite;">
    </div>
    
    <!-- Badge -->
    <div style="display: inline-block; background: linear-gradient(135deg, rgba(255,107,107,0.2), rgba(78,205,196,0.2)); 
        border: 1px solid rgba(255,255,255,0.2); padding: 10px 24px; border-radius: 50px; color: #fff; 
        font-size: 14px; font-weight: 600; margin-bottom: 25px; backdrop-filter: blur(10px);">
        🍁 #1 Facebook-First Trip Planner for Canadians
    </div>
    
    <!-- Headline -->
    <h1 style="font-size: 3.2rem; font-weight: 800; background: linear-gradient(135deg, #fff 0%, #e0e0ff 50%, #fff 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
        line-height: 1.15; margin-bottom: 20px;">
        Plan Your Perfect<br>Canadian Adventure
    </h1>
    
    <!-- Subtitle -->
    <p style="font-size: 1.2rem; color: rgba(255,255,255,0.7); margin-bottom: 35px; line-height: 1.6;">
        Create stunning, shareable trip itineraries in seconds.<br>
        Designed for Facebook Pages, Reels & Carousel posts.
    </p>
    
    <!-- Social Proof Avatars -->
    <div style="display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 30px;">
        <div style="display: flex;">
            <div style="width: 44px; height: 44px; border-radius: 50%; border: 3px solid #1a1a3e; 
                display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; 
                color: white; background: linear-gradient(135deg, #ff6b6b, #ff8e8e);">AB</div>
            <div style="width: 44px; height: 44px; border-radius: 50%; border: 3px solid #1a1a3e; margin-left: -10px;
                display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; 
                color: white; background: linear-gradient(135deg, #4ecdc4, #6ee7de);">BC</div>
            <div style="width: 44px; height: 44px; border-radius: 50%; border: 3px solid #1a1a3e; margin-left: -10px;
                display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; 
                color: white; background: linear-gradient(135deg, #c77dff, #d9a8ff);">ON</div>
            <div style="width: 44px; height: 44px; border-radius: 50%; border: 3px solid #1a1a3e; margin-left: -10px;
                display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; 
                color: white; background: linear-gradient(135deg, #ffbe76, #ffd9a8);">QC</div>
        </div>
        <div style="color: rgba(255,255,255,0.8); font-size: 14px;">
            <span style="color: #4ecdc4; font-weight: 700;">2,400+</span> trips planned across Canada
        </div>
    </div>
    
    <!-- CTA Buttons -->
    <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
        <a href="#" style="display: inline-block; padding: 16px 32px; border-radius: 12px; font-weight: 700; 
            font-size: 16px; text-decoration: none; background: linear-gradient(135deg, #ff6b6b, #ff8e8e); 
            color: white; box-shadow: 0 10px 30px rgba(255,107,107,0.3);">🗺️ Start Planning Free</a>
        <a href="#" style="display: inline-block; padding: 16px 32px; border-radius: 12px; font-weight: 700; 
            font-size: 16px; text-decoration: none; background: rgba(255,255,255,0.1); color: white; 
            border: 2px solid rgba(255,255,255,0.2);">See How It Works</a>
    </div>
</div>

<style>
@keyframes meshMove {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}
</style>
""", height=580)

# Floating preview card
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    components.html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    </style>
    <div style="background: linear-gradient(145deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        border: 1px solid rgba(255,255,255,0.15); border-radius: 24px; padding: 30px;
        backdrop-filter: blur(20px); box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        transition: transform 0.5s ease; max-width: 400px; margin: 0 auto;"
        onmouseover="this.style.transform='perspective(1000px) rotateY(-5deg) rotateX(5deg)'"
        onmouseout="this.style.transform='none'">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px; 
            padding-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1);">
            <div style="width: 12px; height: 12px; border-radius: 50%; background: #ff6b6b;"></div>
            <div style="width: 12px; height: 12px; border-radius: 50%; background: #ffbe76;"></div>
            <div style="width: 12px; height: 12px; border-radius: 50%; background: #4ecdc4;"></div>
            <span style="color: white; font-weight: 600; font-size: 14px; margin-left: 10px;">Sample Itinerary</span>
        </div>
        <div style="font-size: 24px; font-weight: 700; color: white; margin-bottom: 15px;">🏔️ Banff Adventure</div>
        <div>
            <span style="display: inline-block; background: rgba(78,205,196,0.2); color: #4ecdc4; 
                padding: 6px 14px; border-radius: 20px; font-size: 13px; margin-right: 8px;">3 Days</span>
            <span style="display: inline-block; background: rgba(78,205,196,0.2); color: #4ecdc4; 
                padding: 6px 14px; border-radius: 20px; font-size: 13px; margin-right: 8px;">Couple</span>
            <span style="display: inline-block; background: rgba(78,205,196,0.2); color: #4ecdc4; 
                padding: 6px 14px; border-radius: 20px; font-size: 13px;">Nature</span>
        </div>
        <div style="margin-top: 20px; color: rgba(255,255,255,0.7); font-size: 14px; line-height: 1.8;">
            ✓ Lake Louise sunrise<br>
            ✓ Banff Gondola ride<br>
            ✓ Hot springs evening<br>
            <span style="color: #4ecdc4;">+ 6 more activities...</span>
        </div>
    </div>
    """, height=320)

# HOW IT WORKS SECTION
components.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
* { font-family: 'Plus Jakarta Sans', sans-serif; }
</style>
<div style="padding: 60px 20px 30px; text-align: center;">
    <h2 style="font-size: 2.2rem; font-weight: 700; color: white; margin-bottom: 15px;">How It Works</h2>
    <p style="font-size: 1.1rem; color: rgba(255,255,255,0.6); margin-bottom: 40px;">Three simple steps to your dream Canadian trip</p>
    
    <div style="display: flex; justify-content: center; gap: 25px; flex-wrap: wrap;">
        <div style="background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
            border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 35px 25px; 
            text-align: center; flex: 1; min-width: 250px; max-width: 300px;">
            <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
                border-radius: 50%; display: flex; align-items: center; justify-content: center;
                font-size: 24px; font-weight: 800; color: white; margin: 0 auto 20px;">1</div>
            <h3 style="font-size: 1.2rem; font-weight: 700; color: white; margin-bottom: 12px;">Pick Your Destination</h3>
            <p style="color: rgba(255,255,255,0.6); font-size: 14px;">Choose from 12 stunning Canadian destinations, from Banff to Quebec City.</p>
        </div>
        
        <div style="background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
            border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 35px 25px; 
            text-align: center; flex: 1; min-width: 250px; max-width: 300px;">
            <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #4ecdc4, #6ee7de);
                border-radius: 50%; display: flex; align-items: center; justify-content: center;
                font-size: 24px; font-weight: 800; color: #0f0f23; margin: 0 auto 20px;">2</div>
            <h3 style="font-size: 1.2rem; font-weight: 700; color: white; margin-bottom: 12px;">Customize Your Trip</h3>
            <p style="color: rgba(255,255,255,0.6); font-size: 14px;">Set your travel days and style. Solo adventure? Family fun? We've got you.</p>
        </div>
        
        <div style="background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
            border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 35px 25px; 
            text-align: center; flex: 1; min-width: 250px; max-width: 300px;">
            <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #c77dff, #d9a8ff);
                border-radius: 50%; display: flex; align-items: center; justify-content: center;
                font-size: 24px; font-weight: 800; color: white; margin: 0 auto 20px;">3</div>
            <h3 style="font-size: 1.2rem; font-weight: 700; color: white; margin-bottom: 12px;">Share on Facebook</h3>
            <p style="color: rgba(255,255,255,0.6); font-size: 14px;">Get a beautiful, screenshot-ready itinerary perfect for posts and stories.</p>
        </div>
    </div>
</div>
""", height=420)

# WHY FACEBOOK-FIRST SECTION
components.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
* { font-family: 'Plus Jakarta Sans', sans-serif; }
</style>
<div style="background: linear-gradient(145deg, rgba(78,205,196,0.1), rgba(199,125,255,0.1));
    border: 1px solid rgba(255,255,255,0.1); border-radius: 24px; padding: 40px; margin: 20px;">
    <h2 style="font-size: 1.8rem; font-weight: 700; color: white; margin-bottom: 30px;">📱 Why Facebook-First?</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 25px;">
        <div style="display: flex; align-items: flex-start; gap: 15px;">
            <span style="font-size: 28px;">📐</span>
            <div>
                <h4 style="color: white; font-weight: 600; margin: 0 0 5px 0;">Perfect Dimensions</h4>
                <p style="color: rgba(255,255,255,0.6); font-size: 14px; margin: 0;">Sized for FB posts, Stories & Reels without cropping</p>
            </div>
        </div>
        <div style="display: flex; align-items: flex-start; gap: 15px;">
            <span style="font-size: 28px;">🎨</span>
            <div>
                <h4 style="color: white; font-weight: 600; margin: 0 0 5px 0;">Eye-Catching Design</h4>
                <p style="color: rgba(255,255,255,0.6); font-size: 14px; margin: 0;">Bold colours that pop in crowded feeds</p>
            </div>
        </div>
        <div style="display: flex; align-items: flex-start; gap: 15px;">
            <span style="font-size: 28px;">📸</span>
            <div>
                <h4 style="color: white; font-weight: 600; margin: 0 0 5px 0;">Screenshot Ready</h4>
                <p style="color: rgba(255,255,255,0.6); font-size: 14px; margin: 0;">Just screenshot and post - no editing needed</p>
            </div>
        </div>
        <div style="display: flex; align-items: flex-start; gap: 15px;">
            <span style="font-size: 28px;">🔗</span>
            <div>
                <h4 style="color: white; font-weight: 600; margin: 0 0 5px 0;">Page Tab Ready</h4>
                <p style="color: rgba(255,255,255,0.6); font-size: 14px; margin: 0;">Embed directly in your Facebook Page as a tab</p>
            </div>
        </div>
    </div>
</div>
""", height=280)

# PLANNER SECTION HEADER
components.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
* { font-family: 'Plus Jakarta Sans', sans-serif; }
</style>
<div style="padding: 50px 20px 20px; text-align: center;">
    <h2 style="font-size: 2.2rem; font-weight: 700; color: white; margin-bottom: 15px;">🗺️ Plan Your Trip</h2>
    <p style="font-size: 1.1rem; color: rgba(255,255,255,0.6);">Create your personalized Canadian adventure</p>
</div>
""", height=140)

# Check if planner is locked
if not st.session_state.unlocked:
    # Email capture box
    components.html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    </style>
    <div style="background: linear-gradient(145deg, rgba(255,107,107,0.15), rgba(199,125,255,0.15));
        border: 2px solid rgba(255,107,107,0.3); border-radius: 24px; padding: 35px; text-align: center; margin: 0 20px;">
        <h3 style="font-size: 1.5rem; font-weight: 700; color: white; margin-bottom: 10px;">🔓 Unlock the Free Trip Planner</h3>
        <p style="color: rgba(255,255,255,0.7); margin-bottom: 20px;">Enter your email to get instant access + exclusive Canadian travel tips</p>
    </div>
    """, height=160)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input("Email", placeholder="your@email.com", label_visibility="collapsed")
        if st.button("🍁 Unlock Free Planner"):
            if email and "@" in email:
                save_email(email, "planner_unlock")
                st.session_state.unlocked = True
                st.session_state.email_submitted = True
                st.rerun()
            else:
                st.error("Please enter a valid email address")
    
    # Locked overlay
    components.html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    </style>
    <div style="background: linear-gradient(145deg, rgba(30,30,60,0.95), rgba(20,20,40,0.98));
        border: 2px dashed rgba(255,255,255,0.2); border-radius: 24px; padding: 60px 40px; 
        text-align: center; margin: 20px;">
        <div style="font-size: 60px; margin-bottom: 20px;">🔒</div>
        <h3 style="color: white; margin-bottom: 10px;">Trip Planner Locked</h3>
        <p style="color: rgba(255,255,255,0.6);">Enter your email above to unlock the full planner</p>
    </div>
    """, height=280)

else:
    # UNLOCKED PLANNER
    if st.session_state.email_submitted:
        st.success("✅ Welcome! Your planner is now unlocked. Start planning below!")
        st.session_state.email_submitted = False
    
    # Planner inputs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        destination = st.selectbox("🎯 Choose Destination", options=list(DESTINATIONS.keys()), index=0)
    
    with col2:
        days = st.slider("📅 Number of Days", 1, 10, 3)
    
    with col3:
        traveler_type = st.radio("👥 Traveler Type", options=["Solo", "Couple", "Family", "Group"], horizontal=True)
    
    if st.button("✨ Generate My Itinerary"):
        st.session_state.show_itinerary = True
    
    if st.session_state.show_itinerary:
        itinerary = generate_itinerary(destination, days, traveler_type)
        dest_emoji = DESTINATIONS[destination]["emoji"]
        
        # Build itinerary HTML
        itinerary_html = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        * {{ font-family: 'Plus Jakarta Sans', sans-serif; margin: 0; padding: 0; box-sizing: border-box; }}
        </style>
        <div style="background: linear-gradient(145deg, #1a1a3e, #0f0f23); border: 3px solid rgba(255,255,255,0.1);
            border-radius: 30px; padding: 25px; box-shadow: 0 30px 60px rgba(0,0,0,0.4); margin: 20px 0;">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, rgba(255,107,107,0.2), rgba(78,205,196,0.2));
                border-radius: 16px; padding: 25px; margin-bottom: 25px; text-align: center;">
                <div style="font-size: 2rem; font-weight: 800; color: white; margin-bottom: 10px;">
                    {dest_emoji} {destination}
                </div>
                <div style="color: rgba(255,255,255,0.7); font-size: 14px;">
                    <span>📅 {days} Days</span>
                    <span style="margin: 0 10px;">•</span>
                    <span>👥 {traveler_type}</span>
                    <span style="margin: 0 10px;">•</span>
                    <span>🍁 EasyTrip.ca</span>
                </div>
            </div>
        """
        
        for day_data in itinerary:
            itinerary_html += f"""
            <div style="background: linear-gradient(145deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
                border: 1px solid rgba(255,255,255,0.12); border-radius: 20px; padding: 20px; margin-bottom: 15px;">
                <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;
                    padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <div style="background: linear-gradient(135deg, #4ecdc4, #6ee7de); color: #0f0f23;
                        width: 45px; height: 45px; border-radius: 10px; display: flex; align-items: center;
                        justify-content: center; font-weight: 800; font-size: 18px;">{day_data['day']}</div>
                    <div style="color: white; font-size: 1.1rem; font-weight: 600;">Day {day_data['day']} Adventure</div>
                </div>
            """
            
            for activity in day_data['activities']:
                icon = "🍽️" if activity['type'] == 'food' else "✨"
                time_bg = "rgba(255,190,118,0.2)" if activity['type'] == 'food' else "rgba(255,107,107,0.2)"
                time_color = "#ffbe76" if activity['type'] == 'food' else "#ff8e8e"
                itinerary_html += f"""
                <div style="display: flex; align-items: center; gap: 12px; padding: 10px 0;
                    border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <span style="background: {time_bg}; color: {time_color}; padding: 4px 10px;
                        border-radius: 8px; font-size: 11px; font-weight: 600; min-width: 70px; text-align: center;">
                        {activity['time']}</span>
                    <span style="color: rgba(255,255,255,0.9); font-size: 14px;">{icon} {activity['activity']}</span>
                </div>
                """
            
            itinerary_html += f"""
                <div style="background: rgba(199,125,255,0.15); border-left: 4px solid #c77dff;
                    padding: 12px 15px; border-radius: 0 10px 10px 0; margin-top: 12px;">
                    <p style="color: rgba(255,255,255,0.8); font-size: 13px; margin-bottom: 6px;">
                        💡 <strong>Pro tip:</strong> {day_data['tip']}</p>
                    <p style="color: rgba(255,255,255,0.7); font-size: 13px;">
                        👤 <strong>{traveler_type} tip:</strong> {day_data['traveler_tip']}</p>
                </div>
            </div>
            """
        
        itinerary_html += """
            <div style="text-align: center; margin-top: 20px;">
                <span style="display: inline-block; padding: 12px 24px; border-radius: 10px;
                    background: rgba(255,255,255,0.1); color: white; font-weight: 600; font-size: 14px;
                    border: 1px solid rgba(255,255,255,0.2);">📸 Screenshot to share on Facebook</span>
            </div>
        </div>
        """
        
        # Calculate height based on number of days
        height = 350 + (days * 320)
        components.html(itinerary_html, height=height, scrolling=True)
        
        # Share reminder
        components.html("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        * { font-family: 'Plus Jakarta Sans', sans-serif; }
        </style>
        <div style="text-align: center; padding: 25px; background: rgba(255,255,255,0.05); 
            border-radius: 16px; margin: 20px 0;">
            <p style="color: rgba(255,255,255,0.8); margin-bottom: 10px;">
                📱 <strong>Share your trip!</strong> Screenshot this itinerary and post it to your Facebook page or story.</p>
            <p style="color: rgba(255,255,255,0.5); font-size: 13px;">
                Tag us @EasyTripCanada for a chance to be featured! 🍁</p>
        </div>
        """, height=120)

# FOOTER
components.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
* { font-family: 'Plus Jakarta Sans', sans-serif; }
</style>
<div style="text-align: center; padding: 40px 20px; margin-top: 40px; border-top: 1px solid rgba(255,255,255,0.1);">
    <p style="color: rgba(255,255,255,0.5); font-size: 14px; margin-bottom: 8px;">
        EasyTrip.ca 🇨🇦✨ · Designed for Facebook Page Tabs, Reels & carousels.</p>
    <p style="color: rgba(255,255,255,0.4); font-size: 12px;">Made with ❤️ for Canadian travellers</p>
</div>
""", height=120)
