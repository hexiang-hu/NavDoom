#!/usr/bin/env bash
set -e

OP_DIR=$1

if [ -z "$OP_DIR" ]; then
	echo "need to specify operation directory"
	exit
fi

MAPPATH=$OP_DIR/maps

if [ ! -e $MAPPATH ]; then
	echo "need maps directory"
	exit
fi

rm -rf $OP_DIR/outputs
mkdir -p $OP_DIR/outputs
mkdir -p $OP_DIR/outputs/sources
mkdir -p $OP_DIR/outputs/images

NUM_MAZES=200

ACC="./acc/acc"
if [ ! -f $ACC ]; then
	echo "File $ACC does not exist, compiling..."
	make -C ./acc
fi

for FILE in content/*.acs; do
	$ACC -i ./acc $FILE "$OP_DIR/outputs/$(basename ${FILE%.*}).o"
done

PREFIX="$OP_DIR/outputs/sources"

echo "python maze_from_gridworld.py -o $PREFIX -m $MAPPATH"
python maze_from_gridworld.py -o $PREFIX -m $MAPPATH
python wad_for_gridworld.py "${PREFIX}" "$OP_DIR/outputs/" -b $OP_DIR/outputs/griddoom.o
echo "Success."

#python wad_for_gridworld.py "./outputs/sources" "outputs/" -b outputs/griddoom.o
