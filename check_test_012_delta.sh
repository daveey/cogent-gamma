#!/bin/bash
echo "=== Attempt 012-delta: corner_pressure 8.0→7.0 ===" 
ps aux | grep "[p]ython3 -m cogames play" | awk '{print "PID", $2, "- Started:", $9, "- CPU:", $10}'
echo ""
echo "=== Results so far ===" 
tail -30 test_results_012_delta.txt
echo ""
echo "=== Timestamp ===" 
date
