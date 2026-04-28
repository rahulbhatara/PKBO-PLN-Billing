"""
Sistem Perhitungan Tagihan Listrik PLN — Flask API

API:
  POST /api/hitung  — Hitung tagihan berdasarkan golongan
  GET  /            — Halaman web

Polimorfisme terjadi di /api/hitung: satu endpoint memproses 5 golongan
berbeda, memanggil method to_dict() yang SAMA tapi hasilnya BERBEDA.
"""
from flask import Flask, render_template, request, jsonify
from models import (
    PelangganRumahTangga, PelangganBisnis,
    PelangganIndustri, PelangganPemerintah, PelangganMultiguna
)

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/hitung', methods=['POST'])
def hitung_tagihan():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body harus JSON"}), 400

        for f in ['golongan', 'id_pelanggan', 'nama', 'daya_terpasang', 'pemakaian_kwh']:
            if f not in data:
                return jsonify({"error": f"Field '{f}' wajib diisi"}), 400

        gol = data['golongan']
        id_p = str(data['id_pelanggan'])
        nama = str(data['nama'])
        daya = int(data['daya_terpasang'])
        kwh = float(data['pemakaian_kwh'])
        terlambat = int(data.get('hari_terlambat', 0))

        # === POLIMORFISME: satu variabel, lima kemungkinan objek ===
        pelanggan = None

        if gol == 'rumah_tangga':
            pelanggan = PelangganRumahTangga(id_p, nama, daya, kwh, terlambat)

        elif gol == 'bisnis':
            pelanggan = PelangganBisnis(
                id_p, nama, daya, kwh, terlambat,
                kwh_wbp=float(data.get('kwh_wbp', 0)),
                kwh_lwbp=float(data.get('kwh_lwbp', 0)),
                faktor_k=float(data.get('faktor_k', 1.4)),
                kvarh_terukur=float(data.get('kvarh_terukur', 0)),
                power_factor=float(data.get('power_factor', 0.85)),
            )

        elif gol == 'industri':
            pelanggan = PelangganIndustri(
                id_p, nama, daya, kwh, terlambat,
                kwh_wbp=float(data.get('kwh_wbp', 0)),
                kwh_lwbp=float(data.get('kwh_lwbp', 0)),
                faktor_k=float(data.get('faktor_k', 1.4)),
                kvarh_terukur=float(data.get('kvarh_terukur', 0)),
                power_factor=float(data.get('power_factor', 0.85)),
            )

        elif gol == 'pemerintah':
            pelanggan = PelangganPemerintah(
                id_p, nama, daya, kwh, terlambat,
                sub_golongan=str(data.get('sub_golongan', 'P-1')),
                kwh_wbp=float(data.get('kwh_wbp', 0)),
                kwh_lwbp=float(data.get('kwh_lwbp', 0)),
                faktor_k=float(data.get('faktor_k', 1.4)),
                kvarh_terukur=float(data.get('kvarh_terukur', 0)),
                power_factor=float(data.get('power_factor', 0.85)),
            )

        elif gol == 'multiguna':
            pelanggan = PelangganMultiguna(
                id_p, nama, daya, kwh, terlambat,
                faktor_n=float(data.get('faktor_n', 1.0)),
                kvarh_terukur=float(data.get('kvarh_terukur', 0)),
                power_factor=float(data.get('power_factor', 0.85)),
            )

        else:
            return jsonify({"error": f"Golongan '{gol}' tidak dikenal"}), 400

        # Method SAMA, perilaku BERBEDA — polimorfisme!
        return jsonify(pelanggan.to_dict())

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Kesalahan: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
