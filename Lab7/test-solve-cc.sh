#!/usr/bin/env sh

for fname in `ls $1/*.json`; do
	echo "SOLVING INSTANCE $fname"
	python cloud-comp.py $fname
	#ortools-python cloud-comp.py $fname
	echo ''
done