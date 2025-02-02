#!/bin/bash
if [ ! -f metrics.py ]; then
    curl https://raw.githubusercontent.com/sarnthil/emotion-stimulus-detection/main/scripts/eval/metrics.py > metrics.py
fi
if [ ! -f count_errors.py ]; then
    curl https://raw.githubusercontent.com/sarnthil/emotion-stimulus-detection/main/scripts/eval/count_errors.py > count_errors.py
fi

# location of the predictions.json file
PREDFILE=$1

# domain analysis
echo "Domain Analysis on Norec:"
python3 domain_analysis.py ../data/norec/test.json $PREDFILE metadata.json

# negation analysis
echo "Negation Analysis on Norec:"
python3 neg_scope_analysis.py ../data/norec/test.json $PREDFILE negation_test.json

# overlap analysis
echo "Overlap Analysis:"
./assemble_overlap_data.sh
python3  plot_overlaps.py

# qualitative analysis
echo "Qualitative Analysis:"
GOLDPATH=$2 # location of gold test data
PREDPATH=$3 # location of teams submissions
python3 aggregate_qualitative_analysis.py $GOLDPATH $PREDPATH