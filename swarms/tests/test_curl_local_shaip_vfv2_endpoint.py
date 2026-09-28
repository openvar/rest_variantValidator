import json
import subprocess
import time

# -------------------------------------------------
# Local SHAIP API Base (Docker)
# -------------------------------------------------
BASE_URL = "http://localhost:8080/shaip/variantformatter-v2"
THROTTLE_SECONDS = 0


def run_curl(
    variant,
    genome_build="GRCh38",
    transcript_model="refseq",
    select_transcripts="None",
    liftover_level="False",
    checkonly=False,
):
    """
    Run curl against the LOCAL SHAIP VariantFormatter V2 API.

    Uses the same test inputs and assertions as the live LAMP
    benchmark, but through the local REST2/SHAIP endpoint.
    """

    time.sleep(THROTTLE_SECONDS)

    payload = [
        {
            "variant_description": variant,
            "genome_build": genome_build,
            "transcript_model": transcript_model,
            "select_transcripts": select_transcripts,
            "liftover_level": liftover_level,
            "checkonly": checkonly,
        }
    ]

    cmd = [
        "curl",
        "--location",
        "--request", "POST",
        BASE_URL,
        "--header", "Content-Type: application/json",
        "--data-raw", json.dumps(payload),
        "-s",
    ]

    start = time.perf_counter()

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )

    end = time.perf_counter()

    elapsed_ms = (end - start) * 1000

    print(f"[LOCAL SHAIP] {variant} → {elapsed_ms:.1f} ms")

    return json.loads(result.stdout)


# -------------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------------

class TestVariantInputs:

    def test_hybrid_syntax_1(self):
        data = run_curl("chr17:50198002C>A")
        entry = data["chr17:50198002C>A"]["NC_000017.11:g.50198002C>A"]
        assert entry["g_hgvs"] == "NC_000017.11:g.50198002C>A"

    def test_hybrid_syntax_2(self):
        data = run_curl("17:50198002C>A")
        entry = data["17:50198002C>A"]["NC_000017.11:g.50198002C>A"]
        assert entry["g_hgvs"] == "NC_000017.11:g.50198002C>A"


class TestTranscriptSelection:

    def test_transcript_selection_raw(self):
        data = run_curl(
            "NC_000005.10:g.140114829del",
            select_transcripts="raw",
        )
        hgvs_t_and_p = (
            data["NC_000005.10:g.140114829del"]
            ["NC_000005.10:g.140114829del"]
            ["hgvs_t_and_p"]
        )
        assert "NM_005859.3" in hgvs_t_and_p
        assert "NM_005859.4" in hgvs_t_and_p
        assert "NM_005859.5" in hgvs_t_and_p

    def test_transcript_selection_all(self):
        data = run_curl(
            "NC_000005.10:g.140114829del",
            select_transcripts="all",
        )
        hgvs_t_and_p = (
            data["NC_000005.10:g.140114829del"]
            ["NC_000005.10:g.140114829del"]
            ["hgvs_t_and_p"]
        )
        assert "NM_005859.5" in hgvs_t_and_p
        assert "NM_005859.3" not in hgvs_t_and_p
        assert "NM_005859.4" not in hgvs_t_and_p

    def test_transcript_selection_mane_select(self):
        data = run_curl(
            "NC_000005.10:g.140114829del",
            select_transcripts="mane_select",
        )
        hgvs_t_and_p = (
            data["NC_000005.10:g.140114829del"]
            ["NC_000005.10:g.140114829del"]
            ["hgvs_t_and_p"]
        )
        assert "NM_005859.5" in hgvs_t_and_p

    def test_transcript_selection_select(self):
        data = run_curl(
            "NC_000005.10:g.140114829del",
            select_transcripts="select",
        )
        hgvs_t_and_p = (
            data["NC_000005.10:g.140114829del"]
            ["NC_000005.10:g.140114829del"]
            ["hgvs_t_and_p"]
        )
        assert "NM_005859.4" in hgvs_t_and_p
        assert "NM_005859.5" in hgvs_t_and_p
        assert "NM_005859.3" not in hgvs_t_and_p

    def test_transcript_selection_nm(self):
        data = run_curl(
            "NC_000005.10:g.140114829del",
            select_transcripts="NM_005859.4",
        )
        hgvs_t_and_p = (
            data["NC_000005.10:g.140114829del"]
            ["NC_000005.10:g.140114829del"]
            ["hgvs_t_and_p"]
        )
        assert "NM_005859.4" in hgvs_t_and_p
        assert "NM_005859.3" not in hgvs_t_and_p
        assert "NM_005859.5" not in hgvs_t_and_p

    def test_transcript_selection_mane(self):
        data = run_curl(
            "NC_000007.14:g.140924703T>C",
            select_transcripts="mane",
        )
        hgvs_t_and_p = (
            data["NC_000007.14:g.140924703T>C"]
            ["NC_000007.14:g.140924703T>C"]
            ["hgvs_t_and_p"]
        )
        assert "NM_004333.6" in hgvs_t_and_p
        assert "NM_001374258.1" in hgvs_t_and_p
        assert "NM_001354609.1" not in hgvs_t_and_p


class TestVariantAutoCases:

    def test_variant1_bad_build(self):
        v = "NC_000019.10:g.50378563_50378564insTAC"
        data = run_curl(v, genome_build="GRCh37")
        entry = data[v][v]
        assert (
            "chromosome ID NC_000019.10 is not associated"
            in entry["genomic_variant_error"]
        )

    def test_variant2_mismatched_reference(self):
        v = "11-5248232-A-T"
        data = run_curl(v, genome_build="GRCh37")
        entry = data[v][v]
        assert (
            "does not agree with reference sequence"
            in entry["genomic_variant_error"]
        )

    def test_variant3_ref_mismatch(self):
        v = "NC_000012.11:g.122064777A>C"
        data = run_curl(v, genome_build="GRCh37")
        entry = data[v][v]
        assert (
            "does not agree with reference sequence"
            in entry["genomic_variant_error"]
        )

    def test_variant4_synonymous(self):
        v = "NC_000002.11:g.73613030C>T"
        data = run_curl(
            v,
            genome_build="GRCh37",
            select_transcripts="all",
        )
        entry = data[v][v]
        assert entry["genomic_variant_error"] is None
        assert "NM_015120.4" in entry["hgvs_t_and_p"]

    def test_variant5_x_chromosome(self):
        v = "NC_000023.10:g.33229673A>T"
        data = run_curl(
            v,
            genome_build="GRCh37",
            select_transcripts="raw",
        )
        entry = data[v][v]
        assert entry["genomic_variant_error"] is None
        assert "NM_000109.3" in entry["hgvs_t_and_p"]

    def test_variant6_intergenic(self):
        v = "NC_000017.10:g.48279242G>T"
        data = run_curl(
            v,
            genome_build="GRCh37",
            select_transcripts="all",
        )
        entry = data[v][v]

        assert entry["hgvs_t_and_p"]["intergenic"]["alt_genomic_loci"] is None

    def test_variant7_identity(self):
        v = "NC_000017.10:g.48261457_48261463TTATGTT="
        data = run_curl(
            v,
            genome_build="GRCh37",
            select_transcripts="raw",
        )
        entry = data[v][v]
        assert "NM_000088.3" in entry["hgvs_t_and_p"]

    def test_variant8_missense(self):
        v = "NC_000017.10:g.48275363C>A"
        data = run_curl(
            v,
            genome_build="GRCh37",
            select_transcripts="raw",
        )
        entry = data[v][v]
        assert "NM_000088.3" in entry["hgvs_t_and_p"]

    def test_variant9_roundtrip_consistency(self):
        v = "11-5248232-T-A"
        data = run_curl(v, genome_build="GRCh37")
        entry = data[v][v]
        assert entry["p_vcf"] == v
        assert entry["genomic_variant_error"] is None

    def test_variant10_tx_pipe(self):
        v = "NC_000017.10:g.48275363C>A"
        data = run_curl(
            v,
            genome_build="GRCh37",
            select_transcripts="NM_000088.3|NM_000088.4",
        )
        entry = data[v][v]
        assert "NM_000088.3" in entry["hgvs_t_and_p"]
        assert "NM_000088.4" in entry["hgvs_t_and_p"]

    def test_variant10_tx_array(self):
        v = "NC_000017.10:g.48275363C>A"
        data = run_curl(
            v,
            genome_build="GRCh37",
            select_transcripts=[
                "NM_000088.3",
                "NM_000088.4",
            ],
        )
        entry = data[v][v]
        assert "NM_000088.3" in entry["hgvs_t_and_p"]
        assert "NM_000088.4" in entry["hgvs_t_and_p"]
