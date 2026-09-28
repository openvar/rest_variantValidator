import json
import subprocess
import time
import os
from urllib.parse import quote

# -------------------------------------------------------------------------
# Base configuration
# -------------------------------------------------------------------------

BASE_URL = "https://www181.lamp.le.ac.uk/VariantValidator"
THROTTLE_SECONDS = 0
CURL_TIMEOUT = 30  # seconds

# -------------------------------------------------------------------------
# Shared curl runner
# -------------------------------------------------------------------------

def _run_curl(url, variant_label=None, timeout=CURL_TIMEOUT):
    """
    Execute a curl GET request and return parsed JSON.

    Automatically includes Authorization header if
    RESTVV_BEARER_TOKEN is set.

    Prints request + response time.
    """
    time.sleep(THROTTLE_SECONDS)

    bearer_token = os.getenv("RESTVV_BEARER_TOKEN")

    if not bearer_token:
        raise RuntimeError(
            "RESTVV_BEARER_TOKEN environment variable not set. "
            "Please source your token script before running tests."
        )

    cmd = [
        "curl",
        "-s",
        "-X", "GET",
        url,
        "-H", "accept: application/json",
        "-H", "Content-Type: application/json",
        "-H", f"Authorization: Bearer {bearer_token}",
    ]

    start = time.perf_counter()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
        )

    except subprocess.TimeoutExpired:
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(
            f"[RESTVV][TIMEOUT] "
            f"{variant_label or url} → {elapsed_ms:.1f} ms"
        )
        raise

    except subprocess.CalledProcessError as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(
            f"[RESTVV][ERROR] "
            f"{variant_label or url} → {elapsed_ms:.1f} ms"
        )
        print(f"Curl failed: {e.stderr}")
        raise

    elapsed_ms = (time.perf_counter() - start) * 1000

    print(
        f"[RESTVV] "
        f"{variant_label or url} → {elapsed_ms:.1f} ms"
    )

    try:
        return json.loads(result.stdout)

    except json.JSONDecodeError:
        raise ValueError(
            f"Failed to parse JSON response from {url}: "
            f"{result.stdout}"
        )


# -------------------------------------------------------------------------
# Endpoint helper
# -------------------------------------------------------------------------

def run_gene2transcripts(
    gene_query,
    limit_transcripts,
    transcript_set,
    genome_build,
    show_exon_info=False,
):
    """
    Run the legacy REST VV Gene2Transcripts V2 endpoint.

    Endpoint:
        /VariantValidator/tools/gene2transcripts_v2/
            <gene_query>/<limit_transcripts>/
            <transcript_set>/<genome_build>

    Query parameter:
        show_exon_info=true|false
    """

    gene_query = quote(str(gene_query), safe="")
    limit_transcripts = quote(str(limit_transcripts), safe="")
    transcript_set = quote(str(transcript_set), safe="")
    genome_build = quote(str(genome_build), safe="")

    url = (
        f"{BASE_URL}/tools/gene2transcripts_v2/"
        f"{gene_query}/"
        f"{limit_transcripts}/"
        f"{transcript_set}/"
        f"{genome_build}"
        f"?show_exon_info={'true' if show_exon_info else 'false'}"
    )

    return _run_curl(
        url,
        variant_label=(
            f"{gene_query}/{limit_transcripts}/"
            f"{transcript_set}/{genome_build}"
        ),
    )


# -------------------------------------------------------------------------
# Gene2Transcripts test suite
# -------------------------------------------------------------------------

class TestGene2Transcripts:

    def test_COL1A1_raw(self):
        data = run_gene2transcripts(
            "COL1A1",
            "raw",
            "refseq",
            "GRCh38",
            show_exon_info=False,
        )

        entry = data[0]

        assert entry["current_symbol"] == "COL1A1"
        assert entry["hgnc"] == "HGNC:2197"

        refs = [t["reference"] for t in entry["transcripts"]]

        assert "NM_000088.3" in refs
        assert "NM_000088.4" in refs

    def test_COL1A1_all(self):
        data = run_gene2transcripts(
            "COL1A1",
            "all",
            "refseq",
            "GRCh38",
            show_exon_info=False,
        )

        entry = data[0]

        assert entry["current_symbol"] == "COL1A1"

        refs = [t["reference"] for t in entry["transcripts"]]

        assert refs == ["NM_000088.4"]

    def test_BRCA1_mane_select(self):
        data = run_gene2transcripts(
            "BRCA1",
            "mane_select",
            "refseq",
            "GRCh38",
            show_exon_info=False,
        )

        entry = data[0]

        tx = entry["transcripts"][0]

        assert entry["current_symbol"] == "BRCA1"
        assert tx["reference"] == "NM_007294.4"
        assert tx["annotations"]["mane_select"] is True

    def test_LEPRE1_alias_resolution(self):
        data = run_gene2transcripts(
            "LEPRE1",
            "raw",
            "refseq",
            "GRCh38",
            show_exon_info=False,
        )

        entry = data[0]

        assert entry["requested_symbol"] == "LEPRE1"
        assert entry["current_symbol"] == "P3H1"

        refs = [t["reference"] for t in entry["transcripts"]]

        assert "NM_022356.4" in refs

    def test_BRAF_mane(self):
        data = run_gene2transcripts(
            "BRAF",
            "mane",
            "refseq",
            "GRCh38",
            show_exon_info=False,
        )

        entry = data[0]

        refs = [t["reference"] for t in entry["transcripts"]]

        assert "NM_004333.6" in refs
        assert "NM_001374258.1" in refs

    def test_BRAF_mane_expanded(self):
        data = run_gene2transcripts(
            "BRAF",
            "mane",
            "refseq",
            "GRCh38",
            show_exon_info=True,
        )

        entry = data[0]

        refs = [t["reference"] for t in entry["transcripts"]]

        assert "NM_004333.6" in refs
        assert "NM_001374258.1" in refs

    def test_hgnc_id_lookup(self):
        data = run_gene2transcripts(
            "HGNC:2197",
            "mane_select",
            "refseq",
            "GRCh38",
            show_exon_info=False,
        )

        entry = data[0]

        assert entry["current_symbol"] == "COL1A1"
        assert entry["hgnc"] == "HGNC:2197"

        tx = entry["transcripts"][0]

        assert tx["annotations"]["mane_select"] is True
