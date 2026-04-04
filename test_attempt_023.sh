#!/bin/bash
echo "Testing attempt 023: hub penalty mid-tier reduction (2.7 vs 3.0)"
echo "Baseline: 16.84 avg per cog (gamma_v5:v1)"
echo ""

for seed in 42 43 44 45 46; do
  echo "=== Seed $seed ==="
  ANTHROPIC_API_KEY= PYTHONPATH=src/cogamer timeout 600 cogames play -m four_score \
    -p class=cvc.cogamer_policy.CvCPolicy \
    -c 32 -r none --seed $seed 2>&1 | grep -A 2 "Score"
  echo ""
done
