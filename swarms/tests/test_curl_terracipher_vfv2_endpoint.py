import json
import subprocess
import time
import os

# -----------------------------
# API Base and Throttling
# -----------------------------
BASE_URL = "https://shaipup.com/market/shaip?owner=uominnovationfactory&shaip=variantvalidatorapi"
THROTTLE_SECONDS = 0  # ~3 requests/sec (API allows 4/sec)

# Tokens from environment
BEARER_TOKEN = os.getenv("SHAIP_BEARER_TOKEN")
COOKIE_TOKEN = os.getenv("SHAIP_COOKIE_TOKEN")

if not BEARER_TOKEN:
    raise RuntimeError("Please set SHAIP_BEARER_TOKEN in your environment")
if not COOKIE_TOKEN:
    raise RuntimeError("Please set SHAIP_COOKIE_TOKEN in your environment")


def run_curl(
    variant,
    genome_build="GRCh38",
    transcript_model="refseq",
    select_transcripts="None",
    liftover="False",
    checkonly="False",
):
    """
    Run curl against the TerraCipher VariantValidator API and return parsed JSON.
    Uses POST with JSON body.
    """
    time.sleep(THROTTLE_SECONDS)  # avoid rate limiting

    # Build JSON payload
    payload = [
        {
            "select_transcripts": [select_transcripts],
            "liftover": liftover.lower() == "true",
            "checkonly": checkonly.lower() == "true",
            "transcript_model": transcript_model,
            "genome_build": genome_build,
            "variant_description": [variant],
        }
    ]

    cmd = [
        "curl",
        "--location",
        "--request", "POST", BASE_URL,
        "--header", f"Authorization: Bearer {BEARER_TOKEN}",
        "--header", "Content-Type: application/json",
        "--header", f"Cookie: {COOKIE_TOKEN}",
        "--data-raw", json.dumps(payload),
        "-s",  # silent
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)

# -----------------------------
# Variant Inputs
# -----------------------------
class TestVariantInputs:
    def test_hybrid_syntax_1(self):
        data = run_curl("chr17:50198002C>A")
        entry = data["chr17:50198002C>A"]["NC_000017.11:g.50198002C>A"]
        assert entry["g_hgvs"] == "NC_000017.11:g.50198002C>A"

    def test_hybrid_syntax_2(self):
        data = run_curl("17:50198002C>A")
        entry = data["17:50198002C>A"]["NC_000017.11:g.50198002C>A"]
        assert entry["g_hgvs"] == "NC_000017.11:g.50198002C>A"


# -----------------------------
# Transcript Selection
# -----------------------------
class TestTranscriptSelection:
    def test_transcript_selection_raw(self):
        data = run_curl("NC_000005.10:g.140114829del", select_transcripts="raw")
        hgvs_t_and_p = data["NC_000005.10:g.140114829del"]["NC_000005.10:g.140114829del"]["hgvs_t_and_p"]
        assert "NM_005859.3" in hgvs_t_and_p
        assert "NM_005859.4" in hgvs_t_and_p
        assert "NM_005859.5" in hgvs_t_and_p

    def test_transcript_selection_all(self):
        data = run_curl("NC_000005.10:g.140114829del", select_transcripts="all")
        hgvs_t_and_p = data["NC_000005.10:g.140114829del"]["NC_000005.10:g.140114829del"]["hgvs_t_and_p"]
        assert "NM_005859.5" in hgvs_t_and_p
        assert "NM_005859.3" not in hgvs_t_and_p
        assert "NM_005859.4" not in hgvs_t_and_p

    def test_transcript_selection_mane_select(self):
        data = run_curl("NC_000005.10:g.140114829del", select_transcripts="mane_select")
        hgvs_t_and_p = data["NC_000005.10:g.140114829del"]["NC_000005.10:g.140114829del"]["hgvs_t_and_p"]
        assert "NM_005859.5" in hgvs_t_and_p

    def test_transcript_selection_select(self):
        data = run_curl("NC_000005.10:g.140114829del", select_transcripts="select")
        hgvs_t_and_p = data["NC_000005.10:g.140114829del"]["NC_000005.10:g.140114829del"]["hgvs_t_and_p"]
        assert "NM_005859.4" in hgvs_t_and_p
        assert "NM_005859.5" in hgvs_t_and_p
        assert "NM_005859.3" not in hgvs_t_and_p

    def test_transcript_selection_nm(self):
        data = run_curl("NC_000005.10:g.140114829del", select_transcripts="NM_005859.4")
        hgvs_t_and_p = data["NC_000005.10:g.140114829del"]["NC_000005.10:g.140114829del"]["hgvs_t_and_p"]
        assert "NM_005859.4" in hgvs_t_and_p
        assert "NM_005859.3" not in hgvs_t_and_p
        assert "NM_005859.5" not in hgvs_t_and_p

    def test_transcript_selection_mane(self):
        data = run_curl("NC_000007.14:g.140924703T>C", select_transcripts="mane")
        hgvs_t_and_p = data["NC_000007.14:g.140924703T>C"]["NC_000007.14:g.140924703T>C"]["hgvs_t_and_p"]
        assert "NM_004333.6" in hgvs_t_and_p
        assert "NM_001374258.1" in hgvs_t_and_p
        assert "NM_001354609.1" not in hgvs_t_and_p


# -----------------------------
# Auto/Edge Case Variants
# -----------------------------
class TestVariantAutoCases:
    def test_variant1_bad_build(self):
        v = "NC_000019.10:g.50378563_50378564insTAC"
        data = run_curl(v, genome_build="GRCh37")
        entry = data[v][v]
        assert "chromosome ID NC_000019.10 is not associated" in entry["genomic_variant_error"]

    def test_variant2_mismatched_reference(self):
        v = "11-5248232-A-T"
        data = run_curl(v, genome_build="GRCh37")
        entry = data[v][v]
        assert "does not agree with reference sequence" in entry["genomic_variant_error"]

    def test_variant3_ref_mismatch(self):
        v = "NC_000012.11:g.122064777A>C"
        data = run_curl(v, genome_build="GRCh37")
        entry = data[v][v]
        assert "does not agree with reference sequence" in entry["genomic_variant_error"]

    def test_variant4_synonymous(self):
        v = "NC_000002.11:g.73613030C>T"
        data = run_curl(v, genome_build="GRCh37", select_transcripts="all")
        entry = data[v][v]
        assert entry["genomic_variant_error"] is None
        assert "NM_015120.4" in entry["hgvs_t_and_p"]

    def test_variant5_x_chromosome(self):
        v = "NC_000023.10:g.33229673A>T"
        data = run_curl(v, genome_build="GRCh37", select_transcripts="raw")
        entry = data[v][v]
        assert entry["genomic_variant_error"] is None
        assert "NM_000109.3" in entry["hgvs_t_and_p"]

    def test_variant6_intergenic(self):
        v = "NC_000017.10:g.48279242G>T"
        data = run_curl(v, genome_build="GRCh37", select_transcripts="all")
        entry = data[v][v]
        assert entry["hgvs_t_and_p"] == {"intergenic": {"alt_genomic_loci": None}}

    def test_variant7_identity(self):
        v = "NC_000017.10:g.48261457_48261463TTATGTT="
        data = run_curl(v, genome_build="GRCh37", select_transcripts="raw")
        entry = data[v][v]
        assert "NM_000088.3" in entry["hgvs_t_and_p"]

    def test_variant8_missense(self):
        v = "NC_000017.10:g.48275363C>A"
        data = run_curl(v, genome_build="GRCh37", select_transcripts="raw")
        entry = data[v][v]
        assert "NM_000088.3" in entry["hgvs_t_and_p"]

    def test_variant9_roundtrip_consistency(self):
        v = "11-5248232-T-A"
        data = run_curl(v, genome_build="GRCh37")
        entry = data[v][v]
        assert entry["p_vcf"] == v
        assert entry["genomic_variant_error"] is None
