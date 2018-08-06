#!/bin/bash
kill -9 `pgrep raspivid`
kill -9 `pgrep ffmpeg`
printf "Video stopped"
