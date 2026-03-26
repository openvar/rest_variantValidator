import json
import subprocess
import time

# -------------------------------------------------------------------------
# Base configuration for LOCAL testing
# -------------------------------------------------------------------------

# Use whichever port you mapped:
# docker run -p 8080:8080 vv-local
BASE_URL = "http://localhost:8080"
THROTTLE_SECONDS = 0
CURL_TIMEOUT = 30  # seconds


# -------------------------------------------------------------------------
# Shared curl POST runner (LOCAL, no auth)
# -------------------------------------------------------------------------

def _run_local_post(url, payload, label=None, timeout=CURL_TIMEOUT):
    """
    Execute a curl POST request against LOCAL VariantValidator SHAIP server.
    No bearer token. No cookies.
    Returns parsed JSON response.
    """
    time.sleep(THROTTLE_SECONDS)

    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", "Content-Type: application/json",
        "--data-raw", json.dumps(payload)
    ]

    start = time.perf_counter()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout
        )
    except subprocess.TimeoutExpired:
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"[LOCAL TIMEOUT] {label or url} → {elapsed_ms:.1f} ms")
        raise
    except subprocess.CalledProcessError as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"[LOCAL ERROR] {label or url} → {elapsed_ms:.1f} ms")
        print(f"Curl failed: {e.stderr}")
        raise

    elapsed_ms = (time.perf_counter() - start) * 1000
    print(f"[LOCAL] {label or url} → {elapsed_ms:.1f} ms")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise ValueError(f"Failed to parse JSON response from {url}: {result.stdout}")


# -------------------------------------------------------------------------
# Wrapper for local VariantValidator (refseq)
# -------------------------------------------------------------------------

def run_variantvalidator_local(
    variant,
    genome_build,
    select_transcripts="all",
):
    """
    Local POST equivalent of /variantvalidator/<build>/<variant>/<select_transcripts>
    """
    url = f"{BASE_URL}/VariantValidator"

    payload = {
        "variant_description": variant,
        "genome_build": genome_build,
        "select_transcripts": select_transcripts
    }

    return _run_local_post(url, payload, label=variant)


# -------------------------------------------------------------------------
# Wrapper for local VariantValidator (ensembl)
# -------------------------------------------------------------------------

def run_variantvalidator_ensembl_local(
    variant,
    genome_build,
    select_transcripts="all",
):
    url = f"{BASE_URL}/VariantValidator_ensembl"

    payload = {
        "variant_description": variant,
        "genome_build": genome_build,
        "select_transcripts": select_transcripts
    }

    return _run_local_post(url, payload, label=variant)


# -------------------------------------------------------------------------
# Helper for extracting a primary entry
# -------------------------------------------------------------------------

def _get_primary_entry_local(data):
    keys = [k for k in data if k not in ("flag", "metadata")]
    if not keys:
        raise ValueError("No variant data returned from local API.")
    key = keys[0]
    return key, data[key]


# -------------------------------------------------------------------------
# Local RefSeq VariantValidator test suite
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

    def test_validated_NM_variants(self):
        for variant, gene, chrom in self.variants_to_test:
            data = run_variantvalidator_local(
                variant,
                "GRCh38",
                select_transcripts="all"
            )
            key, entry = _get_primary_entry_local(data)
            assert entry["gene_symbol"] == gene
            assert entry["hgvs_transcript_variant"] == variant
            assert entry["annotations"]["chromosome"] == chrom
            assert "refseqgene_context_intronic_sequence" in entry


# -------------------------------------------------------------------------
# Local Ensembl VariantValidator test suite
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

    def test_validated_ENST_variants(self):
        for variant, gene, chrom in self.variants_to_test:
            data = run_variantvalidator_ensembl_local(
                variant,
                "GRCh38",
                select_transcripts="all"
            )
            key, entry = _get_primary_entry_local(data)
            assert entry["gene_symbol"] == gene
            assert entry["hgvs_transcript_variant"] == variant
            assert entry["annotations"]["chromosome"] == chrom