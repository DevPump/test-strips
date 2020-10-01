#!/usr/bin/env sh
working_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
while true; do
	python "$working_dir/app.py";
    sleep 5
done;
