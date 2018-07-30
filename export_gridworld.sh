#!/usr/bin/env bash
set -e

rm -rf outputs
mkdir -p outputs
mkdir -p outputs/sources
mkdir -p outputs/images

NUM_MAZES=200

ACC="./acc/acc"
if [ ! -f $ACC ]; then
	echo "File $ACC does not exist, compiling..."
	make -C ./acc
fi

for FILE in content/*.acs; do
	$ACC -i ./acc $FILE "outputs/$(basename ${FILE%.*}).o"
done

PREFIX="./outputs/sources"
MAPPATH="./maps/"
echo "python maze_from_gridworld.py -o $PREFIX -m $MAPPATH"
python maze_from_gridworld.py -o $PREFIX -m $MAPPATH
python wad_for_gridworld.py "${PREFIX}" "outputs/" -b outputs/static_goal_train.o
echo "Success."
