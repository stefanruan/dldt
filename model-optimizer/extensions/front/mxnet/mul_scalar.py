"""
 Copyright (c) 2018-2019 Intel Corporation

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

from mo.front.common.replacement import FrontReplacementOp
from mo.graph.graph import Node, Graph
from mo.ops.lin_op import Mul
from mo.ops.const import Const


class MulScalarFrontReplacer(FrontReplacementOp):
    op = '_mul_scalar'
    enabled = True

    def replace_op(self, graph: Graph, node: Node):
        in_node = node.in_node()
        out_nodes = [node for node in node.out_nodes().values()]
        graph.remove_edge(node.in_node().id, node.id)
        scalar_value_op = Const(graph, dict(value=node.scalar, shape=node.scalar.shape, symbol_dict={'name': node.id + '/const'}))
        mul_op = Mul(graph, dict(name=node.id + '/mul_', symbol_dict={'name': node.id + '/mul_'}))
        mul_node = mul_op.create_node(inputs=[in_node, scalar_value_op.create_node()])

        for out_node in out_nodes:
            edge_attrs = graph.get_edge_data(node.id, out_node.id)[0]
            graph.remove_edge(node.id, out_node.id)
            graph.add_edges_from([(mul_node.id, out_node.id, edge_attrs)])

        return [mul_node.id]
