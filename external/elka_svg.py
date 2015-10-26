#!/usr/bin/python3
# coding=utf-8
# Batteries
from xml.etree.ElementTree import iterparse as iterparse_xml
import re

# Own
import graphlib

# PyQt4
from PyQt4 import QtGui

# Numpy
import numpy

float_re = (r"([-+]?\d+\.\d+|[-+]?\d+"
             "|[-+]?\d+e[-+]\d+|[-+]?\d+\.\d+e[-+]\d+)")


def tokenize_svgdlang(d):
    cmds_re = r"([MmLlCcz])"
    cmds = re.split(cmds_re, d)
    for cmd, params in zip(cmds[:-1], cmds[1:]):
        if cmd == '':
            continue
        coords = re.findall(float_re, params)
        coords = list(map(float, coords))
        yield (cmd, coords)


def parse_svgdlang(d):
    path = QtGui.QPainterPath()
    head = (0, 0)
    ctrl = None
    for cmd, coords in tokenize_svgdlang(d):
        if cmd == "z":
            path.closeSubpath()
        elif cmd == "M":
            path.moveTo(coords[0], coords[1])
            head = (coords[0], coords[1])
        elif cmd == "m":
            path.moveTo(head[0]+coords[0], head[1]+coords[1])
            head = (head[0]+coords[0], head[1]+coords[1])
        elif cmd == "L":
            path.lineTo(coords[0], coords[1])
            head = (coords[0], coords[1])
        elif cmd == "l":
            path.lineTo(head[0]+coords[0], head[1]+coords[1])
            head = (head[0]+coords[0], head[1]+coords[1])
        elif cmd == "C":
            r = 0
            while r+6 <= len(coords):
                path.cubicTo(coords[r+0], coords[r+1],
                             coords[r+2], coords[r+3],
                             coords[r+4], coords[r+5])
                head = (coords[r+4], coords[r+5])
                ctrl = (coords[r+2], coords[r+3])
                r += 6
        elif cmd == "c":
            r = 0
            while r+6 <= len(coords):
                path.cubicTo(head[0]+coords[r+0], head[1]+coords[r+1],
                             head[0]+coords[r+2], head[1]+coords[r+3],
                             head[0]+coords[r+4], head[1]+coords[r+5])
                head = (head[0]+coords[r+4], head[1]+coords[r+5])
                ctrl = (head[0]+coords[r+2], head[1]+coords[r+3])
                r += 6
        elif cmd == "S":
            r = 0
            # SVG 1.1 spec: If a short hand is used before a full command
            # set the shortened control point to the last known endpoint
            ctrl = ctrl or head
            while r+6 <= len(coords):
                path.cubicTo(-ctrl[0], -ctrl[1],
                             coords[r+0], coords[r+1],
                             coords[r+2], coords[r+3])
                head = (coords[r+2], coords[r+3])
                ctrl = (coords[r+0], coords[r+1])
                r += 6
        elif cmd == "s":
            r = 0
            # SVG 1.1 spec: If a short hand is used before a full command
            # set the shortened control point to the last known endpoint
            ctrl = ctrl or head
            while r+6 <= len(coords):
                path.cubicTo(head[0]-ctrl[0], head[1]-ctrl[1],
                             head[0]+coords[r+0], head[1]+coords[r+1],
                             head[0]+coords[r+2], head[1]+coords[r+3])
                head = (head[0]+coords[r+2], head[1]+coords[r+3])
                ctrl = (head[0]+coords[r+0], head[1]+coords[r+1])
                r += 6
    return path


def parse_transform(inst):
    m = re.match("translate\( *"+float_re+" *, *"+float_re+" *\)", inst)
    if m != None:
        x, y = float(m.group(1)), float(m.group(2))
        return [[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, 0], [0, 0, 0, 1]]
    raise Exception("Invalid transform instruction: "+inst)


def find_subtree_titled(title, source):
    select = 0
    trace = []
    for ev, elem in iterparse_xml(source, events=["start", "end"]):
        if elem.tag == "{http://www.w3.org/2000/svg}g":
            if ev == "start":
                t = elem.find("{http://www.w3.org/2000/svg}title")
                if t != None and t.text == title:
                    select = select + 1
            elif ev == "end":
                select = select - 1
                assert select >= 0, "Element id {}".format(elem.attrib["id"])
                groups.pop()
        else:
            if select > 0:
                groups.append(elem)


def parse(infix, source):
    assert infix != "", "Weird things happen with infix == ''"
    mark = None
    mat_stack = [numpy.identity(4)]
    for ev, elem in iterparse_xml(source, events=("start", "end")):
        if elem.tag == "{http://www.w3.org/2000/svg}g":
            if ev == "start":
                # If a group has "infix" child set the mark to its id.
                # All elements below the mark will be part of the same
                # graph.
                t = elem.find("{http://www.w3.org/2000/svg}title")
                if t != None and infix in t.text:
                    mark = elem.attrib["id"]
                    # Begin a new paths group upon hitting a mark
                    name = t.text
                    paths = []
                elif "id" in elem.attrib and infix in elem.attrib["id"]:
                    mark = elem.attrib["id"]
                    # Begin a new paths group upon hitting a mark
                    name = elem.attrib["id"]
                    paths = []

                # Keep track of the current transformation stack.
                # This has to be done independently of the current mark
                # state since unmarked groups also contribute matrices.
                if "transform" in elem.attrib:
                    mat = parse_transform(elem.attrib["transform"])
                    mat_stack.append(mat_stack[-1].dot(numpy.array(mat)))

            elif ev == "end":
                # If the element which the mark was set on ends, the mark
                # has to be removed as well
                if "id" in elem.attrib and elem.attrib["id"] == mark:
                    mark = None

                    # Dump the current paths group upon leaving a mark.
                    # Even if the various groups have the same infix,
                    # but are part of different subtrees, their elements
                    # should be grouped independently
                    yield name, paths

                    # Remove from scope to make bugs visible
                    del name
                    del paths

                # Keep track of the transformation stack. See above.
                if "transform" in elem.attrib:
                    mat_stack.pop()

        # The following elements are only parsed if they are part of the
        # selection. Additionally, we only care for "end" events, since only
        # those guarantee that the text of an element has been parsed.
        if mark == None or ev != "end":
            continue

        if elem.tag == "{http://www.w3.org/2000/svg}line":
            # A SVG line element can be modeled as an open SVG path with
            # pen thickness but no fill. This conversion is allowed and
            # described in the SVG 1.1 spec.
            w = 0.25 # elem.attrib["style"] match stroke-width:float_re / 2

            v1 = numpy.array([float(elem.attrib["x1"]),
                              float(elem.attrib["y1"])])
            v2 = numpy.array([float(elem.attrib["x2"]),
                              float(elem.attrib["y2"])])

            # Get the normal vector of the line and calculate perpendicular
            # vectors, one to the left one to the right. It doesnt matter
            # which is which as long as they differ.
            n = v2 - v1
            n = n / numpy.linalg.norm(n)
            p = numpy.array([n[1], -n[0]]) * w
            q = numpy.array([-n[1], n[0]]) * w

            path = QtGui.QPainterPath()
            path.moveTo(*(v1+q))
            path.lineTo(*(v1+p))
            path.lineTo(*(v2+p))
            path.lineTo(*(v2+q))
            path.lineTo(*(v1+q))
            path.translate(mat_stack[-1][0, 3], mat_stack[-1][1, 3])
            paths.append(path)
        elif elem.tag == "{http://www.w3.org/2000/svg}path":
            if "style" in elem.attrib or "fill" in elem.attrib:
                # CSS styled elements are not yet supported.
                continue
            path = parse_svgdlang(elem.attrib["d"])
            path.translate(mat_stack[-1][0, 3], mat_stack[-1][1, 3])
            paths.append(path)


def path_intersections(paths):
    for i, path1 in enumerate(paths):
        for j, path2 in enumerate(paths):
            if path1 == path2:
                continue

            isctd = path1.intersected(path2)
            rect = isctd.controlPointRect()
            if not rect.isNull():
                yield (i, j, rect)


def most_distant_vertices(path):
    a, b = None, None
    for poly in path.toSubpathPolygons():
        for pnt in poly:
            if a == None:
                a = pnt
            elif b == None:
                b = pnt
                d = (b.x()-a.x())**2+(b.y()-a.y())**2
            else:
                d_a = (a.x()-pnt.x())**2+(a.y()-pnt.y())**2
                d_b = (b.x()-pnt.x())**2+(b.y()-pnt.y())**2
                if d_a > d:
                    b = pnt
                    d = d_a
                elif d_b > d:
                    a = pnt
                    d = d_b
                else:
                    pass

    assert a != None and b != None
    return ((a.x(), a.y()), (b.x(), b.y()))


def graph_from_paths(paths):
    paths_iscts = {}
    paths_ends = []

    vertices = []
    edges = []

    # Find intersections between paths.
    for i, j, rect in path_intersections(paths):
        center = (rect.x()+rect.width()*0.5, rect.y()+rect.height()*0.5)
        vertices.append(center)
        paths_iscts[i, j] = len(vertices)-1

    # Find the beginning and end of a cuneiform stroke
    for path in paths:
        res = most_distant_vertices(path)
        assert res != None
        vertices.append((res[0][0], res[0][1]))
        vertices.append((res[1][0], res[1][1]))
        paths_ends.append((len(vertices)-2, len(vertices)-1))

    # De-duplicate and merge vertices for a simplified graph
    vertices, remap = graphlib.merge_vertices(vertices)
    paths_iscts = {(i, j): remap[k] for (i, j), k in paths_iscts.items()}
    paths_ends = [(remap[i], remap[j]) for i, j in paths_ends]

    # Use a titled sweepline to reconnect vertices and form edges
    for i in range(len(paths)):
        ends = paths_ends[i]
        iscts = [n for (l, m), n in paths_iscts.items() if l == i]
        # Remove duplicates from collapsed edges.
        stroke = list(set([ends[0]] + iscts + [ends[1]]))
        # Tilted sweep line sorting.
        # unfortunately
        stroke.sort(key=lambda a: vertices[a][0]-vertices[a][1])
        for v1, v2 in zip(stroke[:-1], stroke[1:]):
            assert v1 != v2, "Edges from and to the same vertex are invalid."
            edges.append((v1, v2))

    # Build a adjacency matrix from the edge and vertex lists
    adjacency = numpy.zeros((len(vertices), len(vertices)))
    for edge in edges:
        adjacency[edge[0], edge[1]] = 1
        adjacency[edge[1], edge[0]] = 1

    assert (adjacency.T == adjacency).all(), ("Adjacency matrix of an"
        "undirected graph has to be symmetric.")

    # Since the shape of vertices is unlikely to change anymore
    # use a numpy.array instead, more functions work with numpy.arrays
    vertices = numpy.array(vertices)

    # Labels have to be a python list since any object, not only integers,
    # are valid labels
    labels = list(range(len(vertices)))

    return graphlib.Graph(labels, vertices, adjacency)


def path_to_vertices(path):
    vertices = []
    for poly in path.toSubpathPolygons():
        for pnt in poly:
            vertices.append((pnt.x(), pnt.y()))
    return vertices
