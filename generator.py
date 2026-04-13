import os, re, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
import qrcode

# --- USTAWIENIA WYGLĄDU (możesz tu zmieniać) ---
ROZMIAR_CZCIONKI = 100         # Wielkość liter
INTERLINIA = 110               # Odstęp między liniami (jeśli tekst się zawija)
MARGINES_RAMKI = 80            # Odległość czarnej ramki od brzegu kartki
POZYCJA_TEKSTU_Y = 0.78        # Tekst zaczyna się na 78% wysokości (0.0 - 1.0)
MAX_ZNAKOW_W_LINII = 20        # Kiedy ma dzielić tekst na dwie linie
# ----------------------------------------------

W, H = int(148/25.4*300), int(105/25.4*300)

def podzial(t, max_c=MAX_ZNAKOW_W_LINII):
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
        r.title("QR Generator - Skupienie na Tekście")
        tk.Label(r, text="Wklej listę (linia=kod):").pack(pady=5)
        self.t = tk.Text(r, height=15, width=60); self.t.pack(pady=10)
        tk.Button(r, text="GENERUJ", command=self.go, bg="blue", fg="white", font=("Arial", 10, "bold")).pack(pady=10)
        self.p = ttk.Progressbar(r, length=400); self.p.pack(pady=10)

    def go(self):
        dane = self.t.get("1.0", "end").strip().split('\n')
        if not dane: return
        f = filedialog.askdirectory()
        if not f: return
        cel = os.path.join(f, "KODY_QR_NOWY_FORMAT")
        os.makedirs(cel, exist_ok=True)
        self.p["maximum"] = len(dane)
        
        for i, txt in enumerate(dane, 1):
            txt = txt.strip()
            if not txt: continue
            
            img = Image.new("RGB", (W, H), "white")
            drw = ImageDraw.Draw(img)
            
            # 1. Kod QR - mniejszy i wyśrodkowany
            qr_size = int(H * 0.45)
            qr = qrcode.make(txt).convert("RGB").resize((qr_size, qr_size))
            img.paste(qr, ((W - qr_size)//2, int(H * 0.18)))
            
            # 2. Formatowanie Tekstu
            try:
                # Szukamy czcionki pogrubionej (Arial Bold)
                fnt = ImageFont.truetype("arialbd.ttf", ROZMIAR_CZCIONKI)
            except:
                # Jeśli nie ma Arial, spróbuj innej systemowej lub domyślnej
                try: fnt = ImageFont.truetype("DejaVuSans-Bold.ttf", ROZMIAR_CZCIONKI)
                except: fnt = ImageFont.load_default()
            
            linie = podzial(txt)
            y_start = int(H * POZYCJA_TEKSTU_Y)
            
            for linia in linie:
                # Obliczanie środka dla każdej linii
                tw = drw.textlength(linia, font=fnt)
                drw.text(((W - tw)//2, y_start), linia, fill="black", font=fnt)
                y_start += INTERLINIA # Przejście do nowej linii
                
            # 3. Ramka z dużym marginesem (zgodnie z Twoim zdjęciem)
            drw.rectangle([MARGINES_RAMKI, MARGINES_RAMKI, W - MARGINES_RAMKI, H - MARGINES_RAMKI], 
                          outline="black", width=4)
            
            img.save(os.path.join(cel, f"{i:04d}_{nazwa(txt)}.png"), dpi=(300,300))
            self.p["value"] = i; self.r.update()
            
        messagebox.showinfo("OK", "Gotowe!")

if __name__ == "__main__":
    root = tk.Tk(); Apka(root); root.mainloop()
