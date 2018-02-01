#!/bin/bash
#to be tested for optimal quality/latency proportion

start_video() {
    #raspivid -w 800 -h 500 -fps 10 -vf -hf -cd MJPEG -t 0 -o - | ffmpeg -loglevel panic -i - -f mpegts -codec:v mpeg1video -s 800x500 -b:v 750k https://robots.brainyant.eu:8080/$1
    ffmpeg -loglevel panic -i - -f mpegts -codec:v mpeg1video -s 800x500 -b:v 750k https://robots.brainyant.eu:8080/$1 <(raspivid -w 800 -h 500 -fps 10 -vf -hf -cd MJPEG -t 0 -o -)
}

if [ -z $1 ]; then
    printf "Usage: $0 <secret key>"
else
  until start_video $1; do
    sleep 1
  done
fi
