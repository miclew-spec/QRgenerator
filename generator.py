import os, re, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
import qrcode

# USTAWIENIA A6 300 DPI (1748 x 1240 px)
W, H = int(148/25.4*300), int(105/25.4*300)

def podzial_dla_slabowidzacych(t):
    # Dla osób niedowidzących lepiej mieć mniej słów w linii, ale ogromnych
    slowa = t.split()
    if len(slowa) > 2:
        return [" ".join(slowa[:len(slowa)//2]), " ".join(slowa[len(slowa)//2:])]
    return [t]

def nazwa(s):
    s = re.sub(r'[\\/*?:"<>|]', "", s)
    return s.strip().replace(" ", "_")[:30]

class Apka:
    def __init__(self, r):
        self.r = r
        r.title("GENERATOR DLA NIEDOWIDZĄCYCH")
        tk.Label(r, text="Lista potraw / produktów:", font=("Arial", 12, "bold")).pack(pady=5)
        self.t = tk.Text(r, height=15, width=60); self.t.pack(pady=10)
        tk.Button(r, text="GENERUJ ETYKIETY", command=self.go, bg="yellow", fg="black", font=("Arial", 12, "bold")).pack(pady=10)
        self.p = ttk.Progressbar(r, length=400); self.p.pack(pady=10)

    def go(self):
        dane = self.t.get("1.0", "end").strip().split('\n')
        if not dane: return
        f = filedialog.askdirectory()
        if not f: return
        cel = os.path.join(f, "ETYKIETY_DLA_NIEDOWIDZACYCH")
        os.makedirs(cel, exist_ok=True)
        self.p["maximum"] = len(dane)
        
        for i, txt in enumerate(dane, 1):
            txt = txt.strip()
            if not txt: continue
            
            img = Image.new("RGB", (W, H), "white")
            drw = ImageDraw.Draw(img)
            
            # 1. GIGANTYCZNY KOD QR (zajmuje ok. 70% wysokości)
            # Używamy wysokiej korekcji błędów (ERROR_CORRECT_H), żeby kod był czytelny nawet przy słabym świetle
            qr_api = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=1)
            qr_api.add_data(txt)
            qr_api.make(fit=True)
            qr_img = qr_api.make_image(fill_color="black", back_color="white").convert("RGB")
            
            qr_size = int(H * 0.70)
            qr_img = qr_img.resize((qr_size, qr_size), Image.NEAREST)
            img.paste(qr_img, ((W - qr_size)//2, 20))
            
            # 2. TEKST - EKSTREMALNIE DUŻY I POGRUBIONY
            # Zwiększona czcionka do 130-150 pkt dla maksymalnej czytelności
            try: fnt = ImageFont.truetype("arialbd.ttf", 140)
            except: fnt = ImageFont.load_default()
            
            linie = podzial_dla_slabowidzacych(txt)
            y_text = int(H * 0.72)
            
            for linia in linie:
                tw = drw.textlength(linia, font=fnt)
                # Rysujemy tekst
                drw.text(((W - tw)//2, y_text), linia, fill="black", font=fnt)
                y_text += 150 # Duży odstęp między liniami, żeby litery się nie zlewały
                
            # 3. ZNACZNIKI CIĘCIA (bardzo delikatne, by nie rozpraszały)
            L = 30
            for x, y in [(0,0), (W,0), (0,H), (W,H)]:
                x1 = x; y1 = y
                x2 = x-L if x > 0 else x+L
                y2 = y-L if y > 0 else y+L
                drw.line([(x, y1), (x2, y1)], fill="#CCCCCC", width=1) # Jasnoszare, żeby nie myliły się z tekstem
                drw.line([(x1, y), (x1, y2)], fill="#CCCCCC", width=1)
            
            img.save(os.path.join(cel, f"{i:04d}_{nazwa(txt)}.png"), dpi=(300,300))
            self.p["value"] = i; self.r.update()
            
        messagebox.showinfo("Gotowe", "Etykiety o wysokiej czytelności zostały zapisane.")

if __name__ == "__main__":
    root = tk.Tk(); Apka(root); root.mainloop()
