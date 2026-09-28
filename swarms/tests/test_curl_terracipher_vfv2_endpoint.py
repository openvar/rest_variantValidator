import json
import os
import subprocess
import time


# -------------------------------------------------
# TerraCipher SHAIP API
# -------------------------------------------------

BASE_URL = "https://shaipup.com/market/shaip"

VF_URL = (
    f"{BASE_URL}/variantformatter-v2"
    "?owner=VariantValidator&shaip=rest-variantvalidator2"
)

THROTTLE_SECONDS = 0
CURL_TIMEOUT = 30

_timings = []


# -------------------------------------------------
# Helper
# -------------------------------------------------

def _normalise_select_transcripts(select_transcripts):
    """
    Convert the local SHAIP representation of
    select_transcripts into the TerraCipher V2 schema.

    Local:
        "None"
        "all"
        "raw"
        "mane"
        "mane_select"
        "select"
        "NM_005859.4"
        "NM_000088.3|NM_000088.4"
        ["NM_000088.3", "NM_000088.4"]

    TerraCipher:
        array of strings
    """

    # The local default is the literal string "None".
    # TC does not define "None"; its schema/examples use
    # "all" for an unrestricted transcript selection.
    if select_transcripts == "None":
        return ["all"]

    if isinstance(select_transcripts, str):

        # Local SHAIP also permits the pipe-delimited
        # transcript form.
        if "|" in select_transcripts:
            return select_transcripts.split("|")

        return [select_transcripts]

    # Already an array: preserve it.
    return list(select_transcripts)


def run_curl(
    variant,
    genome_build="GRCh38",
    transcript_model="refseq",
    select_transcripts="None",
    liftover_level="False",
    checkonly=False,
):
    """
    Run curl against the TerraCipher SHAIP VariantFormatter V2 API.

    The test calls are deliberately kept identical to the working
    local SHAIP benchmark. Only the request structure is translated
    to the TerraCipher schema.
    """

    time.sleep(THROTTLE_SECONDS)

    bearer_token = os.getenv("SHAIP_BEARER_TOKEN")

    if not bearer_token:
        raise RuntimeError(
            "SHAIP_BEARER_TOKEN environment variable not set. "
            "Please source set_token.sh first."
        )

    cookie_file = "/tmp/shaip_cookies"

    if not os.path.exists(cookie_file):
        raise RuntimeError(
            f"{cookie_file} not found. "
            "Please source set_token.sh first."
        )

    payload = [
        {
            "variant_description": [variant],
            "genome_build": genome_build,
            "transcript_model": transcript_model,
            "select_transcripts": _normalise_select_transcripts(
                select_transcripts
            ),
            "liftover_level": liftover_level,
            "checkonly": checkonly,
        }
    ]

    cmd = [
        "curl",
        "--location",
        "--request", "POST",
        VF_URL,
        "--header", f"Authorization: Bearer {bearer_token}",
        "--header", "Content-Type: application/json",
        "--cookie", cookie_file,
        "--data-raw", json.dumps(payload),
        "--silent",
        "--show-error",
        "--max-time", str(CURL_TIMEOUT),
        "--write-out", "\n__HTTP_STATUS__:%{http_code}",
    ]

    start = time.perf_counter()

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
        timeout=CURL_TIMEOUT + 5,
    )

    elapsed_ms = (time.perf_counter() - start) * 1000

    stdout = result.stdout

    if "\n__HTTP_STATUS__:" not in stdout:
        raise RuntimeError(
            "No HTTP status returned by TerraCipher.\n"
            f"Response:\n{stdout}"
        )

    body, status_text = stdout.rsplit(
        "\n__HTTP_STATUS__:", 1
    )

    status = int(status_text.strip())

    print(
        f"[TC SHAIP] {variant} → "
        f"{elapsed_ms:.1f} ms "
        f"(HTTP {status})"
    )

    if status != 200:
        raise RuntimeError(
            f"TerraCipher returned HTTP {status}\n"
            f"Response:\n{body}"
        )

    _timings.append(elapsed_ms)

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"TerraCipher returned non-JSON response:\n{body}"
        )


# -------------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------------

class TestVariantInputs:

    def test_hybrid_syntax_1(self):
        data = run_curl("chr17:50198002C>A")
        entry = (
            data["chr17:50198002C>A"]
            ["NC_000017.11:g.50198002C>A"]
        )
        assert entry["g_hgvs"] == "NC_000017.11:g.50198002C>A"

    def test_hybrid_syntax_2(self):
        data = run_curl("17:50198002C>A")
        entry = (
            data["17:50198002C>A"]
            ["NC_000017.11:g.50198002C>A"]
        )
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

        assert (
            entry["hgvs_t_and_p"]
            ["intergenic"]
            ["alt_genomic_loci"]
            is None
        )

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


# -------------------------------------------------
# Run benchmark
# -------------------------------------------------

if __name__ == "__main__":

    tests = [
        TestVariantInputs().test_hybrid_syntax_1,
        TestVariantInputs().test_hybrid_syntax_2,
        TestTranscriptSelection().test_transcript_selection_raw,
        TestTranscriptSelection().test_transcript_selection_all,
        TestTranscriptSelection().test_transcript_selection_mane_select,
        TestTranscriptSelection().test_transcript_selection_select,
        TestTranscriptSelection().test_transcript_selection_nm,
        TestTranscriptSelection().test_transcript_selection_mane,
        TestVariantAutoCases().test_variant1_bad_build,
        TestVariantAutoCases().test_variant2_mismatched_reference,
        TestVariantAutoCases().test_variant3_ref_mismatch,
        TestVariantAutoCases().test_variant4_synonymous,
        TestVariantAutoCases().test_variant5_x_chromosome,
        TestVariantAutoCases().test_variant6_intergenic,
        TestVariantAutoCases().test_variant7_identity,
        TestVariantAutoCases().test_variant8_missense,
        TestVariantAutoCases().test_variant9_roundtrip_consistency,
        TestVariantAutoCases().test_variant10_tx_pipe,
        TestVariantAutoCases().test_variant10_tx_array,
    ]

    print(
        f"Benchmarking {len(tests)} "
        "TerraCipher SHAIP VariantFormatter cases"
    )
    print(f"Endpoint: {VF_URL}")
    print()

    passed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as exc:
            print(f"FAILED: {test.__name__}")
            print(f"       {exc}")
            print()

    print()
    print("=" * 60)
    print(f"Passed: {passed}/{len(tests)}")

    if _timings:
        print(f"Mean:   {sum(_timings) / len(_timings):.1f} ms")
        print(f"Min:    {min(_timings):.1f} ms")
        print(f"Max:    {max(_timings):.1f} ms")

    if passed != len(tests):
        raise SystemExit(1)
