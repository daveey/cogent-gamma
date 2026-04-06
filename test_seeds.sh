#!/bin/bash
# Test policy across seeds 42-46
cd /home/cogent/repo
SEEDS=(42 43 44 45 46)
SCORES=()

for seed in "${SEEDS[@]}"; do
    echo "=== Running seed $seed ==="
    ANTHROPIC_API_KEY= PYTHONPATH=src/cogamer uv run cogames play \
        -m machina_1 \
        -p class=cvc.cogamer_policy.CvCPolicy \
        -c 8 -r none --seed $seed 2>&1 | tee /tmp/seed_${seed}.log

    # Extract score from log
    SCORE=$(grep -oP 'per cog:\s+\K[\d.]+' /tmp/seed_${seed}.log | tail -1)
    SCORES+=($SCORE)
    echo "Seed $seed score: $SCORE"
done

# Calculate average
echo "=== Results ==="
python3 <<EOF
scores = [float(s) for s in "${SCORES[@]}".split()]
avg = sum(scores) / len(scores)
print(f"Seeds: {scores}")
print(f"Average: {avg:.2f}")
EOF
