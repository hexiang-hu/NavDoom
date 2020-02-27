from __future__ import print_function

import argparse
import numpy as np
import glob
import os
import ipdb

def _command_line_parser():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '-o',
      '--output',
      type=str,
      default='outputs/sources')
  parser.add_argument(
      '-m',
      '--maps',
      type=str,
      required=True)

  return parser

WALL_TYPE = np.int8
WALL = 0
EMPTY = 1

class Maze:
  def __init__(self, map_filepath):
    assert os.path.exists(map_filepath)
    with open(map_filepath, 'r') as fd:
      def _process_map_str(token):
        return WALL if token == '#' else EMPTY
      # Generate map for maze
      board = np.array([ [ _process_map_str(char) for char in line.strip('\n') ] \
                                                  for line in fd.readlines() ], dtype=WALL_TYPE)

    self.board = board
    self.nrows = board.shape[0]
    self.ncolumns = board.shape[1]

  def __str__(self):
    return os.linesep.join(''.join('X' if self.is_wall(i, j) else ' '
                                     for j in range(self.ncolumns))
                             for i in range(self.nrows))

  def __hash__(self):
    return hash(self.board.tostring())

  def __eq__(self, other):
    return np.array_equal(self.board, other.board)

  def set_borders(self):
    self.board[0, :] = self.board[-1, :] = WALL
    self.board[:, 0] = self.board[:, -1] = WALL

  def is_wall(self, x, y):
    assert self.in_maze(x, y)
    return self.board[x][y] == WALL

  def set_wall(self, x, y):
    assert self.in_maze(x, y)
    self.board[x][y] = WALL

  def remove_wall(self, x, y):
    assert self.in_maze(x, y)
    self.board[x][y] = EMPTY

  def in_maze(self, x, y):
    return 0 <= x < self.nrows and 0 <= y < self.ncolumns

  def write_to_file(self, filename):
    f = open(filename, 'w')
    f.write(str(self))
    f.close()

if __name__ == '__main__':
  parser = _command_line_parser()
  FLAGS = parser.parse_args()

  print(FLAGS.maps)
  map_filepaths = glob.glob(os.path.join(FLAGS.maps, '*.txt'))
  mazes = set()
  for idx, map_filepath in enumerate(map_filepaths):
    print('Processing {}'.format(map_filepath))
    maze = Maze(map_filepath)
    maze_name = "{}".format(os.path.basename(map_filepath))

    maze.write_to_file(os.path.join(FLAGS.output, maze_name))
