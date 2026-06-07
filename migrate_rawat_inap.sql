-- ============================================================
-- MIGRASI: Modul Rekam Medis Rawat Inap
-- Jalankan sekali di SQL Editor Supabase / psql Anda
-- ============================================================

-- Tabel utama rawat inap (Kajian Awal)
CREATE TABLE IF NOT EXISTS rawat_inap (
  id SERIAL PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(email) ON DELETE CASCADE,
  organization TEXT,
  no_rm TEXT,
  nama TEXT NOT NULL,
  no_bpjs TEXT,
  tgl_lahir TEXT,
  jk TEXT,
  jaminan TEXT DEFAULT 'BPJS',
  no_hp TEXT,
  alamat TEXT,
  kebutuhan TEXT DEFAULT '[]',       -- JSON array
  bicara TEXT DEFAULT 'Jelas',
  komunikasi TEXT DEFAULT 'Verbal',
  emosi TEXT DEFAULT 'Tenang',
  alergi TEXT DEFAULT '',
  alergi_ket TEXT DEFAULT '',
  rpd TEXT DEFAULT '[]',             -- JSON array riwayat penyakit dahulu
  rpd_lain TEXT DEFAULT '',
  rpk TEXT DEFAULT '[]',             -- JSON array riwayat keluarga
  nutrisi TEXT DEFAULT 'Cukup sayur/buah',
  istirahat TEXT DEFAULT 'Normal',
  alkohol TEXT DEFAULT 'Tidak',
  rokok TEXT DEFAULT 'Tidak',
  kerja_bahaya TEXT DEFAULT 'Tidak',
  jatuh1 TEXT DEFAULT 'Tidak',
  jatuh2 TEXT DEFAULT 'Tidak',
  jatuh3 TEXT DEFAULT 'Tidak',
  skala_nyeri INTEGER DEFAULT 0,
  tgl_masuk TEXT,
  cara_masuk TEXT DEFAULT 'Rawat Jalan',
  td TEXT DEFAULT '',
  nadi TEXT DEFAULT '',
  suhu TEXT DEFAULT '',
  rr TEXT DEFAULT '',
  bb TEXT DEFAULT '',
  tb TEXT DEFAULT '',
  spo2 TEXT DEFAULT '',
  gcs TEXT DEFAULT '',
  keluhan TEXT DEFAULT '',
  diagnosis TEXT DEFAULT '',
  icd10 TEXT DEFAULT '',
  ruang TEXT DEFAULT '',
  dokter TEXT DEFAULT '',
  status TEXT DEFAULT 'Aktif',
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- CPPT Harian (maks 5 hari)
CREATE TABLE IF NOT EXISTS ri_cppt (
  id SERIAL PRIMARY KEY,
  rawat_inap_id INTEGER NOT NULL REFERENCES rawat_inap(id) ON DELETE CASCADE,
  hari INTEGER NOT NULL CHECK (hari BETWEEN 1 AND 5),
  tgl TEXT DEFAULT '',
  jam TEXT DEFAULT '',
  subjektif TEXT DEFAULT '',
  objektif TEXT DEFAULT '',
  assesment TEXT DEFAULT '',
  plan TEXT DEFAULT '',
  petugas TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(rawat_inap_id, hari)
);

-- Resume Medik
CREATE TABLE IF NOT EXISTS ri_resume (
  id SERIAL PRIMARY KEY,
  rawat_inap_id INTEGER NOT NULL UNIQUE REFERENCES rawat_inap(id) ON DELETE CASCADE,
  diag_masuk TEXT DEFAULT '',
  diag_keluar TEXT DEFAULT '',
  anamnese TEXT DEFAULT '',
  pemeriksaan TEXT DEFAULT '',
  pengobatan TEXT DEFAULT '',
  prognosa TEXT DEFAULT 'Bonam',
  dokter TEXT DEFAULT '',
  anjuran TEXT DEFAULT '',
  lainlain TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Ringkasan Masuk & Keluar
CREATE TABLE IF NOT EXISTS ri_ringkasan (
  id SERIAL PRIMARY KEY,
  rawat_inap_id INTEGER NOT NULL UNIQUE REFERENCES rawat_inap(id) ON DELETE CASCADE,
  nama_kk TEXT DEFAULT '',
  pekerjaan TEXT DEFAULT '',
  marital TEXT DEFAULT 'Kawin',
  agama TEXT DEFAULT 'Islam',
  cara_masuk TEXT DEFAULT 'Rawat Jalan',
  tgl_masuk TEXT DEFAULT '',
  diag_masuk TEXT DEFAULT '',
  icd_masuk TEXT DEFAULT '',
  tgl_keluar TEXT DEFAULT '',
  diag_keluar TEXT DEFAULT '',
  icd_keluar TEXT DEFAULT '',
  obat_pulang TEXT DEFAULT '',
  infeksi TEXT DEFAULT 'Tidak',
  penyebab_infeksi TEXT DEFAULT '',
  keadaan_keluar TEXT DEFAULT 'Membaik',
  cara_keluar TEXT DEFAULT 'Diijinkan Pulang',
  rujuk_ke TEXT DEFAULT '',
  dokter TEXT DEFAULT '',
  kie TEXT DEFAULT '',
  tgl_kontrol TEXT DEFAULT '',
  petugas_nama TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- CM 3 (Lembar Diagnosa Dokter)
CREATE TABLE IF NOT EXISTS ri_cm3 (
  id SERIAL PRIMARY KEY,
  rawat_inap_id INTEGER NOT NULL UNIQUE REFERENCES rawat_inap(id) ON DELETE CASCADE,
  diag_banding TEXT DEFAULT '',
  diag_utama TEXT DEFAULT '',
  komplikasi TEXT DEFAULT '',
  diag_tambahan TEXT DEFAULT '',
  pengobatan TEXT DEFAULT '',
  tanggal TEXT DEFAULT '',
  dokter TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Selesai! Tabel berhasil dibuat.
