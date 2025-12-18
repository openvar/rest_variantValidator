import json
import subprocess
import time
import os

# -------------------------------------------------------------------------
# Base configuration
# -------------------------------------------------------------------------

BASE_URL = "https://www183.lamp.le.ac.uk/VariantValidator"
THROTTLE_SECONDS = 0
CURL_TIMEOUT = 30  # seconds

# -------------------------------------------------------------------------
# Shared curl runner
# -------------------------------------------------------------------------

def _run_curl(url, timeout=CURL_TIMEOUT):
    """
    Execute a curl GET request and return parsed JSON.
    Automatically includes Authorization header if RESTVV_BEARER_TOKEN is set.
    """
    time.sleep(THROTTLE_SECONDS)

    bearer_token = os.getenv("RESTVV_BEARER_TOKEN")
    if not bearer_token:
        raise RuntimeError(
            "RESTVV_BEARER_TOKEN environment variable not set. "
            "Please export your VariantValidator bearer token before running tests."
        )

    cmd = [
        "curl", "-s", "-X", "GET", url,
        "-H", "accept: application/json",
        "-H", "Content-Type: application/json",
        f"-H", f"Authorization: Bearer {bearer_token}"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout  # <-- ensures curl doesn't hang indefinitely
        )
    except subprocess.TimeoutExpired:
        # Kill curl if somehow still running
        print(f"Curl request to {url} timed out after {timeout} seconds!")
        raise
    except subprocess.CalledProcessError as e:
        print(f"Curl failed: {e.stderr}")
        raise

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise ValueError(f"Failed to parse JSON response from {url}: {result.stdout}")

# -------------------------------------------------------------------------
# Endpoint helpers
# -------------------------------------------------------------------------

def run_variantvalidator(variant, genome_build, select_transcripts="all", endpoint="variantvalidator"):
    url = (
        f"{BASE_URL}/{endpoint}/"
        f"{genome_build}/{variant}/{select_transcripts}"
        f"?content-type=application%2Fjson"
    )
    return _run_curl(url)

# -------------------------------------------------------------------------
# RefSeq VariantValidator test suite (validated variants)
# -------------------------------------------------------------------------

class TestVariantValidatorRefSeqValidated:

    variants_to_test = [
        ("NM_000088.3:c.589G>T", "COL1A1", "17"),
        ("NM_007294.3:c.68_69del", "BRCA1", "17"),
        ("NM_000546.6:c.215C>G", "TP53", "17"),
        ("NM_000492.4:c.1521_1523del", "CFTR", "7"),
        ("NM_000518.5:c.20A>T", "HBB", "11"),
        ("NM_000132.4:c.1835G>A", "F8", "X"),
        ("NM_000133.4:c.1001T>G", "F9", "X"),
        ("NM_004006.2:c.9253dup", "DMD", "X"),
        ("NM_000527.5:c.1775G>A", "LDLR", "19"),
        ("NM_000277.3:c.1222C>T", "PAH", "12")
    ]

    def _get_primary_entry(self, data):
        keys = [k for k in data if k not in ("flag", "metadata")]
        if not keys:
            raise ValueError("No variant data returned from server. "
                             "Check that your bearer token is valid.")
        key = keys[0]
        return key, data[key]

    def test_validated_NM_variants(self):
        for variant, gene, chrom in self.variants_to_test:
            data = run_variantvalidator(variant, "GRCh38", select_transcripts="all")
            key, entry = self._get_primary_entry(data)
            assert entry["gene_symbol"] == gene, f"{variant}: expected {gene}, got {entry.get('gene_symbol')}"
            assert entry["hgvs_transcript_variant"] == variant, f"{variant}: HGVS mismatch"
            assert entry["annotations"]["chromosome"] == chrom, f"{variant}: chromosome mismatch"
            assert "refseqgene_context_intronic_sequence" in entry

# -------------------------------------------------------------------------
# Ensembl VariantValidator test suite (validated variants)
# -------------------------------------------------------------------------

class TestVariantValidatorEnsemblValidated:

    variants_to_test = [
        ("ENST00000269305.4:c.589G>T", "TP53", "17"),
        ("ENST00000357654.9:c.68_69del", "BRCA1", "17"),
        ("ENST00000269305.4:c.215C>G", "TP53", "17"),
        ("ENST00000003084.11:c.1521_1523del", "CFTR", "7"),
        ("ENST00000335295.4:c.20A>T", "HBB", "11"),
        ("ENST00000360256.9:c.1835G>A", "F8", "X"),
        ("ENST00000218099.7:c.1001T>G", "F9", "X"),
        ("ENST00000357033.9:c.9253dup", "DMD", "X"),
        ("ENST00000558518.6:c.1775G>A", "LDLR", "19"),
        ("ENST00000553106.6:c.1222C>T", "PAH", "12")
    ]

    def _get_primary_entry(self, data):
        keys = [k for k in data if k not in ("flag", "metadata")]
        if not keys:
            raise ValueError("No variant data returned from server. "
                             "Check that your bearer token is valid.")
        key = keys[0]
        return key, data[key]

    def test_validated_ENST_variants(self):
        for variant, gene, chrom in self.variants_to_test:
            data = run_variantvalidator(
                variant,
                "GRCh38",
                select_transcripts="all",
                endpoint="variantvalidator_ensembl"
            )
            key, entry = self._get_primary_entry(data)
            assert entry["gene_symbol"] == gene, f"{variant}: expected {gene}, got {entry.get('gene_symbol')}"
            assert entry["hgvs_transcript_variant"] == variant, f"{variant}: HGVS mismatch"
            assert entry["annotations"]["chromosome"] == chrom, f"{variant}: chromosome mismatch"
