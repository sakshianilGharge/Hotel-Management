import streamlit as st
import sqlite3
import hashlib
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).with_name("hotel.db")

st.set_page_config(page_title="Grand Vista Hotel", page_icon="🏨", layout="wide", initial_sidebar_state="expanded")

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db():
    with get_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user', created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            guest_name TEXT NOT NULL, email TEXT NOT NULL, room_type TEXT NOT NULL,
            check_in TEXT NOT NULL, check_out TEXT NOT NULL, guests INTEGER NOT NULL,
            total REAL NOT NULL, status TEXT NOT NULL DEFAULT 'Confirmed',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")
        admin = conn.execute("SELECT id FROM users WHERE email=?", ("admin@grandvista.com",)).fetchone()
        if not admin:
            conn.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)",
                         ("Hotel Administrator", "admin@grandvista.com", hash_password("Admin@123"), "admin"))
        conn.commit()

init_db()

ROOMS = [
    {"name":"Deluxe Room", "price":3500, "capacity":2, "desc":"Elegant comfort, king-size bed, city view and complimentary breakfast.", "img":"https://images.unsplash.com/photo-1611892440504-42a792e24d32?auto=format&fit=crop&w=1200&q=85", "icon":"🛏️"},
    {"name":"Premium Suite", "price":6500, "capacity":3, "desc":"A spacious suite with a lounge area, premium amenities and a beautiful view.", "img":"https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=1200&q=85", "icon":"✨"},
    {"name":"Family Room", "price":5200, "capacity":4, "desc":"Extra space for families, twin sleeping areas and a relaxing sitting corner.", "img":"https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=1200&q=85", "icon":"👨‍👩‍👧‍👦"},
    {"name":"Executive Room", "price":4800, "capacity":2, "desc":"A quiet work-friendly room with a desk, fast Wi-Fi and refined interiors.", "img":"https://images.unsplash.com/photo-1595576508898-0ad5c879a061?auto=format&fit=crop&w=1200&q=85", "icon":"💼"}
]

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
:root { --navy:#102a43; --gold:#c79a45; }
.stApp { background:#f7f8fa; color:#182b3a; font-family:'DM Sans',sans-serif; }
h1,h2,h3 { font-family:'Playfair Display',serif !important; color:#102a43; }
.block-container { padding-top:1.6rem; max-width:1250px; }
.hero { background:linear-gradient(90deg,rgba(8,28,44,.86),rgba(8,28,44,.25)),url('https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=2000&q=90'); background-size:cover; background-position:center; padding:76px 48px; border-radius:22px; color:white; margin-bottom:28px; min-height:330px; display:flex; flex-direction:column; justify-content:center; }
.hero h1 { color:white !important; font-size:clamp(2.3rem,5vw,4.2rem) !important; margin:0; }
.hero p { color:#f1f5f9; font-size:1.12rem; max-width:620px; }
.eyebrow { text-transform:uppercase; letter-spacing:3px; color:#e5bf73; font-weight:700; font-size:.8rem; }
.stat { background:white; border:1px solid #e6eaf0; border-radius:16px; padding:20px; box-shadow:0 6px 24px rgba(16,42,67,.05); }
.stat small { color:#6b7c8f; text-transform:uppercase; letter-spacing:1px; font-size:.75rem; }
.stat h2 { margin:.2rem 0 0; font-family:'DM Sans',sans-serif !important; font-size:1.8rem; }
.room-card { background:white; border-radius:16px; padding:14px; border:1px solid #e6eaf0; height:100%; box-shadow:0 8px 24px rgba(16,42,67,.06); }
.room-card img { width:100%; height:190px; object-fit:cover; border-radius:11px; }
.price { font-size:1.35rem; font-weight:700; color:#a47725; }
.tag { display:inline-block; background:#f8f0df; color:#805b19; padding:5px 10px; border-radius:99px; font-size:.78rem; font-weight:600; }
section[data-testid="stSidebar"] { background:#102a43; }
section[data-testid="stSidebar"] * { color:white !important; }
.stButton>button { border-radius:10px; font-weight:600; min-height:2.6rem; }
div[data-testid="stForm"] { background:white; padding:20px; border-radius:15px; border:1px solid #e6eaf0; }
.footer { color:#6b7c8f; text-align:center; padding:25px 0 10px; border-top:1px solid #e4e8ee; margin-top:35px; }
</style>""", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None

def money(value):
    return f"₹{value:,.0f}"

def fetch_bookings(user_id=None):
    with get_db() as conn:
        if user_id is None:
            return conn.execute("SELECT * FROM bookings ORDER BY created_at DESC").fetchall()
        return conn.execute("SELECT * FROM bookings WHERE user_id=? ORDER BY created_at DESC", (user_id,)).fetchall()

def show_header():
    st.markdown('<div class="eyebrow">A stay worth remembering</div>', unsafe_allow_html=True)
    st.title("Grand Vista Hotel")
    st.caption("Thoughtful hospitality · Elegant rooms · Memorable experiences")

def home_page():
    st.markdown("""<div class="hero">
      <div class="eyebrow">Welcome to Grand Vista</div>
      <h1>Your comfort.<br>Our commitment.</h1>
      <p>Discover beautifully designed rooms, warm hospitality and thoughtful little details that make every stay special.</p>
    </div>""", unsafe_allow_html=True)
    a,b,c = st.columns(3)
    for col, num, label in [(a,"24/7","Guest support"),(b,"4.8/5","Guest experience"),(c,"100%","Comfort focused")]:
        with col: st.markdown(f'<div class="stat"><small>{label}</small><h2>{num}</h2></div>', unsafe_allow_html=True)
    st.write("")
    st.subheader("Find your perfect stay")
    cols = st.columns(2)
    for i, room in enumerate(ROOMS[:2]):
        with cols[i]:
            st.markdown(f"""<div class="room-card"><img src="{room['img']}"><h3>{room['name']}</h3><p>{room['desc']}</p><div class="price">{money(room['price'])} <span style="font-size:.85rem;color:#6b7c8f;font-weight:400">/ night</span></div></div>""", unsafe_allow_html=True)
    st.write("")
    st.subheader("The Grand Vista experience")
    x,y,z = st.columns(3)
    with x: st.markdown("### 🍽️ Dining\nSeasonal flavours, fresh ingredients and in-room dining.")
    with y: st.markdown("### 🧘 Wellness\nRelax, recharge and enjoy a calm atmosphere.")
    with z: st.markdown("### 🚗 Convenience\nHelpful concierge, Wi-Fi and travel assistance.")
    st.markdown('<div class="footer">Grand Vista Hotel · Hospitality with heart · Demo project</div>', unsafe_allow_html=True)

def rooms_page():
    show_header()
    st.subheader("Rooms & Suites")
    st.write("Choose a room that fits your trip. Rates shown are per night and are sample project prices.")
    cols = st.columns(2)
    for i, room in enumerate(ROOMS):
        with cols[i % 2]:
            st.markdown(f"""<div class="room-card"><img src="{room['img']}"><br><br><span class="tag">Up to {room['capacity']} guests</span><h3>{room['name']}</h3><p>{room['desc']}</p><div class="price">{money(room['price'])} <span style="font-size:.85rem;color:#6b7c8f;font-weight:400">/ night</span></div></div>""", unsafe_allow_html=True)
            if st.button(f"Book {room['name']}", key=f"book_{i}", use_container_width=True):
                st.session_state.page = "Book a Room"
                st.session_state.selected_room = room["name"]
                st.rerun()

def about_page():
    show_header()
    st.image("https://images.unsplash.com/photo-1571896349842-33c89424de2d?auto=format&fit=crop&w=1600&q=85", use_container_width=True)
    st.subheader("A welcoming place to pause")
    st.write("Grand Vista Hotel is a sample hotel brand created for this Hotel Management System project. Our concept combines elegant spaces, attentive service and practical amenities for leisure and business travellers.")
    st.subheader("Hotel information")
    left,right = st.columns(2)
    with left:
        st.markdown("**Amenities**")
        st.markdown("- Complimentary Wi-Fi\n- Restaurant and room service\n- 24-hour front desk\n- Daily housekeeping\n- Airport / local travel assistance\n- Family-friendly room options")
    with right:
        st.markdown("**Contact & location**")
        st.markdown("**Address:** 21 Lakeview Road, Pune, Maharashtra (demo address)\n\n**Phone:** +91 98765 43210 (demo)\n\n**Email:** hello@grandvistademo.com\n\n**Check-in:** 2:00 PM · **Check-out:** 11:00 AM")
    st.info("This is a college/demo application. Replace the sample hotel details and contact information with real details before publishing.")

def signup_page():
    show_header()
    st.subheader("Create your guest account")
    with st.form("signup_form"):
        name = st.text_input("Full name")
        email = st.text_input("Email address").strip().lower()
        password = st.text_input("Password (minimum 6 characters)", type="password")
        confirm = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Create account", use_container_width=True)
    if submitted:
        if not name.strip() or not email or "@" not in email:
            st.error("Please enter your name and a valid email address.")
        elif len(password) < 6:
            st.error("Password must contain at least 6 characters.")
        elif password != confirm:
            st.error("Passwords do not match.")
        else:
            try:
                with get_db() as conn:
                    conn.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)",
                                 (name.strip(), email, hash_password(password), "user"))
                    conn.commit()
                st.success("Account created! Please open Login to sign in.")
            except sqlite3.IntegrityError:
                st.error("This email is already registered. Please log in.")

def login_page():
    show_header()
    st.subheader("Welcome back")
    with st.form("login_form"):
        email = st.text_input("Email address").strip().lower()
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)
    if submitted:
        with get_db() as conn:
            user = conn.execute("SELECT * FROM users WHERE email=? AND password_hash=?",
                                (email, hash_password(password))).fetchone()
        if user:
            st.session_state.user = dict(user)
            st.session_state.page = "Admin Dashboard" if user["role"] == "admin" else "My Bookings"
            st.success(f"Welcome, {user['name']}!")
            st.rerun()
        else:
            st.error("Incorrect email or password.")
    with st.expander("Demo administrator login"):
        st.write("Email: `admin@grandvista.com`")
        st.write("Password: `Admin@123`")

def booking_page():
    show_header()
    user = st.session_state.user
    if not user:
        st.warning("Please log in before booking a room.")
        return
    st.subheader("Book a Room")
    default_room = st.session_state.get("selected_room", ROOMS[0]["name"])
    room_names = [r["name"] for r in ROOMS]
    idx = room_names.index(default_room) if default_room in room_names else 0
    with st.form("booking_form"):
        room_name = st.selectbox("Room type", room_names, index=idx)
        c1,c2 = st.columns(2)
        with c1:
            check_in = st.date_input("Check-in", value=date.today() + timedelta(days=1), min_value=date.today())
        with c2:
            check_out = st.date_input("Check-out", value=date.today() + timedelta(days=2), min_value=date.today() + timedelta(days=1))
        guests = st.selectbox("Number of guests", [1,2,3,4], index=1)
        guest_name = st.text_input("Guest name", value=user["name"])
        email = st.text_input("Contact email", value=user["email"])
        submit = st.form_submit_button("Confirm booking", use_container_width=True)
    if submit:
        room = next(r for r in ROOMS if r["name"] == room_name)
        nights = (check_out - check_in).days
        if check_out <= check_in:
            st.error("Check-out must be after check-in.")
        elif guests > room["capacity"]:
            st.error(f"{room_name} supports up to {room['capacity']} guests.")
        elif not guest_name.strip() or "@" not in email:
            st.error("Enter a guest name and valid contact email.")
        else:
            total = nights * room["price"]
            with get_db() as conn:
                conn.execute("""INSERT INTO bookings(user_id,guest_name,email,room_type,check_in,check_out,guests,total,status)
                                VALUES(?,?,?,?,?,?,?,?,?)""",
                             (user["id"], guest_name.strip(), email.strip(), room_name, str(check_in), str(check_out), guests, total, "Confirmed"))
                conn.commit()
            st.success(f"Booking confirmed for {nights} night(s). Estimated total: {money(total)}")
            st.session_state.page = "My Bookings"
            st.rerun()

def my_bookings_page():
    user = st.session_state.user
    if not user:
        st.warning("Please log in to view bookings.")
        return
    show_header()
    st.subheader("My Bookings")
    bookings = fetch_bookings(user["id"])
    if not bookings:
        st.info("You don't have any bookings yet. Visit Rooms & Suites to book your stay.")
        return
    for b in bookings:
        with st.container(border=True):
            a,c,d = st.columns([2,2,1])
            with a:
                st.markdown(f"### {b['room_type']}")
                st.write(f"Booking #{b['id']} · {b['guests']} guest(s)")
            with c:
                st.write(f"**{b['check_in']} → {b['check_out']}**")
                st.write(f"Guest: {b['guest_name']}")
            with d:
                st.markdown(f"**{money(b['total'])}**")
                st.caption(b["status"])

def admin_page():
    user = st.session_state.user
    if not user or user["role"] != "admin":
        st.error("Admin access only. Please log in with the administrator account.")
        return
    show_header()
    st.subheader("Admin Dashboard")
    with get_db() as conn:
        users = conn.execute("SELECT id,name,email,role,created_at FROM users ORDER BY id DESC").fetchall()
        bookings = conn.execute("SELECT * FROM bookings ORDER BY created_at DESC").fetchall()
    revenue = sum(b["total"] for b in bookings if b["status"] != "Cancelled")
    a,b,c,d = st.columns(4)
    for col, label, val in [(a,"Registered users",len([u for u in users if u["role"]=="user"])),(b,"Total bookings",len(bookings)),(c,"Confirmed bookings",len([x for x in bookings if x["status"]=="Confirmed"])),(d,"Booking value",money(revenue))]:
        with col: st.markdown(f'<div class="stat"><small>{label}</small><h2>{val}</h2></div>', unsafe_allow_html=True)
    st.write("")
    st.subheader("All bookings")
    if bookings:
        for bkg in bookings:
            with st.container(border=True):
                x,y,z = st.columns([3,2,2])
                with x:
                    st.markdown(f"**#{bkg['id']} · {bkg['guest_name']}**")
                    st.caption(f"{bkg['email']} · {bkg['room_type']}")
                with y:
                    st.write(f"{bkg['check_in']} → {bkg['check_out']}")
                    st.write(f"{bkg['guests']} guest(s) · {money(bkg['total'])}")
                with z:
                    st.write(f"Status: **{bkg['status']}**")
                    if bkg["status"] == "Confirmed" and st.button("Cancel booking", key=f"cancel_{bkg['id']}"):
                        with get_db() as conn:
                            conn.execute("UPDATE bookings SET status='Cancelled' WHERE id=?", (bkg["id"],))
                            conn.commit()
                        st.rerun()
    else:
        st.info("No bookings have been made yet.")
    st.write("")
    st.subheader("Registered accounts")
    if users:
        st.dataframe([dict(u) for u in users], use_container_width=True, hide_index=True)

if "page" not in st.session_state:
    st.session_state.page = "Home"

with st.sidebar:
    st.markdown("## 🏨 Grand Vista")
    st.caption("HOTEL MANAGEMENT")
    pages = ["Home", "Rooms & Suites", "About the Hotel", "Book a Room"]
    if st.session_state.user:
        pages += ["My Bookings"]
        if st.session_state.user["role"] == "admin":
            pages += ["Admin Dashboard"]
    else:
        pages += ["Login", "Sign Up"]
    current = st.session_state.page if st.session_state.page in pages else "Home"
    selected = st.radio("Navigation", pages, index=pages.index(current))
    st.session_state.page = selected
    st.divider()
    if st.session_state.user:
        st.markdown(f"**Signed in as**\n\n{st.session_state.user['name']}")
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = "Home"
            st.rerun()
    else:
        st.caption("Plan a stay. Make a memory.")

page = st.session_state.page
if page == "Home": home_page()
elif page == "Rooms & Suites": rooms_page()
elif page == "About the Hotel": about_page()
elif page == "Sign Up": signup_page()
elif page == "Login": login_page()
elif page == "Book a Room": booking_page()
elif page == "My Bookings": my_bookings_page()
elif page == "Admin Dashboard": admin_page()
