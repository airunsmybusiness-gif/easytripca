import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="EasyTrip Canada 🇨🇦", page_icon="🍁", layout="centered", initial_sidebar_state="collapsed")

if 'unlocked' not in st.session_state:
    st.session_state.unlocked = False
if 'email_submitted' not in st.session_state:
    st.session_state.email_submitted = False
if 'show_itinerary' not in st.session_state:
    st.session_state.show_itinerary = False

DESTINATIONS = {
    "Banff, Alberta": {"emoji": "🏔️", "activities": ["Lake Louise sunrise", "Banff Gondola ride", "Johnston Canyon hike", "Banff Upper Hot Springs", "Bow Falls walk", "Cave and Basin NHS", "Vermilion Lakes sunset", "Moraine Lake visit", "Sunshine Meadows hike", "Minnewanka Lake cruise"], "food": ["Grizzly House", "Park Distillery", "The Bison", "Juniper Bistro", "Sky Bistro"], "tips": ["Book Lake Louise parking 2 days ahead at reservation.pc.gc.ca", "Bring layers - mountain weather changes fast", "Wildlife on roads - drive slow at dawn/dusk"]},
    "Jasper, Alberta": {"emoji": "🦌", "activities": ["Maligne Lake cruise to Spirit Island", "Columbia Icefield Skywalk", "Athabasca Falls trail", "Pyramid Lake kayak rental", "Jasper SkyTram to Whistlers Summit", "Miette Hot Springs soak", "Valley of Five Lakes loop", "Dark Sky Preserve stargazing", "Maligne Canyon icewalk", "Sunwapta Falls viewpoint"], "food": ["Evil Dave's Grill", "Downstream Restaurant", "Syrahs", "Fiddle River", "Jasper Brewing Co"], "tips": ["Gas up in Jasper - no stations for 100km+ on Icefields Parkway", "Book Maligne Lake cruise in advance", "Watch for elk downtown - they roam freely"]},
    "Vancouver, BC": {"emoji": "🌊", "activities": ["Stanley Park Seawall bike ride", "Granville Island Public Market", "Capilano Suspension Bridge", "Gastown steam clock and shops", "English Bay sunset", "Grouse Mountain Skyride", "Science World dome", "Queen Elizabeth Park", "Chinatown and Dr. Sun Yat-Sen Garden", "SeaBus to North Vancouver"], "food": ["Miku Waterfront", "Vij's", "Tacofino", "The Acorn", "Salmon n' Bannock"], "tips": ["Bring an umbrella - rain is common", "Get a Compass Card for transit", "Book Capilano tickets online to skip lines"]},
    "Victoria, BC": {"emoji": "🌸", "activities": ["Butchart Gardens tour", "Inner Harbour walk", "Royal BC Museum", "Fisherman's Wharf floating homes", "Craigdarroch Castle tour", "Beacon Hill Park", "Whale watching tour", "Afternoon tea at Fairmont Empress", "Fan Tan Alley in Chinatown", "Oak Bay village stroll"], "food": ["Red Fish Blue Fish", "10 Acres Bistro", "Jam Cafe", "Il Terrazzo", "Pagliacci's"], "tips": ["Book BC Ferries in advance for your car", "Rent bikes to explore the waterfront", "Butchart is worth the 25-minute drive"]},
    "Whistler, BC": {"emoji": "⛷️", "activities": ["Peak 2 Peak Gondola between mountains", "Whistler Village stroll", "Lost Lake trails", "Scandinave Spa outdoor baths", "Zipline across Fitzsimmons Creek", "Mountain biking at Whistler Bike Park", "Brandywine Falls Provincial Park", "Train Wreck trail and graffiti bridge", "Alta Lake beach", "Audain Art Museum"], "food": ["Peaked Pies", "Splitz Grill", "Araxi Restaurant", "Red Door Bistro", "Rimrock Cafe"], "tips": ["Sea to Sky Highway is stunning - leave time for stops", "Book Scandinave Spa in advance", "Village is walkable - skip the car"]},
    "Toronto, Ontario": {"emoji": "🏙️", "activities": ["CN Tower EdgeWalk or glass floor", "Kensington Market vintage shops", "Distillery District cobblestones", "Royal Ontario Museum", "Toronto Islands ferry", "St. Lawrence Market Saturday market", "Graffiti Alley murals", "Hockey Hall of Fame", "High Park cherry blossoms", "Art Gallery of Ontario"], "food": ["Canoe", "Pai Northern Thai", "Richmond Station", "Byblos", "Alo Restaurant"], "tips": ["Get a Presto card for TTC transit", "Toronto Islands ferry fills up on weekends", "St. Lawrence Market best on Saturdays"]},
    "Niagara Falls, Ontario": {"emoji": "💧", "activities": ["Journey Behind the Falls tunnel", "Hornblower boat cruise", "Niagara-on-the-Lake wine tour", "Whirlpool Aero Car ride", "Clifton Hill attractions", "Niagara Parks Butterfly Conservatory", "Skylon Tower observation deck", "White Water Walk boardwalk", "Niagara Glen hiking trails", "Floral Clock"], "food": ["Weinkeller", "Treadwell Cuisine", "AG Inspired Cuisine", "Tide and Vine", "The Flour Mill"], "tips": ["Canadian side has the best views", "Wine country is a 20-min drive to Niagara-on-the-Lake", "Falls are illuminated nightly until midnight"]},
    "Montreal, Quebec": {"emoji": "🥐", "activities": ["Old Montreal cobblestone walk", "Mount Royal lookout hike", "Notre-Dame Basilica light show", "Jean-Talon Market food stalls", "Mile End bagel shops and murals", "Plateau-Mont-Royal neighbourhood", "La Ronde amusement park", "Biodome ecosystems", "Underground City shopping", "Lachine Canal bike path"], "food": ["Schwartz's Deli", "Joe Beef", "Olive et Gourmando", "L'Express", "Fairmount Bagel"], "tips": ["Learn basic French - locals appreciate it", "Metro is fast and connects everything", "Get both St-Viateur AND Fairmount bagels to compare"]},
    "Quebec City, Quebec": {"emoji": "🏰", "activities": ["Château Frontenac photo stop", "Old Quebec walls walk", "Montmorency Falls gondola", "Petit Champlain shops", "Plains of Abraham park", "Île d'Orléans farm drive", "Toboggan slide at Dufferin Terrace", "Lévis ferry for skyline views", "La Citadelle guided tour", "Quartier Petit Champlain cafes"], "food": ["Aux Anciens Canadiens", "Chez Muffy", "Le Clocher Penché", "Café Paillard", "Bistro L'Orygine"], "tips": ["Most European-feeling city in North America", "Winter Carnaval in February is magical", "Wear good walking shoes - lots of hills and stairs"]},
    "Halifax, Nova Scotia": {"emoji": "⚓", "activities": ["Peggy's Cove lighthouse", "Halifax Citadel NHS tour", "Waterfront boardwalk", "Maritime Museum of the Atlantic", "Public Gardens Victorian park", "Alexander Keith's Brewery tour", "Fisherman's Cove village", "Point Pleasant Park trails", "Art Gallery of Nova Scotia", "Halifax-Dartmouth ferry ride"], "food": ["The Bicycle Thief", "Five Fishermen", "Stubborn Goat", "The Press Gang", "Edna Restaurant"], "tips": ["Donairs are a Halifax invention - try one", "Peggy's Cove waves are dangerous - stay behind the rocks", "Halifax is 1 hour ahead of Toronto (Atlantic time)"]},
    "Calgary, Alberta": {"emoji": "🤠", "activities": ["Calgary Tower observation deck", "Stephen Avenue pedestrian mall", "Heritage Park Historical Village", "Calgary Zoo pandas", "Prince's Island Park downtown", "Studio Bell music centre", "Inglewood vintage shops", "Peace Bridge walk", "TELUS Spark science centre", "Fish Creek Provincial Park"], "food": ["Charcut Roast House", "River Cafe", "Model Milk", "OEB Breakfast Co", "Ten Foot Henry"], "tips": ["Chinook winds can change temperature 20°C in hours", "Gateway to the Rockies - Banff is 90 min away", "Calgary Stampede runs 10 days in July"]},
    "Ottawa, Ontario": {"emoji": "🍁", "activities": ["Parliament Hill free tour", "Rideau Canal walk or skate", "ByWard Market food and shops", "National Gallery of Canada", "Canadian War Museum", "Gatineau Park hiking", "Changing of the Guard ceremony", "Canadian Museum of History", "Tulip Festival in May", "Sparks Street pedestrian mall"], "food": ["Beckta", "Play Food & Wine", "Whalesbone", "Supply and Demand", "Riviera"], "tips": ["Rideau Canal becomes world's largest skating rink in winter", "Gatineau is in Quebec - bring your French", "Tulip Festival draws 500,000+ visitors in May"]}
}

TRAVELER_TIPS = {
    "Solo": ["Join free walking tours to meet people", "Hostels have great social vibes", "Solo dining at bars is totally normal here"],
    "Couple": ["Book sunset experiences", "Spa days are romantic here", "Ask about couples' packages"],
    "Family": ["Many attractions have family passes", "Pack snacks - kids get hungry", "Check for kid-free hours at pools"],
    "Group": ["Book group rates in advance", "Designate a meeting spot daily", "Split bills with apps like Splitwise"]
}

def save_email(email, source="landing_page"):
    webhook_url = "https://script.google.com/macros/s/AKfycbwcnveURZeNXhzwADjjMl7uAJ7WXccSBdh3CkOTPOBxS4Pp7z2RyY_OmIAeBxV_WfUb6w/exec"
    try:
        requests.post(webhook_url, json={"email": email, "source": source})
    except:
        pass

def generate_itinerary(destination, days, traveler_type):
    dest_data = DESTINATIONS.get(destination, list(DESTINATIONS.values())[0])
    itinerary = []
    activities = dest_data["activities"]
    foods = dest_data["food"]
    tips = dest_data["tips"]
    times = ["8:00 AM", "10:30 AM", "1:00 PM", "3:30 PM", "6:00 PM", "8:00 PM"]
    for day in range(1, days + 1):
        day_activities = []
        day_activities.append({"time": times[0], "activity": activities[(day - 1) % len(activities)], "type": "activity"})
        day_activities.append({"time": times[1], "activity": activities[(day + 1) % len(activities)], "type": "activity"})
        day_activities.append({"time": times[2], "activity": f"Lunch at {foods[(day - 1) % len(foods)]}", "type": "food"})
        day_activities.append({"time": times[3], "activity": activities[(day + 3) % len(activities)], "type": "activity"})
        day_activities.append({"time": times[4], "activity": activities[(day + 5) % len(activities)], "type": "activity"})
        day_activities.append({"time": times[5], "activity": f"Dinner at {foods[day % len(foods)]}", "type": "food"})
        itinerary.append({"day": day, "activities": day_activities, "tip": tips[(day - 1) % len(tips)], "traveler_tip": TRAVELER_TIPS[traveler_type][(day - 1) % len(TRAVELER_TIPS[traveler_type])]})
    return itinerary

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
* { font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif; }
.stApp, [data-testid="stAppViewContainer"] { background: linear-gradient(180deg, #0f0f23 0%, #1a1a3e 50%, #0f0f23 100%); }
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
h1, h2, h3 { color: white !important; }
p { color: rgba(255,255,255,0.8) !important; }
.stTextInput > div > div > input { background: rgba(30,30,60,0.9) !important; border: 2px solid rgba(255,255,255,0.4) !important; border-radius: 12px !important; color: #ffffff !important; font-weight: 500 !important; }
.stTextInput > div > div > input::placeholder { color: rgba(255,255,255,0.6) !important; }
.stButton > button { background: linear-gradient(135deg, #ff6b6b, #ff8e8e) !important; color: white !important; border: none !important; border-radius: 12px !important; font-weight: 700 !important; width: 100% !important; }
.stSelectbox > div > div { background: rgba(255,255,255,0.1) !important; border: 2px solid rgba(255,255,255,0.2) !important; border-radius: 12px !important; }
.stSelectbox label, .stSlider label, .stRadio label { color: white !important; }
.stRadio > div { background: rgba(255,255,255,0.05); padding: 12px; border-radius: 12px; }
</style>""", unsafe_allow_html=True)

st.markdown('<div style="text-align: center; padding-top: 20px;"><div style="display: inline-block; background: linear-gradient(135deg, rgba(255,107,107,0.25), rgba(78,205,196,0.25)); border: 1px solid rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 50px; color: #fff; font-size: 14px; font-weight: 600; margin-bottom: 20px;">🍁 #1 Facebook-First Trip Planner for Canadians</div></div>', unsafe_allow_html=True)

st.markdown('<h1 style="font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #fff 0%, #c7d2fe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; line-height: 1.2; margin-bottom: 15px;">Plan Your Perfect Canadian Adventure</h1>', unsafe_allow_html=True)

st.markdown('<p style="font-size: 1.1rem; color: rgba(255,255,255,0.7) !important; text-align: center; margin-bottom: 25px; line-height: 1.5;">Create stunning, shareable trip itineraries in seconds.<br>Designed for Facebook Pages, Reels & Carousel posts.</p>', unsafe_allow_html=True)

st.markdown('<div style="display: flex; align-items: center; justify-content: center; gap: 12px; margin: 20px 0; flex-wrap: wrap;"><div style="display: flex;"><div style="width: 40px; height: 40px; border-radius: 50%; border: 2px solid #1a1a3e; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; color: white; background: linear-gradient(135deg, #ff6b6b, #ff8e8e);">AB</div><div style="width: 40px; height: 40px; border-radius: 50%; border: 2px solid #1a1a3e; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; color: white; background: linear-gradient(135deg, #4ecdc4, #6ee7de); margin-left: -8px;">BC</div><div style="width: 40px; height: 40px; border-radius: 50%; border: 2px solid #1a1a3e; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; color: white; background: linear-gradient(135deg, #c77dff, #d9a8ff); margin-left: -8px;">ON</div><div style="width: 40px; height: 40px; border-radius: 50%; border: 2px solid #1a1a3e; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; color: white; background: linear-gradient(135deg, #ffbe76, #ffd9a8); margin-left: -8px;">QC</div></div><div style="color: rgba(255,255,255,0.8); font-size: 14px;"><span style="color: #4ecdc4; font-weight: 700;">2,400+</span> trips planned</div></div>', unsafe_allow_html=True)

st.markdown('<div style="background: linear-gradient(145deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05)); border: 1px solid rgba(255,255,255,0.15); border-radius: 20px; padding: 25px; margin: 20px 0;"><div style="display: flex; gap: 6px; margin-bottom: 15px; padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); align-items: center;"><div style="width: 10px; height: 10px; border-radius: 50%; background: #ff6b6b;"></div><div style="width: 10px; height: 10px; border-radius: 50%; background: #ffbe76;"></div><div style="width: 10px; height: 10px; border-radius: 50%; background: #4ecdc4;"></div><span style="color: white; font-weight: 600; font-size: 14px; margin-left: 10px;">Sample Itinerary</span></div><div style="font-size: 1.4rem; font-weight: 700; color: white; margin-bottom: 12px;">🏔️ Banff Adventure</div><div><span style="display: inline-block; background: rgba(78,205,196,0.2); color: #4ecdc4; padding: 5px 12px; border-radius: 15px; font-size: 12px; margin-right: 6px;">3 Days</span><span style="display: inline-block; background: rgba(78,205,196,0.2); color: #4ecdc4; padding: 5px 12px; border-radius: 15px; font-size: 12px; margin-right: 6px;">Couple</span><span style="display: inline-block; background: rgba(78,205,196,0.2); color: #4ecdc4; padding: 5px 12px; border-radius: 15px; font-size: 12px;">Nature</span></div><div style="margin-top: 15px; color: rgba(255,255,255,0.7); font-size: 14px; line-height: 1.8;">✓ Lake Louise sunrise<br>✓ Banff Gondola ride<br>✓ Hot springs evening<br><span style="color: #4ecdc4;">+ 6 more activities...</span></div></div>', unsafe_allow_html=True)

st.markdown('<h2 style="font-size: 1.6rem; font-weight: 700; color: white; text-align: center; margin: 40px 0 10px;">How It Works</h2>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 1rem; color: rgba(255,255,255,0.6) !important; text-align: center; margin-bottom: 25px;">Three simple steps to your dream Canadian trip</p>', unsafe_allow_html=True)

st.markdown('<div style="background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03)); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 25px 20px; text-align: center; margin-bottom: 15px;"><div style="width: 50px; height: 50px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800; color: white; margin-bottom: 15px; background: linear-gradient(135deg, #ff6b6b, #ff8e8e);">1</div><div style="font-size: 1.1rem; font-weight: 700; color: white; margin-bottom: 8px;">Pick Your Destination</div><div style="color: rgba(255,255,255,0.6); font-size: 14px;">Choose from 12 stunning Canadian destinations.</div></div>', unsafe_allow_html=True)

st.markdown('<div style="background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03)); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 25px 20px; text-align: center; margin-bottom: 15px;"><div style="width: 50px; height: 50px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800; color: #0f0f23; margin-bottom: 15px; background: linear-gradient(135deg, #4ecdc4, #6ee7de);">2</div><div style="font-size: 1.1rem; font-weight: 700; color: white; margin-bottom: 8px;">Customize Your Trip</div><div style="color: rgba(255,255,255,0.6); font-size: 14px;">Set your travel days and style.</div></div>', unsafe_allow_html=True)

st.markdown('<div style="background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03)); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 25px 20px; text-align: center; margin-bottom: 15px;"><div style="width: 50px; height: 50px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800; color: white; margin-bottom: 15px; background: linear-gradient(135deg, #c77dff, #d9a8ff);">3</div><div style="font-size: 1.1rem; font-weight: 700; color: white; margin-bottom: 8px;">Share on Facebook</div><div style="color: rgba(255,255,255,0.6); font-size: 14px;">Screenshot and share your itinerary!</div></div>', unsafe_allow_html=True)

st.markdown('<div style="background: linear-gradient(145deg, rgba(78,205,196,0.1), rgba(199,125,255,0.1)); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 25px; margin: 30px 0;"><div style="font-size: 1.3rem; font-weight: 700; color: white; margin-bottom: 20px;">📱 Why Facebook-First?</div><div style="margin-bottom: 15px;"><span style="font-size: 22px;">📐</span><span style="color: white; font-weight: 600; margin-left: 10px;">Perfect Dimensions</span><div style="color: rgba(255,255,255,0.6); font-size: 13px; margin-left: 35px;">Sized for FB posts, Stories & Reels</div></div><div style="margin-bottom: 15px;"><span style="font-size: 22px;">🎨</span><span style="color: white; font-weight: 600; margin-left: 10px;">Eye-Catching Design</span><div style="color: rgba(255,255,255,0.6); font-size: 13px; margin-left: 35px;">Bold colours that pop in feeds</div></div><div style="margin-bottom: 15px;"><span style="font-size: 22px;">📸</span><span style="color: white; font-weight: 600; margin-left: 10px;">Screenshot Ready</span><div style="color: rgba(255,255,255,0.6); font-size: 13px; margin-left: 35px;">Just screenshot and post</div></div><div><span style="font-size: 22px;">🔗</span><span style="color: white; font-weight: 600; margin-left: 10px;">Page Tab Ready</span><div style="color: rgba(255,255,255,0.6); font-size: 13px; margin-left: 35px;">Embed in your Facebook Page</div></div></div>', unsafe_allow_html=True)

st.markdown('<h2 style="font-size: 1.6rem; font-weight: 700; color: white; text-align: center; margin: 40px 0 10px;">🗺️ Plan Your Trip</h2>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 1rem; color: rgba(255,255,255,0.6) !important; text-align: center; margin-bottom: 25px;">Create your personalized Canadian adventure</p>', unsafe_allow_html=True)

if not st.session_state.unlocked:
    st.markdown('<div style="background: linear-gradient(145deg, rgba(255,107,107,0.15), rgba(199,125,255,0.15)); border: 2px solid rgba(255,107,107,0.3); border-radius: 16px; padding: 30px 20px; text-align: center; margin: 20px 0;"><div style="font-size: 1.3rem; font-weight: 700; color: white; margin-bottom: 8px;">🔓 Unlock the Free Trip Planner</div><div style="color: rgba(255,255,255,0.7); font-size: 14px;">Enter your email for instant access + exclusive travel tips</div></div>', unsafe_allow_html=True)
    email = st.text_input("Email", placeholder="your@email.com", label_visibility="collapsed")
    if st.button("🍁 Unlock Free Planner"):
        if email and "@" in email:
            save_email(email, "planner_unlock")
            st.session_state.unlocked = True
            st.session_state.email_submitted = True
            st.rerun()
        else:
            st.error("Please enter a valid email address")
    st.markdown('<div style="background: linear-gradient(145deg, rgba(30,30,60,0.95), rgba(20,20,40,0.98)); border: 2px dashed rgba(255,255,255,0.2); border-radius: 16px; padding: 50px 20px; text-align: center; margin: 20px 0;"><div style="font-size: 50px; margin-bottom: 15px;">🔒</div><div style="color: white; font-size: 1.2rem; font-weight: 600; margin-bottom: 8px;">Trip Planner Locked</div><div style="color: rgba(255,255,255,0.6); font-size: 14px;">Enter your email above to unlock</div></div>', unsafe_allow_html=True)
else:
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
        st.markdown(f'<div style="background: linear-gradient(135deg, rgba(255,107,107,0.2), rgba(78,205,196,0.2)); border-radius: 16px; padding: 25px 20px; text-align: center; margin-bottom: 20px;"><div style="font-size: 1.8rem; font-weight: 800; color: white; margin-bottom: 10px;">{dest_emoji} {destination}</div><div style="color: rgba(255,255,255,0.7); font-size: 14px;">📅 {days} Days • 👥 {traveler_type} • 🍁 EasyTrip.ca</div></div>', unsafe_allow_html=True)
        for day_data in itinerary:
            activities_html = ""
            for activity in day_data['activities']:
                if activity['type'] == 'food':
                    activities_html += f'<div style="display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05);"><span style="background: rgba(255,190,118,0.2); color: #ffbe76; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; min-width: 65px; text-align: center;">{activity["time"]}</span><span style="color: rgba(255,255,255,0.9); font-size: 14px;">🍽️ {activity["activity"]}</span></div>'
                else:
                    activities_html += f'<div style="display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05);"><span style="background: rgba(255,107,107,0.2); color: #ff8e8e; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; min-width: 65px; text-align: center;">{activity["time"]}</span><span style="color: rgba(255,255,255,0.9); font-size: 14px;">✨ {activity["activity"]}</span></div>'
            st.markdown(f'<div style="background: linear-gradient(145deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05)); border: 1px solid rgba(255,255,255,0.12); border-radius: 16px; padding: 20px; margin-bottom: 15px;"><div style="display: flex; align-items: center; gap: 12px; margin-bottom: 15px; padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1);"><div style="background: linear-gradient(135deg, #4ecdc4, #6ee7de); color: #0f0f23; width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 18px;">{day_data["day"]}</div><div style="color: white; font-size: 1.1rem; font-weight: 600;">Day {day_data["day"]} Adventure</div></div>{activities_html}<div style="background: rgba(199,125,255,0.15); border-left: 3px solid #c77dff; padding: 12px; border-radius: 0 10px 10px 0; margin-top: 12px;"><div style="color: rgba(255,255,255,0.8); font-size: 13px; margin-bottom: 6px;">💡 <strong>Pro tip:</strong> {day_data["tip"]}</div><div style="color: rgba(255,255,255,0.8); font-size: 13px;">👤 <strong>{traveler_type} tip:</strong> {day_data["traveler_tip"]}</div></div></div>', unsafe_allow_html=True)
        st.markdown('<div style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; text-align: center; margin: 20px 0;"><div style="color: rgba(255,255,255,0.8); font-size: 14px; margin-bottom: 8px;">📸 <strong>To screenshot:</strong></div><div style="color: rgba(255,255,255,0.5); font-size: 13px;">Mac: Cmd+Shift+4 • Windows: Win+Shift+S • Phone: Power+Volume</div><div style="color: rgba(255,255,255,0.8); font-size: 14px; margin-top: 12px;">Share to Facebook and tag @EasyTripCanada! 🍁</div></div>', unsafe_allow_html=True)

st.markdown('<div style="text-align: center; padding: 30px 0; margin-top: 40px; border-top: 1px solid rgba(255,255,255,0.1);"><div style="color: rgba(255,255,255,0.5); font-size: 14px;">EasyTrip.ca 🇨🇦✨ · Designed for Facebook Page Tabs, Reels & carousels.</div><div style="color: rgba(255,255,255,0.4); font-size: 12px; margin-top: 8px;">Made with ❤️ for Canadian travellers</div></div>', unsafe_allow_html=True)
