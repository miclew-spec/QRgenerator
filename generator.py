import os, re, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
import qrcode

# Rozdzielczość A6 (148x105mm) przy 300 DPI
W_PX, H_PX = int(148/25.4*300), int(105/25.4*300)

def split_text(text, max_chars=22):
    """Dzieli tekst na dwie linie w miejscu spacji."""
    if len(text) <= max_chars or " " not in text: return
    mid = len(text) // 2
    spaces =
    best = min(spaces, key=lambda x: abs(x - mid))
    return.strip(), text[best:].strip()]

def clean_filename(s):
    """Czyści nazwę dania, by nadawała się na nazwę pliku."""
    s = re.sub(r'[\\/*?:"<>|]', "", s) # usuwa znaki zakazane w Windows
    return s.strip().replace(" ", "_")[:30] # zamienia spacje na podkreślniki i skraca

class App:
    def __init__(self, root):
        self.root = root
        root.title("Generator QR A6 - Nazewnictwo")
        root.geometry("500x550")
        tk.Label(root, text="Wklej listę (każda linia = jeden plik):").pack(pady=5)
        self.txt_input = tk.Text(root, height=15, width=60); self.txt_input.pack(pady=10)
        tk.Button(root, text="GENERUJ KODY QR", command=self.run, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), padx=20, pady=10).pack(pady=10)
        self.pb = ttk.Progressbar(root, length=400, mode="determinate"); self.pb.pack(pady=10)
        self.lbl = tk.Label(root, text="Gotowy do pracy"); self.lbl.pack()

    def run(self):
        content = self.txt_input.get("1.0", tk.END).strip()
        if not content: return
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        
        save_path = filedialog.askdirectory(title="Gdzie zapisać kody QR?")
        if not save_path: return
        
        target_dir = os.path.join(save_path, "KODY_QR_A6")
        os.makedirs(target_dir, exist_ok=True)
        
        total = len(lines)
        self.pb["maximum"] = total

        for i, raw_text in enumerate(lines, 1):
            canvas = Image.new("RGB", (W_PX, H_PX), "white")
            draw = ImageDraw.Draw(canvas)
            
            # QR Code - powiększony
            qr = qrcode.QRCode(border=2, error_correction=qrcode.constants.ERROR_CORRECT_M)
            qr.add_data(raw_text); qr.make(fit=True)
            qr_img = qr.make_image().convert("RGB")
            qr_size = int(H_PX * 0.65)
            qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
            canvas.paste(qr_img, ((W_PX - qr_size)//2, int(H_PX * 0.05)))

            # Tekst - Pogrubiony Arial Bold
            parts = split_text(raw_text)
            y_pos = int(H_PX * 0.05) + qr_size + 10
            for p in parts:
                f_size = 85 # Duży rozmiar bazowy
                while True:
                    try: font = ImageFont.truetype("arialbd.ttf", f_size)
                    except: font = ImageFont.load_default()
                    bbox = draw.textbbox((0, 0), p, font=font)
                    tw = bbox[2] - bbox[0]
                    if tw <= (W_PX - 80) or f_size <= 25: break
                    f_size -= 2
                draw.text(((W_PX - tw)//2, y_pos), p, fill="black", font=font)
                y_pos += f_size + 8

            # Ramka cięcia
            draw.rectangle([10, 10, W_PX-10, H_PX-10], outline="black", width=2)
            
            # NAZEWNICTWO PLIKU: Numer_Nazwa.png
            file_name = f"{i:03d}_{clean_filename(raw_text)}.png"
            canvas.save(os.path.join(target_dir, file_name), dpi=(300,300))
            
            self.pb["value"] = i
            self.lbl.config(text=f"Generowanie: {i}/{total}")
            self.root.update()

        messagebox.showinfo("Sukces", f"Zakończono! Pliki zapisane w folderze: {target_dir}")

if __name__ == "__main__":
    root = tk.Tk(); App(root); root.mainloop()
