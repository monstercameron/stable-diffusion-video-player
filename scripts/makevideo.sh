#!/bin/bash

# Specify the path to the folder containing frames
FRAMES_DIR='./output'

# Specify the output filename
OUTPUT_FILE="./outputvideos/output.mp4"

# Use ffmpeg to convert the frames into an mp4 file
ffmpeg -y -framerate 24 -i "$FRAMES_DIR/frame%04d.png" -c:v libx264 -pix_fmt yuv420p "$OUTPUT_FILE"
