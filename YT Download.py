import customtkinter as ctk
import yt_dlp
import os
import threading
import tkinter as tk
from tkinter import messagebox, filedialog

# === PENGATURAN ===
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PengunduhYouTubePRO(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pengunduh YouTube PRO")
        self.geometry("700x520")
        self.resizable(False, False)

        # Variabel
        self.folder_unduhan = os.path.join(os.getcwd(), "unduhan")
        os.makedirs(self.folder_unduhan, exist_ok=True)

        self.format_pilihan = ctk.StringVar(value="Video (MP4)")
        self.kualitas_pilihan = ctk.StringVar(value="720p")

        self.nama_file_saat_ini = ""
        self.buat_tampilan()

    def buat_tampilan(self):
        # Judul
        ctk.CTkLabel(self, text="Pengunduh YouTube PRO",
                     font=ctk.CTkFont(size=26, weight="bold")).pack(pady=15)

        # Kotak URL
        frame_url = ctk.CTkFrame(self)
        frame_url.pack(pady=10, padx=40, fill="x")

        self.kolom_url = ctk.CTkEntry(
            frame_url,
            placeholder_text="Tempel URL YouTube di sini",
            height=45,
            font=ctk.CTkFont(size=14)
        )
        self.kolom_url.pack(pady=12, padx=20, fill="x")
        self.kolom_url.bind("<Return>", lambda e: self.mulai_unduh_di_thread())

        # Pilihan Format & Kualitas
        frame_pilih = ctk.CTkFrame(self)
        frame_pilih.pack(pady=10, padx=40, fill="x")

        ctk.CTkLabel(frame_pilih, text="Format:").grid(row=0, column=0, padx=10, pady=10)
        pilih_format = ctk.CTkComboBox(
            frame_pilih,
            values=["Video (MP4)", "Audio (MP3)"],
            variable=self.format_pilihan,
            width=130,
            command=self.perbarui_pilihan_kualitas
        )
        pilih_format.grid(row=0, column=1, padx=10)

        ctk.CTkLabel(frame_pilih, text="Kualitas:").grid(row=0, column=2, padx=10)
        self.pilih_kualitas = ctk.CTkComboBox(
            frame_pilih,
            values=["480p", "720p", "1080p", "Terbaik"],
            variable=self.kualitas_pilihan,
            width=130
        )
        self.pilih_kualitas.grid(row=0, column=3, padx=10)

        # Pilih Folder
        ctk.CTkButton(
            frame_pilih,
            text="Pilih Folder",
            width=110,
            command=self.pilih_folder
        ).grid(row=0, column=4, padx=10)

        self.label_folder = ctk.CTkLabel(
            self,
            text=f"Folder: {self.folder_unduhan}",
            font=ctk.CTkFont(size=10),
            text_color="gray70",
            wraplength=650
        )
        self.label_folder.pack(pady=(0, 10))

        # Tombol Unduh
        self.tombol_unduh = ctk.CTkButton(
            self,
            text="UNDUH",
            height=50,
            font=ctk.CTkFont(size=20, weight="bold"),
            command=self.mulai_unduh_di_thread
        )
        self.tombol_unduh.pack(pady=10, fill="x", padx=120)

        # Progress Bar
        self.baris_kemajuan = ctk.CTkProgressBar(self, width=550)
        self.baris_kemajuan.pack(pady=5)
        self.baris_kemajuan.set(0)

        # Status
        self.label_status = ctk.CTkLabel(self, text="Tempel URL untuk mulai...",
                                         font=ctk.CTkFont(size=12))
        self.label_status.pack(pady=5)

        # Nama File
        self.label_nama_file = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray70",
            wraplength=650
        )
        self.label_nama_file.pack(pady=(0, 10))

        # Tombol Bawah
        frame_bawah = ctk.CTkFrame(self)
        frame_bawah.pack(pady=10, fill="x", padx=40)

        ctk.CTkButton(frame_bawah, text="Buka Folder",
                      command=lambda: os.startfile(self.folder_unduhan))\
            .pack(side="left", padx=10)
        ctk.CTkButton(frame_bawah, text="Hapus Info",
                      command=self.hapus_info).pack(side="left", padx=5)

    # ------------------- FUNGSI -------------------

    def perbarui_pilihan_kualitas(self, pilihan):
        if pilihan == "Audio (MP3)":
            self.pilih_kualitas.configure(state="disabled")
            self.kualitas_pilihan.set("Tidak Berlaku")
        else:
            self.pilih_kualitas.configure(state="normal")
            self.kualitas_pilihan.set("720p")

    def pilih_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_unduhan)
        if folder:
            self.folder_unduhan = folder
            self.label_folder.configure(text=f"Folder: {folder}")

    def hapus_info(self):
        self.kolom_url.delete(0, 'end')
        self.baris_kemajuan.set(0)
        self.label_status.configure(text="Tempel URL untuk mulai...")
        self.label_nama_file.configure(text="")

    def ambil_format_kualitas(self):
        peta = {
            "480p": "bestvideo[height<=480]+bestaudio/best",
            "720p": "bestvideo[height<=720]+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best",
            "Terbaik": "bestvideo+bestaudio/best"
        }
        return peta.get(self.kualitas_pilihan.get(), "bestvideo+bestaudio/best")

    def mulai_unduh_di_thread(self):
        threading.Thread(target=self.proses_unduhan, daemon=True).start()

    def proses_unduhan(self):
        url = self.kolom_url.get().strip()
        if not url:
            self.after(0, lambda: messagebox.showwarning("Peringatan", "URL tidak boleh kosong!"))
            return

        self.after(0, lambda: [
            self.tombol_unduh.configure(state="disabled"),
            self.label_status.configure(text="Memulai unduhan..."),
            self.baris_kemajuan.set(0),
            self.label_nama_file.configure(text="")
        ])

        opsi = {
            'outtmpl': f'{self.folder_unduhan}/%(title)s.%(ext)s',
            'progress_hooks': [self.hook_kemajuan],
            'ignoreerrors': True,
            'no_warnings': True,
        }

        # Konfigurasi Format
        if self.format_pilihan.get() == "Audio (MP3)":
            opsi['format'] = 'bestaudio/best'
            opsi['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            opsi['format'] = self.ambil_format_kualitas()
            opsi['merge_output_format'] = 'mp4'

        try:
            with yt_dlp.YoutubeDL(opsi) as ydl:
                info = ydl.extract_info(url, download=True)
                self.nama_file_saat_ini = info.get('title', 'File tidak diketahui')

            self.after(0, lambda: [
                self.label_status.configure(text="Selesai."),
                self.label_nama_file.configure(text=f"File: {self.nama_file_saat_ini}"),
                messagebox.showinfo("Sukses", "Unduhan selesai!"),
                os.startfile(self.folder_unduhan)
            ])
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.after(0, lambda: self.tombol_unduh.configure(state="normal"))

    def hook_kemajuan(self, data):
        if data['status'] == 'downloading':
            persen = float(data.get('_percent_str', '0').replace('%', '').strip()) / 100
            kecepatan = data.get('speed')
            speed_str = f"{kecepatan / (1024*1024):.1f} MB/s" if kecepatan else "..."

            self.after(0, lambda: [
                self.baris_kemajuan.set(persen),
                self.label_status.configure(
                    text=f"Mengunduh... {data.get('_percent_str','0%')} ({speed_str})"
                )
            ])
        elif data['status'] == 'finished':
            self.after(0, lambda: self.label_status.configure(text="Memproses..."))

# === JALANKAN APLIKASI ===
if __name__ == "__main__":
    app = PengunduhYouTubePRO()
    app.mainloop()
