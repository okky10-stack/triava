from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def analyze_keluhan(keluhan, kategori="Umum"):

    kategori = (kategori or "Umum").lower()

    # ======================
    # BASE PROMPT
    # ======================
    base_prompt = f"""
Keluhan utama pasien:
{keluhan}

Anda adalah asisten triase UGD.

Tugas:
Buat daftar poin anamnesis singkat yang perlu digali dokter.

Aturan:
- Maksimal 5-7 poin
- Setiap poin maksimal 5-8 kata
- Jangan buat kalimat panjang
- Jangan beri diagnosis
- Fokus pada red flag
- Sesuaikan dengan jenis keluhan
"""

    # ======================
    # KATEGORI KHUSUS
    # ======================
    if "hamil" in kategori:

        extra = """
Pasien adalah IBU HAMIL.

WAJIB fokus pada:
- usia kehamilan
- jumlah perdarahan
- nyeri perut / kontraksi
- gerakan janin
- riwayat ANC
- riwayat komplikasi sebelumnya
"""

    elif "postpartum" in kategori:

        extra = """
Pasien adalah POSTPARTUM.

Fokus pada:
- jumlah perdarahan
- nyeri perut
- demam
- bau lokia
- tekanan darah / pusing
"""

    elif "bayi" in kategori or "anak" in kategori:

        extra = """
Pasien adalah BAYI / ANAK.

WAJIB fokus pada:
- mau minum / tidak
- kesadaran
- kejang
- demam
- sesak napas
- aktivitas / rewel
"""

    else:
        extra = ""

    # ======================
    # FINAL PROMPT
    # ======================
    prompt = base_prompt + "\n" + extra

    # ======================
    # OPENAI CALL
    # ======================
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": "Anda adalah asisten triase medis yang fokus pada red flag dan pertanyaan singkat."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content
