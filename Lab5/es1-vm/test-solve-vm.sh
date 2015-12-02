#!/usr/bin/env sh

for fname in `ls $1/*.json`; do
	echo "SOLVING INSTANCE $fname"
	python vm-reassignment.py $fname
done