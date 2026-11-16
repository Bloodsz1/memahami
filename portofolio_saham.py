"""
Pelacak Portofolio Saham (IDX) - project belajar Python dasar + OOP.

Konsep yang dipakai:
- Python dasar : variabel, if/else, loop, fungsi, dictionary, f-string, try/except
- OOP          : class, __init__, method, @property, @classmethod, __str__
- File         : simpan & baca data dengan JSON
"""
import json

LEMBAR_PER_LOT = 100          # 1 lot saham di BEI = 100 lembar
FILE_DATA = "portofolio.json"


def rupiah(angka, dengan_tanda=False):
    """Ubah angka jadi format rupiah: 1500000 -> +Rp1.500.000"""
    teks = f"{abs(angka):,.0f}".replace(",", ".")
    if angka < 0:
        return f"-Rp{teks}"
    elif angka > 0 and dengan_tanda:
        return f"+Rp{teks}"
    else:
        return f"Rp{teks}"


# ===== CLASS 1: Saham -> mewakili SATU saham yang kamu pegang =====
class Saham:
    def __init__(self, kode, lot, harga_beli, harga_sekarang=None):
        self.kode = kode.upper()
        self.lot = lot
        self.harga_beli = harga_beli
        # kalau harga sekarang belum diisi, anggap sama dengan harga beli
        self.harga_sekarang = harga_sekarang or harga_beli

    @property
    def lembar(self):
        """Jumlah lembar = lot x 100. Dipanggil tanpa tanda kurung: saham.lembar"""
        return self.lot * LEMBAR_PER_LOT

    def modal(self):
        return self.lembar * self.harga_beli

    def nilai_sekarang(self):
        return self.lembar * self.harga_sekarang

    def untung_rugi(self):
        return self.nilai_sekarang() - self.modal()

    def persen(self):
        if self.modal() == 0:
            return 0
        return self.untung_rugi() / self.modal() * 100

    def sedang_untung(self):
        return self.untung_rugi() > 0

    def to_dict(self):
        """Ubah objek jadi dictionary supaya bisa disimpan ke JSON."""
        return {
            "kode": self.kode,
            "lot": self.lot,
            "harga_beli": self.harga_beli,
            "harga_sekarang": self.harga_sekarang,
        }

    @classmethod
    def dari_dict(cls, data):
        """Kebalikan to_dict: bikin objek Saham dari dictionary."""
        return cls(data["kode"], data["lot"], data["harga_beli"], data["harga_sekarang"])

    def __str__(self):
        tanda = "+" if self.untung_rugi() >= 0 else ""
        return (f"{self.kode:<6} {self.lot:>4} lot | beli {rupiah(self.harga_beli):>10} "
                f"| kini {rupiah(self.harga_sekarang):>10} "
                f"| P/L {rupiah(self.untung_rugi(), dengan_tanda=True):>12} ({tanda}{self.persen():.2f}%)")


# ===== CLASS 2: Portofolio -> kumpulan banyak Saham =====
class Portofolio:
    def __init__(self):
        self.daftar = {}   # dictionary: {"BBCA": objek Saham, ...}

    def beli(self, kode, lot, harga):
        kode = kode.upper()
        if kode in self.daftar:
            # sudah punya -> hitung harga rata-rata (average price)
            lama = self.daftar[kode]
            total_modal = lama.modal() + lot * LEMBAR_PER_LOT * harga
            total_lot = lama.lot + lot
            lama.harga_beli = total_modal / (total_lot * LEMBAR_PER_LOT)
            lama.lot = total_lot
            lama.harga_sekarang = harga
        else:
            self.daftar[kode] = Saham(kode, lot, harga)

    def jual(self, kode, lot):
        kode = kode.upper()
        if kode not in self.daftar:
            raise ValueError(f"Kamu tidak punya saham {kode}.")
        saham = self.daftar[kode]
        if lot > saham.lot:
            raise ValueError(f"Lot {kode} kamu hanya {saham.lot}.")
        saham.lot -= lot
        if saham.lot == 0:
            del self.daftar[kode]   # habis -> hapus dari portofolio

    def update_harga(self, kode, harga):
        kode = kode.upper()
        if kode not in self.daftar:
            raise ValueError(f"Kamu tidak punya saham {kode}.")
        self.daftar[kode].harga_sekarang = harga

    def total_modal(self):
        return sum(s.modal() for s in self.daftar.values())

    def total_nilai(self):
        return sum(s.nilai_sekarang() for s in self.daftar.values())

    def tampilkan(self):
        if not self.daftar:
            print("\nPortofolio masih kosong.")
            return
        print("\n" + "=" * 85)
        for saham in self.daftar.values():
            print(saham)
        print("=" * 85)
        modal, nilai = self.total_modal(), self.total_nilai()
        pl = nilai - modal
        persen = pl / modal * 100 if modal else 0
        print(f"Total modal : {rupiah(modal)}")
        print(f"Nilai kini  : {rupiah(nilai)}")
        print(f"Untung/Rugi : {rupiah(pl, dengan_tanda=True)} ({persen:.2f}%)")

    def simpan(self):
        with open(FILE_DATA, "w") as f:
            json.dump([s.to_dict() for s in self.daftar.values()], f, indent=2)

    def muat(self):
        try:
            with open(FILE_DATA) as f:
                for data in json.load(f):
                    saham = Saham.dari_dict(data)
                    self.daftar[saham.kode] = saham
        except FileNotFoundError:
            pass   # pertama kali jalan, file belum ada -> tidak apa-apa


# ===== Program utama: menu interaktif =====
def baca_angka(pesan):
    """Minta input angka. Ulangi terus sampai user mengisi dengan benar."""
    while True:
        try:
            nilai = float(input(pesan))
            if nilai <= 0:
                print("Angka harus lebih dari 0.")
                continue
            return nilai
        except ValueError:
            print("Masukkan angka yang valid.")


def main():
    portofolio = Portofolio()
    portofolio.muat()

    while True:
        print("\n--- PORTOFOLIO SAHAM ---")
        print("1. Beli saham")
        print("2. Jual saham")
        print("3. Update harga saham")
        print("4. Lihat portofolio")
        print("0. Keluar")
        pilihan = input("Pilih menu: ").strip()

        try:
            if pilihan == "1":
                kode = input("Kode saham (mis. BBCA): ")
                lot = int(baca_angka("Jumlah lot: "))
                harga = baca_angka("Harga beli per lembar: ")
                portofolio.beli(kode, lot, harga)
                print("Berhasil ditambahkan.")
            elif pilihan == "2":
                kode = input("Kode saham: ")
                lot = int(baca_angka("Jumlah lot dijual: "))
                portofolio.jual(kode, lot)
                print("Berhasil dijual.")
            elif pilihan == "3":
                kode = input("Kode saham: ")
                harga = baca_angka("Harga sekarang per lembar: ")
                portofolio.update_harga(kode, harga)
                print("Harga diperbarui.")
            elif pilihan == "4":
                portofolio.tampilkan()
            elif pilihan == "0":
                print("Data tersimpan. Sampai jumpa!")
                break
            else:
                print("Menu tidak dikenal.")
        except ValueError as error:
            print(f"Error: {error}")

        portofolio.simpan()   # simpan otomatis setiap selesai aksi


if __name__ == "__main__":
    main()
