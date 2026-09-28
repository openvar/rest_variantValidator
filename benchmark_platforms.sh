#!/bin/bash

set -u

OUTDIR="benchmark_runs"
MASTER_LOG="$OUTDIR/all_benchmarks.log"

mkdir -p "$OUTDIR"
rm -f "$MASTER_LOG"

run_group() {
    local group="$1"
    shift

    for script in "$@"; do

        if [[ ! -f "$script" ]]; then
            echo "ERROR: benchmark script not found: $script" | tee -a "$MASTER_LOG"
            exit 1
        fi

        echo "============================================================" | tee -a "$MASTER_LOG"
        echo "SCRIPT: $script" | tee -a "$MASTER_LOG"
        echo "GROUP:  $group" | tee -a "$MASTER_LOG"
        echo "============================================================" | tee -a "$MASTER_LOG"

        for run in {1..6}; do

            echo | tee -a "$MASTER_LOG"
            echo "----- RUN $run -----" | tee -a "$MASTER_LOG"

            start=$(date +%s)

            pytest "$script" 2>&1 | tee -a "$MASTER_LOG"

            end=$(date +%s)
            wall=$((end - start))

            if [ "$run" -eq 1 ]; then
                echo "WARM-UP RUN: discard from benchmark" | tee -a "$MASTER_LOG"
            else
                echo "BENCHMARK RUN: $run" | tee -a "$MASTER_LOG"
            fi

            echo "Shell wall time: ${wall}s" | tee -a "$MASTER_LOG"
        done

        echo | tee -a "$MASTER_LOG"
    done
}


# ------------------------------------------------------------
# Gene2Transcripts
# ------------------------------------------------------------

run_group "G2T" \
    swarms/tests/test_curl_local_shaip_g2t_endpoint.py \
    swarms/tests/test_curl_restvv_g2t_endpoint.py \
    # swarms/tests/test_curl_terracipher_g2t_endpoint.py


# ------------------------------------------------------------
# VariantFormatter
#
# REST VV1 equivalent is the historical LOVD endpoint test.
# ------------------------------------------------------------

run_group "VariantFormatter" \
    swarms/tests/test_curl_local_shaip_vfv2_endpoint.py \
    swarms/tests/test_curl_restvv_lovd_endpoint.py \
    # swarms/tests/test_curl_terracipher_vfv2_endpoint.py


# ------------------------------------------------------------
# VariantValidator
# ------------------------------------------------------------

run_group "VariantValidator" \
    swarms/tests/test_curl_local_shaip_vv_endpoint.py \
    swarms/tests/test_curl_restvv_vv_enpoints.py \
    # swarms/tests/test_curl_terracipher_vv_endpoint.py


echo "============================================================" | tee -a "$MASTER_LOG"
echo "ALL BENCHMARKS COMPLETE" | tee -a "$MASTER_LOG"
echo "Results: $MASTER_LOG" | tee -a "$MASTER_LOG"
echo "============================================================" | tee -a "$MASTER_LOG"
