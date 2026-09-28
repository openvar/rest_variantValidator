import json
import subprocess
import time


# -------------------------------------------------
# Local SHAIP API
# -------------------------------------------------

BASE_URL = "http://localhost:8080/shaip/gene2transcripts-v2"
THROTTLE_SECONDS = 0

_timings = []


# -------------------------------------------------
# Helper
# -------------------------------------------------

def run_curl(payload):
    time.sleep(THROTTLE_SECONDS)

    cmd = [
        "curl",
        "--location",
        "--request", "POST",
        BASE_URL,
        "--header", "Content-Type: application/json",
        "--data-raw", json.dumps([payload]),
        "--silent",
        "--show-error",
        "--fail-with-body",
    ]

    start = time.perf_counter()

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )

    elapsed_ms = (time.perf_counter() - start) * 1000
    _timings.append(elapsed_ms)

    print(
        f"[LOCAL SHAIP] "
        f"{payload['gene_query']} "
        f"({payload['limit_transcripts']}, "
        f"exons={payload['show_exon_info']}) "
        f"→ {elapsed_ms:.1f} ms"
    )

    return json.loads(result.stdout)


# -------------------------------------------------
# Tests
# -------------------------------------------------

def test_COL1A1_raw():
    data = run_curl({
        "gene_query": "COL1A1",
        "genome_build": "GRCh38",
        "transcript_set": "refseq",
        "limit_transcripts": "raw",
        "show_exon_info": False,
    })

    entry = data[0]

    assert entry["current_symbol"] == "COL1A1"
    assert entry["hgnc"] == "HGNC:2197"
    assert len(entry["transcripts"]) >= 3

    refs = [t["reference"] for t in entry["transcripts"]]

    assert "NM_000088.3" in refs
    assert "NM_000088.4" in refs


def test_COL1A1_all():
    data = run_curl({
        "gene_query": "COL1A1",
        "genome_build": "GRCh38",
        "transcript_set": "refseq",
        "limit_transcripts": "all",
        "show_exon_info": False,
    })

    entry = data[0]

    assert entry["current_symbol"] == "COL1A1"
    assert entry["hgnc"] == "HGNC:2197"
    assert len(entry["transcripts"]) == 1

    refs = [t["reference"] for t in entry["transcripts"]]

    assert "NM_000088.4" in refs


def test_BRCA1_mane_select():
    data = run_curl({
        "gene_query": "BRCA1",
        "genome_build": "GRCh38",
        "transcript_set": "refseq",
        "limit_transcripts": "mane_select",
        "show_exon_info": False,
    })

    entry = data[0]

    assert entry["current_symbol"] == "BRCA1"
    assert entry["hgnc"] == "HGNC:1100"
    assert len(entry["transcripts"]) == 1

    tx = entry["transcripts"][0]

    assert tx["reference"] == "NM_007294.4"
    assert tx["annotations"]["mane_select"] is True


def test_LEPRE1_alias_resolution():
    data = run_curl({
        "gene_query": "LEPRE1",
        "genome_build": "GRCh38",
        "transcript_set": "refseq",
        "limit_transcripts": "raw",
        "show_exon_info": False,
    })

    entry = data[0]

    assert entry["requested_symbol"] == "LEPRE1"
    assert entry["current_symbol"] == "P3H1"
    assert entry["hgnc"] == "HGNC:19316"
    assert len(entry["transcripts"]) >= 5

    refs = [t["reference"] for t in entry["transcripts"]]

    assert "NM_022356.4" in refs


def test_BRAF_mane():
    data = run_curl({
        "gene_query": "BRAF",
        "genome_build": "GRCh38",
        "transcript_set": "refseq",
        "limit_transcripts": "mane",
        "show_exon_info": False,
    })

    entry = data[0]

    assert entry["current_symbol"] == "BRAF"
    assert entry["hgnc"] == "HGNC:1097"
    assert len(entry["transcripts"]) == 2

    refs = [t["reference"] for t in entry["transcripts"]]

    assert "NM_004333.6" in refs
    assert "NM_001374258.1" in refs


def test_BRAF_mane_expanded():
    data = run_curl({
        "gene_query": "BRAF",
        "genome_build": "GRCh38",
        "transcript_set": "refseq",
        "limit_transcripts": "mane",
        "show_exon_info": True,
    })

    entry = data[0]

    refs = [t["reference"] for t in entry["transcripts"]]

    assert "NM_004333.6" in refs
    assert "NM_001374258.1" in refs


def test_hgnc_id_lookup():
    data = run_curl({
        "gene_query": "HGNC:2197",
        "genome_build": "GRCh38",
        "transcript_set": "refseq",
        "limit_transcripts": "mane_select",
        "show_exon_info": False,
    })

    entry = data[0]

    assert entry["current_symbol"] == "COL1A1"
    assert entry["hgnc"] == "HGNC:2197"
    assert len(entry["transcripts"]) == 1

    tx = entry["transcripts"][0]

    assert tx["annotations"]["mane_select"] is True


# -------------------------------------------------
# Run benchmark
# -------------------------------------------------

if __name__ == "__main__":

    tests = [
        test_COL1A1_raw,
        test_COL1A1_all,
        test_BRCA1_mane_select,
        test_LEPRE1_alias_resolution,
        test_BRAF_mane,
        test_BRAF_mane_expanded,
        test_hgnc_id_lookup,
    ]

    print(f"Benchmarking {len(tests)} local SHAIP Gene2Transcripts cases")
    print(f"Endpoint: {BASE_URL}")
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
