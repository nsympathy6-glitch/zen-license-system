import sys, os, hashlib, webbrowser
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QFrame, QScrollArea, QStackedWidget,
    QGridLayout, QFileDialog, QMessageBox, QSizePolicy, QSpacerItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
import httpx

SERVER = os.getenv("LICENSE_SERVER_URL", "http://localhost:8000")
DISCORD = "https://discord.gg/bR2khn3q5"
TIKTOK = "https://www.tiktok.com/@jxshyy2k"
SITE = "https://shoot3p.pages.dev"

VIDEOS = [
    r"C:\Users\josh\Desktop\discord bot\shoot3p-bot\assets\announce\video 7.mp4",
    r"C:\Users\josh\Desktop\discord bot\shoot3p-bot\assets\announce\video.mkv 3.mp4",
]

SCRIPTS = [
    {"id":"nba2k_3ps","name":"NBA 2K27 - 3PS Secret","game":"NBA 2K27",
     "desc":"The ultimate NBA 2K27 competitive advantage. Dominate park, rec, and pro-am with undetectable aim assistance, green releases, and auto-footer scripts.",
     "feat":["Auto Green Release","Smart Aimbot","Auto Dribble Combos","Speed Boost","Anti-Detection","Shot Timing Profiles","Park & Rec Ready","Pro-Am Tournament"],
     "price":49.99,"tier":"plus","color":"#FF6B35","icon":"\U0001f3c0"},
    {"id":"nba2k_2s","name":"NBA 2K27 - 2S Script","game":"NBA 2K27",
     "desc":"Specialized for 2v2 and small ball. Quick ISO moves, fast breaks, and clutch shooting for duos.",
     "feat":["ISO Move Presets","Quick Stop Green","Fast Break Auto","Alley-Oop Boost","Stamina Mgmt","2v2 Rotation"],
     "price":39.99,"tier":"standard","color":"#4ECDC4","icon":"\U0001f3c0"},
    {"id":"cod_shooty","name":"COD - Call of Shooty","game":"Call of Duty",
     "desc":"Precision aiming for Warzone and Multiplayer. Zero recoil, snap aim, and predictive tracking.",
     "feat":["Zero Recoil","Snap-to-Target","Predictive Tracking","Auto Dropshot","Slide Cancel","Multi-Weapon"],
     "price":44.99,"tier":"plus","color":"#E74C3C","icon":"\U0001f52b"},
    {"id":"bo2_script","name":"Black Ops 2 - BO2 Script","game":"COD: BO2",
     "desc":"Classic BO2 zombies and multiplayer enhancement. Max ammo, insta-kill combos, and lobby tools.",
     "feat":["Zombies Insta-Kill","Max Ammo Auto","Hip-Fire Boost","360 No-Scope","Headshot Multi","Lobby Tools"],
     "price":29.99,"tier":"standard","color":"#9B59B6","icon":"\U0001f480"},
    {"id":"apex_scripts","name":"Apex Legends Scripts","game":"Apex Legends",
     "desc":"Competitive Apex advantage. Tap-strafe macros, aim smoothing, and legend ability automation.",
     "feat":["Tap-Strafe Macro","Aim Smoothing","Shield Swap","Slide-Jump","Kraber Predictor","Arena Presets"],
     "price":44.99,"tier":"plus","color":"#E67E22","icon":"\U0001f3af"},
    {"id":"fortnite_boxed","name":"Fortnite - Boxed by 3P","game":"Fortnite",
     "desc":"Build-edit dominance. Triple edits, piece control macros, and aim assist tuning for controller.",
     "feat":["Triple Edit Macro","Piece Control Auto","Aim Assist Tuner","90s Builder","Zone War Sets","FNCS Settings"],
     "price":49.99,"tier":"plus","color":"#F1C40F","icon":"\U0001f3d7\ufe0f"},
    {"id":"rust_zen","name":"Rust - Rusty Zen","game":"Rust",
     "desc":"Survival dominance. Recoil patterns, spray control, and PVP automation for wipes and raids.",
     "feat":["AK-47 Recoil","Spray Control","Auto Heal","Door Camp Alert","Raid Timer","Night Vision"],
     "price":34.99,"tier":"standard","color":"#795548","icon":"\u26cf\ufe0f"},
]

BG="#0d0d1a"; CAR="#12122a"; BDR="#1e1e3a"; ACC="#6C63FF"; MUT="#555577"; SEC="#8888aa"


class API(QThread):
    done = pyqtSignal(dict)
    err = pyqtSignal(str)
    def __init__(self, m, u, d=None):
        super().__init__(); self.m,self.u,self.d=m,u,d
    def run(self):
        try:
            with httpx.Client(timeout=10) as c:
                r = c.get(self.u) if self.m=="GET" else c.post(self.u,json=self.d)
                (self.done if r.status_code==200 else self.err).emit(r.json() if r.status_code==200 else {"e":r.json().get("detail","Error")})
        except Exception as e: self.err.emit({"e":str(e)})


class Btn(QPushButton):
    def __init__(self, t, c=ACC, h=46, p=None):
        super().__init__(t,p); self.setFixedHeight(h); self.setCursor(Qt.PointingHandCursor)
        h2=c.lstrip('#'); r,g,b=int(h2[0:2],16),int(h2[2:4],16),int(h2[4:6],16)
        dk=f"rgb({int(r*.7)},{int(g*.7)},{int(b*.7)})"; lt=f"rgb({min(255,int(r*1.2))},{min(255,int(g*1.2))},{min(255,int(b*1.2))})"
        self.setStyleSheet(f"QPushButton{{background:{c};color:white;border:none;border-radius:8px;padding:0 24px;font-size:13px;font-weight:600;letter-spacing:1px;}}QPushButton:hover{{background:{lt}}}QPushButton:pressed{{background:{dk}}}QPushButton:disabled{{background:#222;color:#444}}")

class Card(QFrame):
    def __init__(self, bc=BDR, p=None):
        super().__init__(p); self.setStyleSheet(f"QFrame{{background:{CAR};border:1px solid {bc};border-radius:14px;}}")

def find_script(sid):
    return next((s for s in SCRIPTS if s['id']==sid), None)


# ══════════════════════════════════════════════════════════════
# LOGIN PAGE
# ══════════════════════════════════════════════════════════════
class LoginPage(QWidget):
    ok = pyqtSignal(str,str)
    def __init__(self, main=None):
        super().__init__(); self.main=main
        r = QHBoxLayout(self); r.setContentsMargins(0,0,0,0); r.setSpacing(0)

        # ── Left branding panel ──
        L = QFrame(); L.setMinimumWidth(360); L.setMaximumWidth(440)
        L.setStyleSheet("QFrame{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #6C63FF,stop:0.5 #4a42d4,stop:1 #2d2b80);}")
        ll = QVBoxLayout(L); ll.setContentsMargins(40,40,40,40); ll.setSpacing(10)
        lg = QLabel("SHOOT 3P"); lg.setFont(QFont("Segoe UI",32,QFont.Bold)); lg.setStyleSheet("color:white;letter-spacing:3px;"); ll.addWidget(lg)
        tl = QLabel("TOOLS"); tl.setFont(QFont("Segoe UI",18)); tl.setStyleSheet("color:rgba(255,255,255,0.6);letter-spacing:5px;"); ll.addWidget(tl)
        ll.addSpacing(16)
        tg = QLabel("Premium Cronus Zen Scripts\nfor Competitive Players"); tg.setFont(QFont("Segoe UI",11)); tg.setStyleSheet("color:rgba(255,255,255,0.5);"); tg.setWordWrap(True); ll.addWidget(tg)
        ll.addStretch()
        st = QHBoxLayout(); st.setSpacing(24)
        for n,l in [("1000+","Members"),("50+","Scripts"),("24/7","Support")]:
            cl=QVBoxLayout(); nl=QLabel(n); nl.setFont(QFont("Segoe UI",18,QFont.Bold)); nl.setStyleSheet("color:white;"); cl.addWidget(nl)
            ll2=QLabel(l); ll2.setFont(QFont("Segoe UI",9)); ll2.setStyleSheet("color:rgba(255,255,255,0.45);"); cl.addWidget(ll2); st.addLayout(cl)
        ll.addLayout(st); ll.addSpacing(16)
        lk = QHBoxLayout(); lk.setSpacing(14)
        for t,c,u in [("Discord","#5865F2",DISCORD),("TikTok","#ff0050",TIKTOK),("Website","#fff",SITE)]:
            b=QPushButton(t); b.setCursor(Qt.PointingHandCursor); b.setStyleSheet(f"QPushButton{{color:{c};background:transparent;border:none;font-size:12px;font-weight:600;}}QPushButton:hover{{color:white;}}")
            b.clicked.connect(lambda _,url=u:webbrowser.open(url)); lk.addWidget(b)
        ll.addLayout(lk)
        r.addWidget(L)

        # ── Right login panel ──
        R = QWidget(); R.setStyleSheet(f"background:{BG};")
        rl = QVBoxLayout(R); rl.setContentsMargins(56,40,56,40); rl.setSpacing(0)
        rl.addSpacerItem(QSpacerItem(0,10,QSizePolicy.Minimum,QSizePolicy.Expanding))
        w=QLabel("Welcome back"); w.setFont(QFont("Segoe UI",26,QFont.Bold)); w.setStyleSheet("color:white;"); rl.addWidget(w)
        rl.addSpacing(4)
        s=QLabel("Connect your Discord, then enter your Zen serial"); s.setFont(QFont("Segoe UI",12)); s.setStyleSheet(f"color:{SEC};"); rl.addWidget(s)
        rl.addSpacing(20)

        # Step indicator
        steps_row = QHBoxLayout(); steps_row.setSpacing(8)
        self.step1_dot = QLabel("1"); self.step1_dot.setFixedSize(22,22)
        self.step1_dot.setStyleSheet("background:#5865F2;border-radius:11px;color:white;font-size:10px;font-weight:bold;"); self.step1_dot.setAlignment(Qt.AlignCenter)
        steps_row.addWidget(self.step1_dot)
        self.step1_lbl = QLabel("Discord"); self.step1_lbl.setStyleSheet("color:#5865F2;font-size:11px;font-weight:600;"); steps_row.addWidget(self.step1_lbl)
        line1 = QLabel(); line1.setFixedSize(30,2); line1.setStyleSheet(f"background:{BDR};"); steps_row.addWidget(line1)
        self.step2_dot = QLabel("2"); self.step2_dot.setFixedSize(22,22)
        self.step2_dot.setStyleSheet(f"background:#333;border-radius:11px;color:#555;font-size:10px;font-weight:bold;"); self.step2_dot.setAlignment(Qt.AlignCenter)
        steps_row.addWidget(self.step2_dot)
        self.step2_lbl = QLabel("Zen Serial"); self.step2_lbl.setStyleSheet("color:#555;font-size:11px;font-weight:600;"); steps_row.addWidget(self.step2_lbl)
        steps_row.addStretch(); rl.addLayout(steps_row); rl.addSpacing(16)

        # Discord button
        self.discord_btn = QPushButton("  Login with Discord"); self.discord_btn.setFixedHeight(50); self.discord_btn.setCursor(Qt.PointingHandCursor)
        self.discord_btn.setStyleSheet("QPushButton{background:#5865F2;color:white;border:none;border-radius:10px;font-size:15px;font-weight:600;}QPushButton:hover{background:#4752c4;}QPushButton:pressed{background:#3c45a5;}")
        self.discord_btn.clicked.connect(self._discord_login); rl.addWidget(self.discord_btn)
        rl.addSpacing(4)
        self.discord_status = QLabel(""); self.discord_status.setFont(QFont("Segoe UI",10)); self.discord_status.setStyleSheet("color:#F39C12;"); self.discord_status.setAlignment(Qt.AlignCenter); rl.addWidget(self.discord_status)
        rl.addSpacing(16)

        # Divider
        div = QFrame(); div.setFixedHeight(1); div.setStyleSheet(f"background:{BDR};"); rl.addWidget(div)
        rl.addSpacing(16)

        # Zen serial
        l2=QLabel("ZEN SERIAL NUMBER"); l2.setStyleSheet(f"color:{SEC};font-size:11px;font-weight:600;letter-spacing:1px;"); rl.addWidget(l2); rl.addSpacing(6)
        self.si=QLineEdit(); self.si.setPlaceholderText("Connect Discord first"); self.si.setFixedHeight(46); self.si.setEnabled(False)
        self.si.setStyleSheet("QLineEdit{background:#0a0a18;color:white;border:1px solid #2a2a44;border-radius:8px;padding:0 14px;font-size:14px;}QLineEdit:focus{border:1px solid #6C63FF;}QLineEdit:disabled{color:#444;}")
        rl.addWidget(self.si); rl.addSpacing(20)

        self.btn=Btn("ENTER PORTAL"); self.btn.setFixedHeight(50); self.btn.clicked.connect(self._go); rl.addWidget(self.btn)
        rl.addSpacing(4)
        self.er=QLabel(""); self.er.setStyleSheet("color:#E74C3C;font-size:12px;"); self.er.setAlignment(Qt.AlignCenter); rl.addWidget(self.er)
        rl.addSpacerItem(QSpacerItem(0,12,QSizePolicy.Minimum,QSizePolicy.Expanding))

        # Website sync note
        note = Card("#5865F244"); nsl = QVBoxLayout(note); nsl.setContentsMargins(14,10,14,10); nsl.setSpacing(4)
        nst = QLabel("Just purchased a script?"); nst.setFont(QFont("Segoe UI",10,QFont.Bold)); nst.setStyleSheet("color:#5865F2;"); nsl.addWidget(nst)
        nsb = QLabel("Log in through our website first to sync your purchases. Your website account is linked through Discord, so your orders will appear here automatically.")
        nsb.setFont(QFont("Segoe UI",9)); nsb.setStyleSheet("color:#aaa;"); nsb.setWordWrap(True); nsl.addWidget(nsb)
        nbl = QPushButton("Open Website"); nbl.setCursor(Qt.PointingHandCursor); nbl.setStyleSheet("QPushButton{color:#5865F2;background:transparent;border:none;font-size:10px;font-weight:bold;text-align:left;padding:0;}QPushButton:hover{color:white;}")
        nbl.clicked.connect(lambda:webbrowser.open(SITE)); nsl.addWidget(nbl)
        rl.addWidget(note); rl.addSpacing(10)

        # Links
        lk2 = QHBoxLayout(); lk2.setSpacing(12); lk2.setAlignment(Qt.AlignCenter)
        for t,c,u in [("Website","#6C63FF",SITE),("TikTok","#ff0050",TIKTOK),("Discord","#5865F2",DISCORD)]:
            b=QPushButton(t); b.setCursor(Qt.PointingHandCursor); b.setStyleSheet(f"QPushButton{{color:{c};background:transparent;border:none;font-size:11px;font-weight:600;}}QPushButton:hover{{color:white;}}")
            b.clicked.connect(lambda _,url=u:webbrowser.open(url)); lk2.addWidget(b)
        rl.addLayout(lk2)
        r.addWidget(R,1)

        self.discord_id = None; self.username = None

    def _discord_login(self):
        webbrowser.open(f"{SERVER}/api/auth/discord")
        self.discord_status.setText("Waiting for Discord authorization... (check browser)")
        self.discord_status.setStyleSheet("color:#F39C12;")
        self._poll = QTimer(self); self._poll.timeout.connect(self._check); self._poll.start(2000)

    def _check(self):
        w=API("GET",f"{SERVER}/api/auth/status"); w.done.connect(self._discord_result); w.err.connect(lambda _:None); w.start(); self._w=w

    def _discord_result(self, data):
        if data.get("connected"):
            self.discord_id=data.get("discord_id",""); self.username=data.get("username","")
            self._poll.stop()
            self.discord_status.setText(f"Connected as {self.username}"); self.discord_status.setStyleSheet("color:#27ae60;font-weight:bold;")
            self.discord_btn.setEnabled(False)
            self.discord_btn.setStyleSheet("QPushButton{background:#27ae60;color:white;border:none;border-radius:10px;font-size:14px;font-weight:600;}")
            self.discord_btn.setText(f"  {self.username}")
            self.si.setEnabled(True); self.si.setPlaceholderText("ABC123XYZ789")
            self.step2_dot.setStyleSheet("background:#5865F2;border-radius:11px;color:white;font-size:10px;font-weight:bold;")
            self.step2_lbl.setStyleSheet("color:#5865F2;font-size:11px;font-weight:600;")

    def _go(self):
        if not self.discord_id: self.er.setText("Connect your Discord first"); return
        s=self.si.text().strip()
        if not s: self.er.setText("Enter your Zen serial number"); return
        self.btn.setEnabled(False); self.er.setText("")
        w=API("POST",f"{SERVER}/api/login",{"discord_id":self.discord_id,"zen_serial":s})
        w.done.connect(lambda _: (self.btn.setEnabled(True), self.ok.emit(self.discord_id, s)))
        w.err.connect(lambda e: (self.btn.setEnabled(True), self.er.setText(str(e.get("e","Error")))))
        w.start(); self._w=w


# ══════════════════════════════════════════════════════════════
# PORTAL — Shows all scripts
# ══════════════════════════════════════════════════════════════
class Portal(QWidget):
    def __init__(self, did, zid, main):
        super().__init__()
        self.did,self.zid,self.main=did,zid,main; self.purchased=set()
        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # Top bar
        bar=QFrame(); bar.setFixedHeight(56); bar.setStyleSheet(f"QFrame{{background:{CAR};border-bottom:1px solid {BDR};}}")
        bl=QHBoxLayout(bar); bl.setContentsMargins(24,0,24,0)
        br=QLabel("SHOOT 3P TOOLS"); br.setFont(QFont("Segoe UI",12,QFont.Bold)); br.setStyleSheet("color:white;letter-spacing:2px;"); bl.addWidget(br)
        bl.addStretch()
        ui=QLabel(f"{self.did}  |  {self.zid}"); ui.setFont(QFont("Consolas",9)); ui.setStyleSheet(f"color:{SEC};background:#0a0a18;border-radius:5px;padding:5px 12px;"); bl.addWidget(ui)
        lo=QPushButton("Logout"); lo.setCursor(Qt.PointingHandCursor); lo.setStyleSheet(f"QPushButton{{color:{SEC};background:transparent;border:1px solid #333;border-radius:5px;padding:5px 14px;font-size:11px;}}QPushButton:hover{{color:white;border-color:#666;}}")
        lo.clicked.connect(lambda:self.main.show_login()); bl.addWidget(lo)
        root.addWidget(bar)

        # Scrollable content
        sc=QScrollArea(); sc.setWidgetResizable(True); sc.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        bd=QWidget(); bd.setStyleSheet("background:transparent;")
        bdl=QVBoxLayout(bd); bdl.setContentsMargins(40,20,40,40); bdl.setSpacing(16)

        # Info cards
        row=QHBoxLayout(); row.setSpacing(12)
        for t,v,c in [("DISCORD ID",self.did,"#5865F2"),("ZEN SERIAL",self.zid,ACC)]:
            cr=Card(); cr.setFixedHeight(76)
            cl=QVBoxLayout(cr); cl.setContentsMargins(16,10,16,10)
            tl=QLabel(t); tl.setStyleSheet(f"color:{SEC};font-size:10px;font-weight:600;letter-spacing:2px;"); cl.addWidget(tl)
            vl=QLabel(v); vl.setFont(QFont("Consolas",11,QFont.Bold)); vl.setStyleSheet(f"color:{c};"); cl.addWidget(vl)
            row.addWidget(cr)
        bdl.addLayout(row)

        # Verification note
        note=Card("#F39C1244"); nl=QVBoxLayout(note); nl.setContentsMargins(16,12,16,12); nl.setSpacing(4)
        nt=QLabel("AFTER GETTING A SCRIPT: Compile it to your Zen. When opened, you will see a Challenge Code. Go to Discord and type:  !redeem <serial> <discord_id> <challenge_code>  to get your unlock key.")
        nt.setFont(QFont("Segoe UI",10)); nt.setStyleSheet("color:#ddd;"); nt.setWordWrap(True); nl.addWidget(nt)
        dlb=QPushButton("Open Discord"); dlb.setCursor(Qt.PointingHandCursor); dlb.setStyleSheet("QPushButton{color:#5865F2;background:transparent;border:none;font-size:11px;font-weight:bold;text-align:left;padding:0;}QPushButton:hover{color:white;}")
        dlb.clicked.connect(lambda:webbrowser.open(DISCORD)); nl.addWidget(dlb)
        bdl.addWidget(note)

        # Scripts header
        sec=QLabel("ALL SCRIPTS"); sec.setStyleSheet(f"color:{ACC};font-size:13px;font-weight:700;letter-spacing:3px;"); bdl.addWidget(sec)

        # Load purchased status + show all scripts
        self.cards=[]
        grid=QGridLayout(); grid.setSpacing(16); grid.setAlignment(Qt.AlignHCenter)
        for i,s in enumerate(SCRIPTS):
            card=FullScriptCard(s, self.did, self.zid, self.main)
            grid.addWidget(card, i//2, i%2); self.cards.append((s['id'],card))
        bdl.addLayout(grid)
        bdl.addStretch()
        sc.setWidget(bd); root.addWidget(sc)
        self._load_purchases()

    def _load_purchases(self):
        w=API("GET",f"{SERVER}/api/scripts/{self.did}/{self.zid}")
        w.done.connect(self._got_purchases); w.err.connect(lambda _:None); w.start(); self._w=w

    def _got_purchases(self, data):
        orders=data.get("orders",[])
        self.purchased={o.get('product','') for o in orders}
        for sid,card in self.cards:
            if sid in self.purchased:
                order=next((o for o in orders if o.get('product')==sid),None)
                card.set_purchased(order)


class FullScriptCard(QFrame):
    def __init__(self, data, did, zid, main):
        super().__init__()
        self.data=data; self.did=did; self.zid=zid; self.main=main; self.order=None
        self.setStyleSheet(f"QFrame{{background:{CAR};border:1px solid {BDR};border-radius:16px;}}QFrame:hover{{border:1px solid {data['color']}88;}}")
        self.setFixedWidth(470)
        lay=QVBoxLayout(self); lay.setContentsMargins(20,16,20,16); lay.setSpacing(6)

        hdr=QHBoxLayout(); hdr.setSpacing(12)
        ic=QLabel(data['icon']); ic.setFont(QFont("Segoe UI Emoji",30)); ic.setFixedWidth(40); ic.setAlignment(Qt.AlignCenter); hdr.addWidget(ic)
        inf=QVBoxLayout(); inf.setSpacing(1)
        nm=QLabel(data['name']); nm.setFont(QFont("Segoe UI",13,QFont.Bold)); nm.setStyleSheet("color:white;"); inf.addWidget(nm)
        gm=QLabel(data['game']); gm.setFont(QFont("Segoe UI",10)); gm.setStyleSheet(f"color:{data['color']};"); inf.addWidget(gm)
        hdr.addLayout(inf); hdr.addStretch()
        pr=QLabel(f"${data['price']:.2f}"); pr.setFont(QFont("Segoe UI",16,QFont.Bold)); pr.setStyleSheet(f"color:{data['color']};"); hdr.addWidget(pr)
        lay.addLayout(hdr)

        ds=QLabel(data['desc']); ds.setFont(QFont("Segoe UI",10)); ds.setStyleSheet(f"color:{SEC};"); ds.setWordWrap(True); lay.addWidget(ds)

        feat_row=QHBoxLayout(); feat_row.setSpacing(4)
        for f in data['feat'][:6]:
            fl=QLabel(f); fl.setFont(QFont("Segoe UI",8)); fl.setStyleSheet(f"color:#aaa;background:#0a0a18;border-radius:4px;padding:3px 7px;"); feat_row.addWidget(fl)
        lay.addLayout(feat_row)

        btm=QHBoxLayout(); btm.setSpacing(8)
        tier=QLabel(data['tier'].upper()); tier.setFont(QFont("Segoe UI",9,QFont.Bold)); tier.setStyleSheet(f"color:{data['color']};background:{data['color']}18;border:1px solid {data['color']}44;border-radius:4px;padding:4px 12px;")
        btm.addWidget(tier); btm.addStretch()
        self.action_btn=Btn("GET SCRIPT",data['color'],36); self.action_btn.setFixedWidth(130); self.action_btn.clicked.connect(self._action)
        btm.addWidget(self.action_btn)
        self.status_lbl=QLabel(""); self.status_lbl.setFont(QFont("Segoe UI",9)); self.status_lbl.setStyleSheet("color:#27ae60;font-weight:bold;")
        btm.addWidget(self.status_lbl)
        lay.addLayout(btm)

    def set_purchased(self, order):
        self.order=order
        self.action_btn.setText("EXPORT")
        self.action_btn.setStyleSheet(f"QPushButton{{background:#27ae60;color:white;border:none;border-radius:8px;padding:0 24px;font-size:13px;font-weight:600;letter-spacing:1px;}}QPushButton:hover{{background:#2ecc71;}}QPushButton:pressed{{background:#229954;}}")
        exp=order.get('expires_at','') if order else ''
        if exp:
            try: exp=datetime.fromisoformat(exp).strftime('%d %b %Y')
            except: pass
        self.status_lbl.setText(f"Purchased  |  Expires: {exp}")

    def _action(self):
        if self.order:
            seed=hashlib.sha256(f"{self.order['order_id']}:shoot3p-secret-2024".encode()).hexdigest()[:8]
            export_order={**self.order, "seed":seed}
            self.main.export(export_order, self.data)
        else:
            webbrowser.open(SITE)


# ══════════════════════════════════════════════════════════════
# EXPORT PAGE
# ══════════════════════════════════════════════════════════════
class ExportPage(QWidget):
    def __init__(self, order, script, main):
        super().__init__()
        self.order,self.script,self.main=order,script,main
        root=QVBoxLayout(self); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        bar=QFrame(); bar.setFixedHeight(56); bar.setStyleSheet(f"QFrame{{background:{CAR};border-bottom:1px solid {BDR};}}")
        tl=QHBoxLayout(bar); tl.setContentsMargins(24,0,24,0)
        bk=QPushButton("< Back"); bk.setCursor(Qt.PointingHandCursor); bk.setStyleSheet(f"QPushButton{{color:{SEC};background:transparent;border:none;font-size:13px;}}QPushButton:hover{{color:white;}}")
        bk.clicked.connect(lambda:self.main.show_portal()); tl.addWidget(bk); tl.addStretch()
        br=QLabel(f"EXPORT — {script['name']}"); br.setFont(QFont("Segoe UI",12,QFont.Bold)); br.setStyleSheet("color:white;letter-spacing:1px;"); tl.addWidget(br)
        tl.addStretch(); tl.addSpacing(40)
        root.addWidget(bar)

        sc=QScrollArea(); sc.setWidgetResizable(True); sc.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        bd=QWidget(); bd.setStyleSheet("background:transparent;")
        bdl=QVBoxLayout(bd); bdl.setContentsMargins(48,20,48,40); bdl.setSpacing(12)

        # Order info
        oi=Card(); oll=QVBoxLayout(oi); oll.setContentsMargins(16,12,16,12)
        orow=QHBoxLayout(); orow.setSpacing(8)
        for t,v in [("Order",order.get('order_id','')),("Script",script['name']),("Tier",order.get('tier','').upper())]:
            f=QFrame(); f.setStyleSheet("background:#0a0a18;border-radius:5px;")
            fl=QVBoxLayout(f); fl.setContentsMargins(10,6,10,6); fl.setSpacing(1)
            tl2=QLabel(t); tl2.setStyleSheet(f"color:{SEC};font-size:9px;font-weight:600;"); fl.addWidget(tl2)
            vl=QLabel(str(v)); vl.setFont(QFont("Consolas",10,QFont.Bold)); vl.setStyleSheet("color:white;"); fl.addWidget(vl)
            orow.addWidget(f)
        oll.addLayout(orow)
        orow2=QHBoxLayout(); orow2.setSpacing(8)
        for t,v in [("Serial",order.get('zen_serial','')),("Seed",order.get('seed','')),("Expires",order.get('expires_at','N/A'))]:
            f=QFrame(); f.setStyleSheet("background:#0a0a18;border-radius:5px;")
            fl=QVBoxLayout(f); fl.setContentsMargins(10,6,10,6); fl.setSpacing(1)
            tl2=QLabel(t); tl2.setStyleSheet(f"color:{SEC};font-size:9px;font-weight:600;"); fl.addWidget(tl2)
            vl=QLabel(str(v)[:24]); vl.setFont(QFont("Consolas",10,QFont.Bold)); vl.setStyleSheet("color:white;"); fl.addWidget(vl)
            orow2.addWidget(f)
        oll.addLayout(orow2)
        bdl.addWidget(oi)

        sec=QLabel("YOUR PERSONALIZED SCRIPT"); sec.setStyleSheet(f"color:{script['color']};font-size:13px;font-weight:700;letter-spacing:3px;"); bdl.addWidget(sec)
        self.txt=QTextEdit(); self.txt.setReadOnly(True); self.txt.setMinimumHeight(200)
        self.txt.setStyleSheet(f"QTextEdit{{background:#0a0a18;color:#4ECDC4;border:1px solid {BDR};border-radius:10px;padding:14px;font-family:'Consolas',monospace;font-size:11px;}}")
        bdl.addWidget(self.txt)

        bts=QHBoxLayout()
        cp=Btn("COPY TO CLIPBOARD"); cp.clicked.connect(lambda:(QApplication.clipboard().setText(self.txt.toPlainText()),QMessageBox.information(self,"Copied!","Script copied!"))); bts.addWidget(cp)
        sv=Btn("SAVE AS FILE","#4ECDC4"); sv.clicked.connect(self._save); bts.addWidget(sv)
        bdl.addLayout(bts)

        inst=Card("#F39C1244"); il=QVBoxLayout(inst); il.setContentsMargins(18,14,18,14); il.setSpacing(4)
        it=QLabel("NEXT STEPS"); it.setStyleSheet("color:#F39C12;font-size:12px;font-weight:700;letter-spacing:2px;"); il.addWidget(it)
        for s in ["1. Copy or save the script above","2. Open GPC Compiler and paste the script","3. Compile it to your Zen","4. Disconnect Zen and run the script","5. You will see a Challenge Code on screen","6. Go to Discord: !redeem <serial> <discord_id> <challenge>","7. Enter the key you receive into your Zen","8. Script is now unlocked!"]:
            sl=QLabel(f"  {s}"); sl.setFont(QFont("Segoe UI",10)); sl.setStyleSheet("color:#bbb;"); il.addWidget(sl)
        dl=QPushButton("Open Discord"); dl.setCursor(Qt.PointingHandCursor); dl.setStyleSheet("QPushButton{color:#5865F2;background:transparent;border:none;font-size:10px;font-weight:bold;text-align:left;padding:0;}QPushButton:hover{color:white;}")
        dl.clicked.connect(lambda:webbrowser.open(DISCORD)); il.addWidget(dl)
        bdl.addWidget(inst)
        bdl.addStretch()
        sc.setWidget(bd); root.addWidget(sc)
        self._gen()

    def _gen(self):
        seed=self.order.get('seed','DEF'); serial=self.order.get('zen_serial',''); oid=self.order.get('order_id','')
        ch=hashlib.sha256(f"{serial}:{seed}:SECRET".encode()).hexdigest()[:16].upper()
        tp=os.path.join(os.path.dirname(__file__),'..','scripts','template.gpc')
        try:
            with open(tp) as f: gpc=f.read()
        except: gpc="// Template not found"
        gpc=gpc.replace("{{SEED}}",seed).replace("{{ZEN_SERIAL}}",serial).replace("{{ORDER_ID}}",oid).replace("{{CHALLENGE}}",ch)
        self.txt.setPlainText(gpc)

    def _save(self):
        t=self.txt.toPlainText()
        if t:
            p,_=QFileDialog.getSaveFileName(self,"Save",f"{self.script['name'].replace(' ','_')}.gpc","GPC Files (*.gpc)")
            if p:
                with open(p,'w') as f: f.write(t)
                QMessageBox.information(self,"Saved!",f"Saved to {p}")


# ══════════════════════════════════════════════════════════════
# MAIN WINDOW
# ══════════════════════════════════════════════════════════════
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shoot 3P Tools")
        self.setMinimumSize(1060,680); self.resize(1160,760)
        self.did=self.zid=None
        cw=QWidget(); self.setCentralWidget(cw)
        ml=QVBoxLayout(cw); ml.setContentsMargins(0,0,0,0); ml.setSpacing(0)

        self.vid=QVideoWidget(); self.vid.setFixedHeight(160); self.vid.setStyleSheet("background:black;")
        self.player=QMediaPlayer(); self.player.setVideoOutput(self.vid); self.player.setVolume(25)
        for v in VIDEOS:
            if os.path.exists(v):
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile(v))); self.player.play()
                self.player.mediaStatusChanged.connect(lambda s: (self.player.setPosition(0),self.player.play()) if s==QMediaPlayer.EndOfMedia else None)
                break

        self.stack=QStackedWidget()
        ml.addWidget(self.vid,2); ml.addWidget(self.stack,6)

        self.lp=LoginPage(self); self.stack.addWidget(self.lp); self.lp.ok.connect(self._logged)
        self.setStyleSheet(f"background:{BG};color:white;")

    def _logged(self,d,s): self.did,self.zid=d,s; self.show_portal()
    def show_login(self):
        self.lp=LoginPage(self); self.stack.addWidget(self.lp); self.lp.ok.connect(self._logged); self.stack.setCurrentWidget(self.lp)
    def show_portal(self):
        p=Portal(self.did,self.zid,self); self.stack.addWidget(p); self.stack.setCurrentWidget(p)
    def export(self,o,s):
        p=ExportPage(o,s,self); self.stack.addWidget(p); self.stack.setCurrentWidget(p)


if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setStyleSheet("QScrollBar:vertical{background:#0d0d1a;width:7px;}QScrollBar::handle:vertical{background:#333;border-radius:3px;}QScrollBar::handle:vertical:hover{background:#6C63FF;}QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0px;}")
    w=Main(); w.show(); sys.exit(app.exec_())
