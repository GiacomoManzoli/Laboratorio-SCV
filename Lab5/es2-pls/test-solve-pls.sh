#!/usr/bin/env sh

for fname in `ls $1/*.json`; do
	echo "SOLVING INSTANCE $fname"
	python pls.py $fname
done