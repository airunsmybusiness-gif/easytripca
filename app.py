import streamlit as st
import requests
from datetime import datetime

# Page config - MUST BE FIRST
st.set_page_config(
    page_title="EasyTrip Canada 🇨🇦",
    page_icon="🍁",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'unlocked' not in st.session_state:
    st.session_state.unlocked = False
if 'email_submitted' not in st.session_state:
    st.session_state.email_submitted = False
if 'show_itinerary' not in st.session_state:
    st.session_state.show_itinerary = False

# Destination data
DESTINATIONS = {
    "Banff, Alberta": {
        "emoji": "🏔️",
        "activities": ["Lake Louise sunrise", "Banff Gondola ride", "Johnston Canyon hike", "Hot springs soak", "Bow Falls walk", "Cave and Basin NHS", "Vermilion Lakes sunset", "Moraine Lake visit", "Sunshine Meadows hike", "Wildlife safari"],
        "food": ["Grizzly House", "Park Distillery", "The Bison", "Juniper Bistro", "Eden"],
        "tips": ["Book Lake Louise parking early", "Bring layers - weather changes fast", "Wildlife is everywhere - keep distance"]
    },
    "Jasper, Alberta": {
        "emoji": "🦌",
        "activities": ["Maligne Lake cruise", "Columbia Icefield skywalk", "Athabasca Falls", "Pyramid Lake kayak", "Jasper SkyTram", "Miette Hot Springs", "Valley of Five Lakes", "Stargazing at Dark Sky Preserve", "Wildlife watching", "Sunwapta Falls"],
        "food": ["Evil Dave's Grill", "Downstream Restaurant", "Syrahs", "Fiddle River", "Olive Bistro"],
        "tips": ["Gas up before leaving town", "Dark Sky Preserve is magical", "Elk roam downtown - be careful"]
    },
    "Vancouver, BC": {
        "emoji": "🌊",
        "activities": ["Stanley Park seawall", "Granville Island market", "Capilano Suspension Bridge", "Gastown steam clock", "English Bay sunset", "Grouse Mountain", "Science World", "VanDusen Gardens", "Chinatown tour", "Seabus to North Van"],
        "food": ["Tacofino", "Salmon n' Bannock", "Miku", "Vij's", "The Acorn"],
        "tips": ["Bring an umbrella always", "Transit is excellent", "Book Capilano tickets online"]
    },
    "Victoria, BC": {
        "emoji": "🌸",
        "activities": ["Butchart Gardens", "Inner Harbour walk", "Royal BC Museum", "Fisherman's Wharf", "Craigdarroch Castle", "Beacon Hill Park", "Whale watching tour", "Afternoon tea at Empress", "Chinatown walk", "Oak Bay village"],
        "food": ["Red Fish Blue Fish", "10 Acres Bistro", "Jam Cafe", "Pagliacci's", "Il Terrazzo"],
        "tips": ["Ferry fills up - book ahead", "Rent bikes for the seawall", "Butchart is worth the drive"]
    },
    "Whistler, BC": {
        "emoji": "⛷️",
        "activities": ["Peak 2 Peak Gondola", "Village stroll", "Lost Lake trails", "Scandinave Spa", "Zipline adventure", "Mountain biking", "Brandywine Falls", "Bungee jumping", "Golf at Fairmont", "Train Wreck hike"],
        "food": ["Peaked Pies", "Splitz Grill", "Araxi", "Red Door Bistro", "Rimrock Cafe"],
        "tips": ["Sea to Sky Highway is stunning", "Book spa in advance", "Village is walkable"]
    },
    "Toronto, Ontario": {
        "emoji": "🏙️",
        "activities": ["CN Tower EdgeWalk", "Kensington Market", "Distillery District", "ROM museum", "Toronto Islands", "St. Lawrence Market", "Graffiti Alley", "Hockey Hall of Fame", "High Park", "AGO art gallery"],
        "food": ["Canoe", "Pai Northern Thai", "Alo Restaurant", "Richmond Station", "Byblos"],
        "tips": ["Get a Presto card", "Islands are car-free paradise", "Weekends at markets are busy"]
    },
    "Niagara Falls, Ontario": {
        "emoji": "💧",
        "activities": ["Journey Behind the Falls", "Hornblower cruise", "Niagara-on-the-Lake", "Whirlpool Aero Car", "Clifton Hill games", "Wine tour", "Butterfly Conservatory", "Skylon Tower", "White Water Walk", "Floral Clock"],
        "food": ["Weinkeller", "Treadwell", "AG Inspired Cuisine", "Tide & Vine", "Benchmark"],
        "tips": ["Canadian side has best views", "Wine country is 20min away", "Falls are lit at night"]
    },
    "Montreal, Quebec": {
        "emoji": "🥐",
        "activities": ["Old Montreal walk", "Mount Royal hike", "Notre-Dame Basilica", "Jean-Talon Market", "Mile End murals", "Plateau stroll", "La Ronde", "Biodome visit", "Underground City", "Lachine Canal bike"],
        "food": ["Schwartz's Deli", "Joe Beef", "Olive et Gourmando", "L'Express", "Toqué!"],
        "tips": ["Everyone speaks French first", "Metro is fast and clean", "Bagel debate is real"]
    },
    "Quebec City, Quebec": {
        "emoji": "🏰",
        "activities": ["Château Frontenac", "Old Quebec walls walk", "Montmorency Falls", "Petit Champlain shops", "Plains of Abraham", "Île d'Orléans drive", "Toboggan run", "Ferry to Lévis", "Citadelle tour", "Quartier Petit Champlain"],
        "food": ["Aux Anciens Canadiens", "Chez Muffy", "Le Clocher Penché", "Café Paillard", "Légende"],
        "tips": ["Most European city in NA", "Winter is magical here", "Wear good walking shoes"]
    },
    "Halifax, Nova Scotia": {
        "emoji": "⚓",
        "activities": ["Peggy's Cove", "Halifax Citadel", "Waterfront boardwalk", "Maritime Museum", "Public Gardens", "Alexander Keith's tour", "Fisherman's Cove", "Point Pleasant Park", "Art Gallery of NS", "Dartmouth ferry"],
        "food": ["The Bicycle Thief", "Five Fishermen", "Stubborn Goat", "The Press Gang", "Edna"],
        "tips": ["Donairs are Halifax invention", "Peggy's Cove waves are dangerous", "East Coast time is 1hr ahead"]
    },
    "Calgary, Alberta": {
        "emoji": "🤠",
        "activities": ["Calgary Tower", "Stephen Avenue walk", "Heritage Park", "Calgary Zoo", "Prince's Island Park", "Studio Bell music centre", "Inglewood shops", "Peace Bridge", "TELUS Spark", "Fish Creek Park"],
        "food": ["Charcut Roast House", "River Cafe", "Model Milk", "OEB Breakfast Co", "Ten Foot Henry"],
        "tips": ["Chinooks change weather fast", "Gateway to Rockies", "Stampede is in July"]
    },
    "Ottawa, Ontario": {
        "emoji": "🍁",
        "activities": ["Parliament Hill tour", "Rideau Canal walk", "ByWard Market", "National Gallery", "Canadian War Museum", "Gatineau Park hike", "Changing of the Guard", "Museum of History", "Tulip Festival", "Sparks Street"],
        "food": ["Beckta", "Play Food & Wine", "Whalesbone", "Supply and Demand", "Riviera"],
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
    """Save email to Google Sheets"""
    webhook_url = "https://script.google.com/macros/s/AKfycbwcnveURZeNXhzwADjjMl7uAJ7WXccSBdh3CkOTPOBxS4Pp7z2RyY_OmIAeBxV_WfUb6w/exec"
    try:
        requests.post(webhook_url, json={"email": email, "source": source})
    except:
        pass


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


# ============ CUSTOM CSS ============
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

* { font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif; }

.stApp, [data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #0f0f23 0%, #1a1a3e 50%, #0f0f23 100%);
}

[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

h1, h2, h3 { color: white !important; }
p { color: rgba(255,255,255,0.8) !important; }

.stTextInput > div > div > input {
    background: rgba(255,255,255,0.1) !important;
    border: 2px solid rgba(255,255,255,0.2) !important;
    border-radius: 12px !important;
    color: white !important;
}

.stButton > button {
    background: linear-gradient(135deg, #ff6b6b, #ff8e8e) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    width: 100% !important;
}

.stSelectbox > div > div {
    background: rgba(255,255,255,0.1) !important;
    border: 2px solid rgba(255,255,255,0.2) !important;
    border-radius: 12px !important;
}

.stSelectbox label, .stSlider label, .stRadio label { color: white !important; }

.stRadio > div {
    background: rgba(255,255,255,0.05);
    padding: 12px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


# ============ HERO SECTION ============
st.markdown("""
<div style="text-align: center; padding-top: 20px;">
    <div style="display: inline-block; background: linear-gradient(135deg, rgba(255,107,107,0.25), rgba(78,205,196,0.25)); border: 1px solid rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 50px; color: #fff; font-size: 14px; font-weight: 600; margin-bottom: 20px;">
        🍁 #1 Facebook-First Trip Planner for Canadians
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style="font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #fff 0%, #c7d2fe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; line-height: 1.2; margin-bottom: 15px;">
    Plan Your Perfect Canadian Adventure
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<p style="font-size: 1.1rem; color: rgba(255,255,255,0.7) !important; text-align: center; margin-bottom: 25px; line-height: 1.5;">
    Create stunning, shareable trip itineraries in seconds.<br>Designed for Facebook Pages, Reels & Carousel posts.
</p>
""", unsafe_allow_html=True)

# Social proof
st.markdown("""
<div style="display: flex; align-items: center; justify-content: center; gap: 12px; margin: 20px 0; flex-wrap: wrap;">
    <div style="display: flex;">
        <div style="width: 40px; height: 40px; border-radius: 50%; border: 2px solid #1a1a3e; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; color: white; background: linear-gradient(135deg, #ff6b6b, #ff8e8e);">AB</div>
        <div style="width: 40px; height: 40px; border-radius: 50%; border: 2px solid #1a1a3e; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; color: white; background: linear-gradient(135deg, #4ecdc4, #6ee7de); margin-left: -8px;">BC</div>
        <div style="width: 40px; height: 40px; border-radius: 50%; border: 2px solid #1a1a3e; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; color: white; background: linear-gradient(135deg, #c77dff, #d9a8ff); margin-left: -8px;">ON</div>
        <div style="width: 40px; height: 40px; border-radius: 50%; border: 2px solid #1a1a3e; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; color: white; background: linear-gradient(135deg, #ffbe76, #ffd9a8); margin-left: -8px;">QC</div>
    </div>
    <div style="color: rgba(255,255,255,0.8); font-size: 14px;"><span style="color: #4ecdc4; font-weight: 700;">2,400+</span> trips planned</div>
</div>
""", unsafe_allow_html=True)

# Preview card
st.markdown("""
<div style="background: linear-gradient(145deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05)); border: 1px solid rgba(255,255,255,0.15); border-radius: 20px; padding: 25px; margin: 20px 0;">
    <div style="display: flex; gap: 6px; margin-bottom: 15px; padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); align-items: center;">
        <div style="width: 10px; height: 10px; border-radius: 50%; background: #ff6b6b;"></div>
        <div style="width: 10px; height: 10px; border-radius: 50%; background: #ffbe76;"></div>
        <div style="width: 10px; height: 10px; border-radius: 50%; background: #4ecdc4;"></div>
        <span style="color: white; font-weight: 600; font-size: 14px; margin-left: 10px;">Sample Itinerary</span>
    </div>
    <div style="font-size: 1.4rem; font-weight: 700; color: white; margin-bottom: 12px;">🏔️ Banff Adventure</div>
    <div>
        <span style="display: inline-block; background: rgba(78,205,196,0.2); color: #4ecdc4; padding: 5px 12px; border-radius: 15px; font-size: 12px; margin-right: 6px;">3 Days</span>
        <span style="display: inline-block; background: rgba(78,205,196,0.2); color: #4ecdc4; padding: 5px 12px; border-radius: 15px; font-size: 12px; margin-right: 6px;">Couple</span>
        <span style="display: inline-block; background: rgba(78,205,196,0.2); color: #4ecdc4; padding: 5px 12px; border-radius: 15px; font-size: 12px;">Nature</span>
    </div>
    <div style="margin-top: 15px; color: rgba(255,255,255,0.7); font-size: 14px; line-height: 1.8;">
        ✓ Lake Louise sunrise<br>
        ✓ Banff Gondola ride<br>
        ✓ Hot springs evening<br>
        <span style="color: #4ecdc4;">+ 6 more activities...</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ============ HOW IT WORKS ============
st.markdown('<h2 style="font-size: 1.6rem; font-weight: 700; color: white; text-align: center; margin: 40px 0 10px;">How It Works</h2>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 1rem; color: rgba(255,255,255,0.6) !important; text-align: center; margin-bottom: 25px;">Three simple steps to your dream Canadian trip</p>', unsafe_allow_html=True)

# Step 1
st.markdown("""
<div style="background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03)); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 25px 20px; text-align: center; margin-bottom: 15px;">
    <div style="width: 50px; height: 50px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800; color: white; margin-bottom: 15px; background: linear-gradient(135deg, #ff6b6b, #ff8e8e);">1</div>
    <div style="font-size: 1.1rem; font-weight: 700; color: white; margin-bottom: 8px;">Pick Your Destination</div>
    <div style="color: rgba(255,255,255,0.6); font-size: 14px;">Choose from 12 stunning Canadian destinations.</div>
</div>
""", unsafe_allow_html=True)

# Step 2
st.markdown("""
<div style="background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03)); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 25px 20px; text-align: center; margin-bottom: 15px;">
    <div style="width: 50px; height: 50px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800; color: #0f0f23; margin-bottom: 15px; background: linear-gradient(135deg, #4ecdc4, #6ee7de);">2</div>
    <div style="font-size: 1.1rem; font-weight: 700; color: white; margin-bottom: 8px;">Customize Your Trip</div>
    <div style="color: rgba(255,255,255,0.6); font-size: 14px;">Set your travel days and style.</div>
</div>
""", unsafe_allow_html=True)

# Step 3
st.markdown("""
<div style="background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03)); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 25px 20px; text-align: center; margin-bottom: 15px;">
    <div style="width: 50px; height: 50px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800; color: white; margin-bottom: 15px; background: linear-gradient(135deg, #c77dff, #d9a8ff);">3</div>
    <div style="font-size: 1.1rem; font-weight: 700; color: white; margin-bottom: 8px;">Share on Facebook</div>
    <div style="color: rgba(255,255,255,0.6); font-size: 14px;">Screenshot and share your itinerary!</div>
</div>
""", unsafe_allow_html=True)


# ============ WHY FACEBOOK-FIRST ============
st.markdown("""
<div style="background: linear-gradient(145deg, rgba(78,205,196,0.1), rgba(199,125,255,0.1)); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 25px; margin: 30px 0;">
    <div style="font-size: 1.3rem; font-weight: 700; color: white; margin-bottom: 20px;">📱 Why Facebook-First?</div>
    <div style="margin-bottom: 15px;">
        <span style="font-size: 22px;">📐</span>
        <span style="color: white; font-weight: 600; margin-left: 10px;">Perfect Dimensions</span>
        <div style="color: rgba(255,255,255,0.6); font-size: 13px; margin-left: 35px;">Sized for FB posts, Stories & Reels</div>
    </div>
    <div style="margin-bottom: 15px;">
        <span style="font-size: 22px;">🎨</span>
        <span style="color: white; font-weight: 600; margin-left: 10px;">Eye-Catching Design</span>
        <div style="color: rgba(255,255,255,0.6); font-size: 13px; margin-left: 35px;">Bold colours that pop in feeds</div>
    </div>
    <div style="margin-bottom: 15px;">
        <span style="font-size: 22px;">📸</span>
        <span style="color: white; font-weight: 600; margin-left: 10px;">Screenshot Ready</span>
        <div style="color: rgba(255,255,255,0.6); font-size: 13px; margin-left: 35px;">Just screenshot and post</div>
    </div>
    <div>
        <span style="font-size: 22px;">🔗</span>
        <span style="color: white; font-weight: 600; margin-left: 10px;">Page Tab Ready</span>
        <div style="color: rgba(255,255,255,0.6); font-size: 13px; margin-left: 35px;">Embed in your Facebook Page</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ============ PLANNER SECTION ============
st.markdown('<h2 style="font-size: 1.6rem; font-weight: 700; color: white; text-align: center; margin: 40px 0 10px;">🗺️ Plan Your Trip</h2>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 1rem; color: rgba(255,255,255,0.6) !important; text-align: center; margin-bottom: 25px;">Create your personalized Canadian adventure</p>', unsafe_allow_html=True)

if not st.session_state.unlocked:
    # Email capture box
    st.markdown("""
    <div style="background: linear-gradient(145deg, rgba(255,107,107,0.15), rgba(199,125,255,0.15)); border: 2px solid rgba(255,107,107,0.3); border-radius: 16px; padding: 30px 20px; text-align: center; margin: 20px 0;">
        <div style="font-size: 1.3rem; font-weight: 700; color: white; margin-bottom: 8px;">🔓 Unlock the Free Trip Planner</div>
        <div style="color: rgba(255,255,255,0.7); font-size: 14px;">Enter your email for instant access + exclusive travel tips</div>
    </div>
    """, unsafe_allow_html=True)
    
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
    st.markdown("""
    <div style="background: linear-gradient(145deg, rgba(30,30,60,0.95), rgba(20,20,40,0.98)); border: 2px dashed rgba(255,255,255,0.2); border-radius: 16px; padding: 50px 20px; text-align: center; margin: 20px 0;">
        <div style="font-size: 50px; margin-bottom: 15px;">🔒</div>
        <div style="color: white; font-size: 1.2rem; font-weight: 600; margin-bottom: 8px;">Trip Planner Locked</div>
        <div style="color: rgba(255,255,255,0.6); font-size: 14px;">Enter your email above to unlock</div>
    </div>
    """, unsafe_allow_html=True)

else:
    # Unlocked planner
    if st.session_state.email_submitted:
        st.success("✅ Welcome! Your planner is unlocked. Start planning below!")
        st.session_state.email_submitted = False
    
    destination = st.selectbox("🎯 Choose Destination", options=list(DESTINATIONS.keys()), index=0)
    days = st.slider("📅 Number of Days", 1, 10, 3)
    traveler_type = st.radio("👥 Traveler Type", options=["Solo", "Couple", "Family", "Group"], horizontal=True)
    
    if st.button("✨ Generate My Itinerary"):
        st.session_state.show_itinerary = True
    
    if st.session_state.show_itinerary:
        itinerary = generate_itinerary(destination, days, traveler_type)
        dest_emoji = DESTINATIONS[destination]["emoji"]
        
        # Itinerary header
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(255,107,107,0.2), rgba(78,205,196,0.2)); border-radius: 16px; padding: 25px 20px; text-align: center; margin-bottom: 20px;">
            <div style="font-size: 1.8rem; font-weight: 800; color: white; margin-bottom: 10px;">{dest_emoji} {destination}</div>
            <div style="color: rgba(255,255,255,0.7); font-size: 14px;">📅 {days} Days • 👥 {traveler_type} • 🍁 EasyTrip.ca</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Day cards
        for day_data in itinerary:
            activities_html = ""
            for activity in day_data['activities']:
                if activity['type'] == 'food':
                    activities_html += f"""
                    <div style="display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <span style="background: rgba(255,190,118,0.2); color: #ffbe76; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; min-width: 65px; text-align: center;">{activity['time']}</span>
                        <span style="color: rgba(255,255,255,0.9); font-size: 14px;">🍽️ {activity['activity']}</span>
                    </div>
                    """
                else:
                    activities_html += f"""
                    <div style="display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <span style="background: rgba(255,107,107,0.2); color: #ff8e8e; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; min-width: 65px; text-align: center;">{activity['time']}</span>
                        <span style="color: rgba(255,255,255,0.9); font-size: 14px;">✨ {activity['activity']}</span>
                    </div>
                    """
            
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05)); border: 1px solid rgba(255,255,255,0.12); border-radius: 16px; padding: 20px; margin-bottom: 15px;">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 15px; padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <div style="background: linear-gradient(135deg, #4ecdc4, #6ee7de); color: #0f0f23; width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 18px;">{day_data['day']}</div>
                    <div style="color: white; font-size: 1.1rem; font-weight: 600;">Day {day_data['day']} Adventure</div>
                </div>
                {activities_html}
                <div style="background: rgba(199,125,255,0.15); border-left: 3px solid #c77dff; padding: 12px; border-radius: 0 10px 10px 0; margin-top: 12px;">
                    <div style="color: rgba(255,255,255,0.8); font-size: 13px; margin-bottom: 6px;">💡 <strong>Pro tip:</strong> {day_data['tip']}</div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 13px;">👤 <strong>{traveler_type} tip:</strong> {day_data['traveler_tip']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Share box
        st.markdown("""
        <div style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; text-align: center; margin: 20px 0;">
            <div style="color: rgba(255,255,255,0.8); font-size: 14px; margin-bottom: 8px;">📸 <strong>To screenshot:</strong></div>
            <div style="color: rgba(255,255,255,0.5); font-size: 13px;">Mac: Cmd+Shift+4 • Windows: Win+Shift+S • Phone: Power+Volume</div>
            <div style="color: rgba(255,255,255,0.8); font-size: 14px; margin-top: 12px;">Share to Facebook and tag @EasyTripCanada! 🍁</div>
        </div>
        """, unsafe_allow_html=True)


# ============ FOOTER ============
st.markdown("""
<div style="text-align: center; padding: 30px 0; margin-top: 40px; border-top: 1px solid rgba(255,255,255,0.1);">
    <div style="color: rgba(255,255,255,0.5); font-size: 14px;">EasyTrip.ca 🇨🇦✨ · Designed for Facebook Page Tabs, Reels & carousels.</div>
    <div style="color: rgba(255,255,255,0.4); font-size: 12px; margin-top: 8px;">Made with ❤️ for Canadian travellers</div>
</div>
""", unsafe_allow_html=True)
