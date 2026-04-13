import os, re, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
import qrcode

W, H = int(148/25.4*300), int(105/25.4*300)

def podzial_inteligentny(t):
    slowa = t.split()
    if len(slowa) <= 2: return [t]
    # Dzieli mniej więcej w połowie słów
    srodek = len(slowa) // 2
    return [" ".join(slowa[:srodek]), " ".join(slowa[srodek:])]

def nazwa(s):
    s = re.sub(r'[\\/*?:"<>|]', "", s)
    return s.strip().replace(" ", "_")[:30]

class Apka:
    def __init__(self, r):
        self.r = r
        r.title("Generator A6 - Poprawiony Tekst")
        tk.Label(r, text="Wklej listę (nawet bardzo długie nazwy):").pack(pady=5)
        self.t = tk.Text(r, height=15, width=60); self.t.pack(pady=10)
        tk.Button(r, text="GENERUJ", command=self.go, bg="green", fg="white").pack(pady=10)
        self.p = ttk.Progressbar(r, length=400); self.p.pack(pady=10)

    def go(self):
        dane = self.t.get("1.0", "end").strip().split('\n')
        if not dane: return
        f = filedialog.askdirectory()
        if not f: return
        cel = os.path.join(f, "KODY_A6_POPRAWIONE")
        os.makedirs(cel, exist_ok=True)
        self.p["maximum"] = len(dane)
        
        for i, txt in enumerate(dane, 1):
            txt = txt.strip()
            if not txt: continue
            
            img = Image.new("RGB", (W, H), "white")
            drw = ImageDraw.Draw(img)
            
            # 1. KOD QR (zajmuje 65% wysokości)
            qr_size = int(H * 0.65)
            qr = qrcode.make(txt).convert("RGB").resize((qr_size, qr_size))
            img.paste(qr, ((W - qr_size)//2, 30))
            
            # 2. DYNAMICZNY TEKST
            linie = podzial_inteligentny(txt)
            max_width = W - 100 # Margines boczny, żeby tekst nie dotykał krawędzi
            font_size = 140     # Startowa wielkość (bardzo duża)
            
            # Pętla dopasowująca rozmiar czcionki
            while font_size > 40:
                try: fnt = ImageFont.truetype("arialbd.ttf", font_size)
                except: fnt = ImageFont.load_default()
                
                # Sprawdź, czy najdłuższa linia mieści się w szerokości
                szerokosci = [drw.textlength(l, font=fnt) for l in linie]
                if max(szerokosci) <= max_width:
                    break
                font_size -= 5 # Zmniejszaj o 5px aż zacznie pasować
            
            y_text = int(H * 0.72)
            for linia in linie:
                tw = drw.textlength(linia, font=fnt)
                drw.text(((W - tw)//2, y_text), linia, fill="black", font=fnt)
                y_text += int(font_size * 1.1) # Dynamiczny odstęp między liniami
                
            # 3. ZNACZNIKI CIĘCIA (delikatne)
            L = 30
            for x, y in [(0,0), (W,0), (0,H), (W,H)]:
                x1, y1 = x, y
                x2 = x-L if x > 0 else x+L
                y2 = y-L if y > 0 else y+L
                drw.line([(x, y1), (x2, y1)], fill="#DDDDDD", width=1)
                drw.line([(x1, y), (x1, y2)], fill="#DDDDDD", width=1)
            
            img.save(os.path.join(cel, f"{i:04d}_{nazwa(txt)}.png"), dpi=(300,300))
            self.p["value"] = i; self.r.update()
            
        messagebox.showinfo("OK", "Gotowe! Teksty zostały dopasowane.")

if __name__ == "__main__":
    root = tk.Tk(); Apka(root); root.mainloop()
