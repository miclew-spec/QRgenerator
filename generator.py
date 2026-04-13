import os, re, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
import qrcode

# USTAWIENIA A6 300 DPI
W, H = int(148/25.4*300), int(105/25.4*300)

def podzial(t, max_c=18): # Skróciłem max_c, bo przy dużym QR tekst musi być zwarty
    if len(t) <= max_c or " " not in t: return [t]
    m = len(t) // 2
    sp = [i for i, c in enumerate(t) if c == ' ']
    if not sp: return [t]
    b = min(sp, key=lambda x: abs(x - m))
    return [t[:b].strip(), t[b:].strip()]

def nazwa(s):
    s = re.sub(r'[\\/*?:"<>|]', "", s)
    return s.strip().replace(" ", "_")[:30]

class Apka:
    def __init__(self, r):
        self.r = r
        r.title("QR Generator A6 - Duży Kod + Znaczniki")
        tk.Label(r, text="Wklej listę:").pack(pady=5)
        self.t = tk.Text(r, height=15, width=60); self.t.pack(pady=10)
        tk.Button(r, text="GENERUJ", command=self.go, bg="black", fg="white", font=("Arial", 10, "bold")).pack(pady=10)
        self.p = ttk.Progressbar(r, length=400); self.p.pack(pady=10)

    def go(self):
        dane = self.t.get("1.0", "end").strip().split('\n')
        if not dane: return
        f = filedialog.askdirectory()
        if not f: return
        cel = os.path.join(f, "ETYKIETY_PRO_A6")
        os.makedirs(cel, exist_ok=True)
        self.p["maximum"] = len(dane)
        
        for i, txt in enumerate(dane, 1):
            txt = txt.strip()
            if not txt: continue
            
            img = Image.new("RGB", (W, H), "white")
            drw = ImageDraw.Draw(img)
            
            # 1. KOD QR - Zwiększony do ok. 2/3 wysokości (ok. 67-70%)
            qr_size = int(H * 0.68) 
            qr = qrcode.make(txt).convert("RGB").resize((qr_size, qr_size))
            img.paste(qr, ((W - qr_size)//2, int(H * 0.05)))
            
            # 2. TEKST - Pogrubiony, dopasowany pod duży kod
            try: fnt = ImageFont.truetype("arialbd.ttf", 110)
            except: fnt = ImageFont.load_default()
            
            linie = podzial(txt)
            y_text = int(H * 0.75) # Start tekstu zaraz pod wielkim kodem
            
            for linia in linie:
                tw = drw.textlength(linia, font=fnt)
                drw.text(((W - tw)//2, y_text), linia, fill="black", font=fnt)
                y_text += 120
                
            # 3. LINIE CIĘCIA (Zamiast ramki)
            # Rysujemy małe "narożniki" na krawędziach formatu A6
            L = 40 # Długość linii cięcia
            # Lewy górny
            drw.line([(0, 0), (L, 0)], fill="black", width=2)
            drw.line([(0, 0), (0, L)], fill="black", width=2)
            # Prawy górny
            drw.line([(W, 0), (W-L, 0)], fill="black", width=2)
            drw.line([(W, 0), (W, L)], fill="black", width=2)
            # Lewy dolny
            drw.line([(0, H), (L, H)], fill="black", width=2)
            drw.line([(0, H), (0, H-L)], fill="black", width=2)
            # Prawy dolny
            drw.line([(W, H), (W-L, H)], fill="black", width=2)
            drw.line([(W, H), (W, H-L)], fill="black", width=2)
            
            # ZAPIS
            img.save(os.path.join(cel, f"{i:04d}_{nazwa(txt)}.png"), dpi=(300,300))
            self.p["value"] = i; self.r.update()
            
        messagebox.showinfo("OK", "Wygenerowano etykiety ze znacznikami cięcia!")

if __name__ == "__main__":
    root = tk.Tk(); Apka(root); root.mainloop()
