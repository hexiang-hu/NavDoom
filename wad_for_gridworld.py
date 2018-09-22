import re
from omg import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('prefix')
parser.add_argument('wad')
parser.add_argument(
    '-b',
    '--behavior',
    default=False,
    help='path to compiled lump containing map behavior (default: None)')
parser.add_argument(
    '-s',
    '--script',
    default=False,
    help='path to script source lump containing map behavior (optional)')

BLOCK_SIZE = 96
COLORS = [[2, 3, 4], [5, 6, 7], [8, 9, 10]]

def build_wall(maze):
    things = []
    linedefs = []
    vertexes = []
    v_indexes = {}

    max_w = len(maze[0]) - 1
    max_h = len(maze) - 1

    def __is_edge(w, h):
        return w in (0, max_w) or h in (0, max_h)

    def __add_start(w, h):
        x, y = w * BLOCK_SIZE, h * BLOCK_SIZE
        x += int(BLOCK_SIZE / 2)
        y += int(BLOCK_SIZE / 2)
        things.append(ZThing(*[len(things) + 1000, x, y, 0, 0, 9001, 22279]))

    def __add_vertex(w, h):
        if (w, h) in v_indexes:
            return

        x, y = w * BLOCK_SIZE, h * BLOCK_SIZE
        x += int(BLOCK_SIZE / 2)
        y += int(BLOCK_SIZE / 2)
        v_indexes[w, h] = len(vertexes)
        vertexes.append(Vertex(x, y))

    def __add_line(start, end, edge=False, front=0, back=0):
        assert start in v_indexes
        assert end in v_indexes

        mask = 1
        if __is_edge(*start) and __is_edge(*end):
            if not edge:
                return
            else:
                # Changed the back side (one towards outside the map)
                # to be -1 (65535 for Doom)
                back = 65535
                mask = 15

        # Flipped end and start vertices to make lines "point" at back direction (mostly to see if it works)
        line_properties = [v_indexes[end], v_indexes[start], mask
                           ] + [0] * 6 + [front, back]
        line = ZLinedef(*line_properties)
        linedefs.append(line)

    for h, row in enumerate(maze):
        for w, block in enumerate(row.strip()):
            if block == 'X':
                __add_vertex(w, h)
            else:
                pass

    corners = [[( 0, 0), ( 0, 5), ( 0, 10), ( 0, 15)],
               [( 5, 0), ( 5, 5), ( 5, 10), ( 5, 15)],
               [(10, 0), (10, 5), (10, 10), (10, 15)],
               [(15, 0), (15, 5), (15, 10), (15, 15)]]
    # corners = [(0, 0), (0, max_w), (max_h, 0), (max_h, max_w)]
    for _corners in corners:
        for v in _corners:
            __add_vertex(*v)
    
    def wall_colors(x, y):
        _x = min(x, 14) // 5
        _y = min(y, 14) // 5
        return COLORS[_x][_y]

    j = 0
    for i in range(len(corners[0]))[::-1]:
        if i != 0:
            __add_line(corners[j][i], corners[j][i - 1], True, COLORS[min(j,2)][min(i-1,2)])

    j = len(corners) - 1
    for i in range(len(corners[0])):
        if i != (len(corners[0]) - 1):
            __add_line(corners[j][i], corners[j][i + 1], True, COLORS[min(j,2)][min(i,2)])
    
    i = len(corners[0]) - 1
    for j in range(len(corners))[::-1]:
        if j != 0:
            __add_line(corners[j][i], corners[j - 1][i], True, COLORS[min(j-1,2)][min(i,2)])

    i = 0
    for j in range(len(corners)):
        if j != len(corners) - 1:
            __add_line(corners[j][i], corners[j + 1][i], True, COLORS[min(j,2)][min(i,2)])


    # Now connect the walls
    for h, row in enumerate(maze):
        for w, _ in enumerate(row):
            if (w, h) not in v_indexes:
                __add_start(w, h)
                continue

            if (w + 1, h) in v_indexes:
                front = wall_colors(w, max(h-1, 0))
                back = wall_colors(w, min(h+1, 15))
                # if h == 0 or h == 15:
                #     __add_line((w, h), (w + 1, h), True, front, back)
                # else:
                __add_line((w, h), (w + 1, h), False, back, front)

            if (w, h + 1) in v_indexes:
                front = wall_colors(max(w-1, 0), h)
                back = wall_colors(min(w+1, 15), h)
                # if w == 0 or w == 15:
                #     __add_line((w, h), (w, h + 1), True, front, back)
                # else:
                __add_line((w, h), (w, h + 1), False, front, back)

    return things, vertexes, linedefs


def main(flags):


    for map_index, file_name in enumerate(
            glob.glob('{}/*.txt'.format(flags.prefix))):

        new_wad = WAD()
        with open(file_name) as maze_source:
            maze = [line.strip() for line in maze_source.readlines()]
            maze = [line for line in maze if line]

        new_map = MapEditor()
        new_map.Linedef = ZLinedef
        new_map.Thing = ZThing
        new_map.behavior = Lump(from_file=flags.behavior or None)
        new_map.scripts = Lump(from_file=flags.script or None)
        things, vertexes, linedefs = build_wall(maze)
        new_map.things = things + [ZThing(0, 0, 0, 0, 0, 1, 7)]
        new_map.vertexes = vertexes
        new_map.linedefs = linedefs
        new_map.sectors = [ Sector(0, 128, 'CEIL5_2', 'CEIL5_2', 240, 0, 0) ]
        new_map.sidedefs = [
            Sidedef(0, 0, '-', '-', 'STONE2', 0),   # 0
            Sidedef(0, 0, '-', '-', '-', 0),        # 1
            Sidedef(0, 0, 'BIGBRIK1', 'BIGBRIK1', 'BIGBRIK1', 0), # 2
            Sidedef(0, 0, 'BIGBRIK2', 'BIGBRIK2', 'BIGBRIK2', 0), # 3
            Sidedef(0, 0, 'SFALL1', 'SFALL1', 'SFALL1', 0),       # 4
            Sidedef(0, 0, 'SILVER1', 'SILVER1', 'SILVER1', 0),    # 5
            Sidedef(0, 0, 'SILVER2', 'SILVER2', 'SILVER2', 0),    # 6
            Sidedef(0, 0, 'BIGDOOR2', 'BIGDOOR2', 'BIGDOOR2', 0), # 7
            Sidedef(0, 0, 'BIGBRIK3', 'BIGBRIK3', 'BIGBRIK3', 0), # 8
            Sidedef(0, 0, 'SILVER3', 'SILVER3', 'SILVER3', 0), # 9
            Sidedef(0, 0, 'STONE2', 'STONE2', 'STONE2', 0),    # 10
        ]
        new_wad.maps['MAP01'] = new_map.to_lumps()

        new_wad.to_file(os.path.join(flags.wad, "{}.wad".format(os.path.basename(file_name))))


if __name__ == "__main__":
    main(parser.parse_args())
