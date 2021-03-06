from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import getopt
import os
import sys

import graphlearn as gl
import numpy as np
import time


def main(argv):
  cur_path = sys.path[0]

  task_index = 0
  task_count = 1
  tracker = ""
  hosts= ""

  opts, args = getopt.getopt(argv, 'c:j:t:', ['task_index=', 'task_count=', 'tracker=', 'hosts='])
  for opt, arg in opts:
    if opt in ('-c', '--task_index'):
      task_index = int(arg)
    elif opt in ('-j', '--task_count'):
      task_count = int(arg)
    elif opt in ('-t', '--tracker'):
      tracker = arg
    elif opt in ('-h', '--hosts'):
      hosts = arg
    else:
      pass

  mode = 0 if hosts else 1
  gl.set_tracker_mode(mode)

  g = gl.Graph()

  g.node(os.path.join(cur_path, "data/user"),
         node_type="user", decoder=gl.Decoder(weighted=True)) \
    .node(os.path.join(cur_path, "data/item"),
          node_type="item", decoder=gl.Decoder(attr_types=['string', 'int', 'float', 'float', 'string'])) \
    .edge(os.path.join(cur_path, "data/u-i"),
          edge_type=("user", "item", "buy"), decoder=gl.Decoder(weighted=True))

  if mode == 0:
    g.init(task_index, hosts=hosts)
  else:
    g.init(task_index, task_count, tracker=tracker)

  print("Get Edges...")
  edges = g.E("buy").batch(2).shuffle().emit()
  print(edges.src_ids)
  print(edges.dst_ids)
  print(edges.weights)
  print("Get Edges Done...")

  print("Get Nodes...")
  print("Get user Nodes...")
  nodes = g.V("user", np.array([0, 1, 2, 3, 4])).emit()
  print(nodes.ids)
  print(nodes.weights)
  print("Get item Nodes...")
  nodes = g.V("item").batch(4).shuffle().emit()
  print(nodes.ids)
  print(nodes.int_attrs)
  print(nodes.float_attrs)
  print(nodes.string_attrs)
  print("Query item Nodes...")
  nodes = g.V("item", np.array([101, 102, 103])).emit()
  print(nodes.ids)
  print(nodes.int_attrs)
  print("Get Nodes Done...")

  print("Random sample...")
  s = g.neighbor_sampler("buy", expand_factor=2, strategy="random")
  nodes = s.get(np.array([0, 1, 2])).layer_nodes(1)
  print(nodes.ids)
  print(nodes.float_attrs)
  print(nodes.embedding_agg(func="mean"))
  print("Random Sample Done...")

  print("Full sample...")
  s = g.neighbor_sampler("buy", expand_factor=2, strategy="full")
  nodes = s.get(np.array([0, 1, 2])).layer_nodes(1)
  print(nodes.ids)
  print(nodes.offsets)
  print(nodes.embedding_agg())
  print("Full Sample Done...")

  print("InDegree neg sample...")
  s = g.negative_sampler("buy", expand_factor=3, strategy="in_degree")
  print(s.get(np.array([0, 1, 2])).ids)
  print("InDegree Negative Sample Done...")

  print("NodeWeight neg sample...")
  s = g.negative_sampler("user", expand_factor=3, strategy="node_weight")
  print(s.get(np.array([0, 1, 2])).ids)
  print("NodeWeight Negative Sample Done...")
  g.close()


if __name__ == "__main__":
  main(sys.argv[1:])