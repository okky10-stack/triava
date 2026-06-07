"""
satusehat.py — Modul integrasi Satu Sehat untuk Triava ERM
Letakkan file ini di: /home/ubuntu/triage_new/satusehat.py
Kompatibel Python 3.9+
"""

import requests
import time
import logging
from datetime import datetime, date
from typing import Optional, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [SatuSehat] %(message)s")
log = logging.getLogger(__name__)

# ============================================================
# KONFIGURASI — isi dengan credentials sandbox kamu
# ============================================================
CLIENT_ID     = "1kNUDtpe8oWJkq7OhwmpXRJH8mYILOzeEhjW8FYvcHSLucMI"
CLIENT_SECRET = "lu5ALUAZ4corjr1rxADgFmIHNG1bV2RNJVDKvmgWfQSxbC0Rbsad2FjviJTXoNyJ"
ORG_ID        = "8e2e8088-5250-4d12-a412-fa134b0a66ed"

BASE_AUTH = "https://api-satusehat-stg.dto.kemkes.go.id/oauth2/v1"
BASE_FHIR = "https://api-satusehat-stg.dto.kemkes.go.id/fhir-r4/v1"
# ============================================================


class SatuSehat:
    def __init__(self):
        self._token = None
        self._token_expires_at = 0

    # ----------------------------------------------------------
    # AUTH
    # ----------------------------------------------------------
    def _get_token(self):
        if self._token and time.time() < self._token_expires_at - 60:
            return self._token
        resp = requests.post(
            f"{BASE_AUTH}/accesstoken?grant_type=client_credentials",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET},
        )
        resp.raise_for_status()
        data = resp.json()
        self._token = data["access_token"]
        self._token_expires_at = time.time() + int(data.get("expires_in", 3600))
        log.info("Token baru didapat")
        return self._token

    def _headers(self):
        return {"Authorization": f"Bearer {self._get_token()}"}

    def _post(self, path, body):
        resp = requests.post(f"{BASE_FHIR}/{path}", headers=self._headers(), json=body)
        resp.raise_for_status()
        return resp.json()

    def _get(self, path, params=None):
        resp = requests.get(f"{BASE_FHIR}/{path}", headers=self._headers(), params=params)
        resp.raise_for_status()
        return resp.json()

    # ----------------------------------------------------------
    # PATIENT
    # ----------------------------------------------------------
    def get_ihs_number(self, nik):
        """Cari IHS Number pasien berdasarkan NIK. Return string atau None."""
        try:
            data = self._get("Patient", {
                "identifier": f"https://fhir.kemkes.go.id/id/nik|{nik}"
            })
            if data.get("total", 0) > 0:
                resource = data["entry"][0]["resource"]
                ihs = next(
                    (i["value"] for i in resource.get("identifier", [])
                     if "ihs-number" in i.get("system", "")),
                    None
                )
                nama = resource.get("name", [{}])[0].get("text", "-")
                log.info(f"Pasien ditemukan: {nama} | IHS: {ihs}")
                return ihs
            log.warning(f"Pasien NIK {nik} tidak ditemukan di Satu Sehat")
            return None
        except Exception as e:
            log.error(f"get_ihs_number error: {e}")
            return None

    def get_ihs_number_dokter(self, nik_dokter):
        """Cari IHS Number dokter berdasarkan NIK. Return string atau None."""
        try:
            data = self._get("Practitioner", {
                "identifier": f"https://fhir.kemkes.go.id/id/nik|{nik_dokter}"
            })
            if data.get("total", 0) > 0:
                resource = data["entry"][0]["resource"]
                ihs = next(
                    (i["value"] for i in resource.get("identifier", [])
                     if "ihs-number" in i.get("system", "")),
                    None
                )
                log.info(f"Dokter ditemukan | IHS: {ihs}")
                return ihs
            return None
        except Exception as e:
            log.error(f"get_ihs_number_dokter error: {e}")
            return None

    # ----------------------------------------------------------
    # ENCOUNTER — kunjungan rawat jalan
    # ----------------------------------------------------------
    def create_encounter(self, ihs_pasien, ihs_dokter, tgl_kunjungan=None, location_id=None):
        """
        Kirim data kunjungan rawat jalan ke Satu Sehat.
        Return encounter_id string jika berhasil, None jika gagal.
        """
        if tgl_kunjungan is None:
            tgl_kunjungan = date.today()

        tgl_str = tgl_kunjungan.strftime("%Y-%m-%dT07:00:00+07:00")

        body = {
            "resourceType": "Encounter",
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory"
            },
            "subject": {
                "reference": f"Patient/{ihs_pasien}",
                "display": "Pasien"
            },
            "participant": [{
                "type": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                        "code": "ATND",
                        "display": "attender"
                    }]
                }],
                "individual": {
                    "reference": f"Practitioner/{ihs_dokter}",
                    "display": "Dokter"
                }
            }],
            "period": {
                "start": tgl_str,
                "end": tgl_str
            },
            "location": [{
                "location": {
                    "reference": f"Location/{location_id or ORG_ID}",
                    "display": "Puskesmas"
                }
            }],
            "serviceProvider": {
                "reference": f"Organization/{ORG_ID}"
            }
        }

        try:
            result = self._post("Encounter", body)
            enc_id = result.get("id")
            log.info(f"Encounter berhasil dibuat: {enc_id}")
            return enc_id
        except Exception as e:
            log.error(f"create_encounter error: {e}")
            return None

    # ----------------------------------------------------------
    # CONDITION — diagnosis ICD-10
    # ----------------------------------------------------------
    def create_condition(self, ihs_pasien, encounter_id, kode_icd10, nama_diagnosis):
        """
        Kirim diagnosis ICD-10. Harus dipanggil setelah create_encounter.
        Return condition_id string jika berhasil.
        """
        body = {
            "resourceType": "Condition",
            "clinicalStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": "active",
                    "display": "Active"
                }]
            },
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                    "code": "encounter-diagnosis",
                    "display": "Encounter Diagnosis"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://hl7.org/fhir/sid/icd-10",
                    "code": kode_icd10,
                    "display": nama_diagnosis
                }]
            },
            "subject": {"reference": f"Patient/{ihs_pasien}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
            "onsetDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+07:00"),
            "recordedDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+07:00"),
        }

        try:
            result = self._post("Condition", body)
            cond_id = result.get("id")
            log.info(f"Condition berhasil dibuat: {cond_id} ({kode_icd10})")
            return cond_id
        except Exception as e:
            log.error(f"create_condition error: {e}")
            return None

    # ----------------------------------------------------------
    # OBSERVATION — vital sign
    # ----------------------------------------------------------
    def create_observation_vital(self, ihs_pasien, encounter_id,
                                  tekanan_darah_sistolik=None,
                                  tekanan_darah_diastolik=None,
                                  nadi=None, suhu=None,
                                  respirasi=None, saturasi_o2=None):
        """
        Kirim vital sign ke Satu Sehat.
        Return list observation_id yang berhasil dibuat.
        """
        params_list = []
        if tekanan_darah_sistolik:
            params_list.append({"loinc": "8480-6", "display": "Systolic blood pressure",
                                 "value": tekanan_darah_sistolik, "unit": "mm[Hg]"})
        if tekanan_darah_diastolik:
            params_list.append({"loinc": "8462-4", "display": "Diastolic blood pressure",
                                 "value": tekanan_darah_diastolik, "unit": "mm[Hg]"})
        if nadi:
            params_list.append({"loinc": "8867-4", "display": "Heart rate",
                                 "value": nadi, "unit": "/min"})
        if suhu:
            params_list.append({"loinc": "8310-5", "display": "Body temperature",
                                 "value": suhu, "unit": "Cel"})
        if respirasi:
            params_list.append({"loinc": "9279-1", "display": "Respiratory rate",
                                 "value": respirasi, "unit": "/min"})
        if saturasi_o2:
            params_list.append({"loinc": "59408-5", "display": "Oxygen saturation",
                                 "value": saturasi_o2, "unit": "%"})

        ids = []
        for p in params_list:
            body = {
                "resourceType": "Observation",
                "status": "final",
                "category": [{"coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "vital-signs"
                }]}],
                "code": {"coding": [{
                    "system": "http://loinc.org",
                    "code": p["loinc"],
                    "display": p["display"]
                }]},
                "subject": {"reference": f"Patient/{ihs_pasien}"},
                "encounter": {"reference": f"Encounter/{encounter_id}"},
                "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+07:00"),
                "valueQuantity": {
                    "value": p["value"], "unit": p["unit"],
                    "system": "http://unitsofmeasure.org", "code": p["unit"]
                }
            }
            try:
                result = self._post("Observation", body)
                obs_id = result.get("id")
                log.info(f"Observation {p['display']}: {obs_id}")
                ids.append(obs_id)
            except Exception as e:
                log.error(f"create_observation error ({p['display']}): {e}")
        return ids


# ----------------------------------------------------------
# TEST — jalankan: python3 satusehat.py
# ----------------------------------------------------------
if __name__ == "__main__":
    print("\n=== TEST MODUL SATU SEHAT ===\n")
    ss = SatuSehat()

    token = ss._get_token()
    print(f"Token    : {'OK' if token else 'GAGAL'}")

    NIK_TEST = "3174050708880001"
    ihs = ss.get_ihs_number(NIK_TEST)
    print(f"IHS Test : {ihs or 'tidak ditemukan (normal di sandbox)'}")

    print("\n=== SELESAI ===")
    print("Modul siap dipakai di Triava!")
