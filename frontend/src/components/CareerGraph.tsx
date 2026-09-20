import { useEffect, useState } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
  type Node,
  type Edge
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import dagre from 'dagre';
import { api } from '../lib/api';

interface GraphData {
  nodes: { id: string; name: string; category: string }[];
  edges: { source: string; target: string }[];
}

const nodeWidth = 180;
const nodeHeight = 50;

function getLayoutedElements(nodes: any[], edges: any[], direction = 'TB') {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({ rankdir: direction });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  nodes.forEach((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    node.targetPosition = direction === 'TB' ? 'top' : 'left';
    node.sourcePosition = direction === 'TB' ? 'bottom' : 'right';
    // We are shifting the dagre node position (anchor=center) to the top left
    node.position = {
      x: nodeWithPosition.x - nodeWidth / 2,
      y: nodeWithPosition.y - nodeHeight / 2,
    };
    return node;
  });

  return { nodes, edges };
}

export function CareerGraph({ careerId }: { careerId: string }) {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<GraphData>(`/careers/${careerId}/graph`).then((data) => {
      const initialNodes = data.nodes.map((n) => ({
        id: n.id,
        data: { label: n.name },
        style: {
          background: 'var(--paper-raised)',
          border: '1px solid var(--line-dark)',
          borderRadius: '8px',
          fontSize: '12px',
          fontWeight: 500,
          color: 'var(--ink)',
          width: nodeWidth,
          padding: '10px'
        },
      }));
      const initialEdges = data.edges.map((e, idx) => ({
        id: `e${idx}`,
        source: e.source,
        target: e.target,
        animated: true,
        style: { stroke: 'var(--teal)' },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: 'var(--teal)',
        },
      }));

      const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
        initialNodes,
        initialEdges
      );

      setNodes(layoutedNodes);
      setEdges(layoutedEdges);
      setLoading(false);
    });
  }, [careerId, setNodes, setEdges]);

  if (loading) {
    return <div className="h-64 flex items-center justify-center text-[var(--slate)]">Loading graph...</div>;
  }

  if (nodes.length === 0) {
    return null;
  }

  return (
    <div style={{ height: 600 }} className="w-full rounded-xl border border-[var(--line)] bg-[var(--paper)]">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
