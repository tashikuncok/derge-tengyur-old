#!/bin/bash

cd ~/Users/trinley/github/derge-tengyur/notes

while read line

do

OldImageName=${line%,*}

NewImageName=${line#*,}

mv "$OldImageName" "$NewImageName"

done <"names.csv"