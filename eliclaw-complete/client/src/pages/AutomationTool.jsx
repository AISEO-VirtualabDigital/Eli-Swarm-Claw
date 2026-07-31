import { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import ReactFlow, {
  Controls, Background, MiniMap,
  addEdge, useNodesState, useEdgesState,
  Handle, Position
} from 'react-flow-renderer'
import 'react-flow-renderer/dist/style.css'
import {
  Zap, Play, Save, Trash2, Plus, GitBranch, Mail, Search,
  Globe, FileText, Bell, Clock, Loader2, CheckCircle
} from 'lucide-react'
import toast from 'react-hot-toast'

// Custom Node Components
const TriggerNode = ({ data }) => (
  <div className="bg-green-500/10 border-2 border-green-500/30 rounded-xl p-4 min-w-[180px]">
    <Handle type="source" position={Position.Bottom} className="w-3 h-3 bg-green-500" />
    <div className="flex items-center gap-2 mb-2">
      <Zap size={16} className="text-green-400" />
      <span className="font-semibold text-sm">{data.label}</span>
    </div>
    <p className="text-xs text-dark-400">{data.description}</p>
  </div>
)

const ActionNode = ({ data }) => (
  <div className="bg-primary-500/10 border-2 border-primary-500/30 rounded-xl p-4 min-w-[180px]">
    <Handle type="target" position={Position.Top} className="w-3 h-3 bg-primary-500" />
    <Handle type="source" position={Position.Bottom} className="w-3 h-3 bg-primary-500" />
    <div className="flex items-center gap-2 mb-2">
      <data.icon size={16} className="text-primary-400" />
      <span className="font-semibold text-sm">{data.label}</span>
    </div>
    <p className="text-xs text-dark-400">{data.description}</p>
  </div>
)

const ConditionNode = ({ data }) => (
  <div className="bg-yellow-500/10 border-2 border-yellow-500/30 rounded-xl p-4 min-w-[180px]">
    <Handle type="target" position={Position.Top} className="w-3 h-3 bg-yellow-500" />
    <Handle type="source" position={Position.Bottom} className="w-3 h-3 bg-yellow-500" />
    <div className="flex items-center gap-2 mb-2">
      <GitBranch size={16} className="text-yellow-400" />
      <span className="font-semibold text-sm">{data.label}</span>
    </div>
    <p className="text-xs text-dark-400">{data.description}</p>
  </div>
)

const nodeTypes = {
  trigger: TriggerNode,
  action: ActionNode,
  condition: ConditionNode,
}

const nodeTemplates = [
  { type: 'trigger', label: 'New Lead', description: 'When a new lead is captured', icon: Zap, data: { trigger: 'new_lead' } },
  { type: 'trigger', label: 'Schedule', description: 'Run on a schedule', icon: Clock, data: { trigger: 'schedule' } },
  { type: 'action', label: 'Send Email', description: 'Send email to lead', icon: Mail, data: { action: 'send_email' } },
  { type: 'action', label: 'Run Audit', description: 'SEO audit on URL', icon: Search, data: { action: 'run_audit' } },
  { type: 'action', label: 'Notify Slack', description: 'Send Slack notification', icon: Bell, data: { action: 'slack_notify' } },
  { type: 'action', label: 'Generate Report', description: 'Create PDF report', icon: FileText, data: { action: 'generate_report' } },
  { type: 'condition', label: 'Score Check', description: 'If SEO score < 70', icon: GitBranch, data: { condition: 'score_check' } },
  { type: 'condition', label: 'URL Match', description: 'If URL contains...', icon: Globe, data: { condition: 'url_match' } },
]

export default function AutomationTool() {
  const [nodes, setNodes, onNodesChange] = useNodesState([
    {
      id: '1',
      type: 'trigger',
      position: { x: 250, y: 50 },
      data: { label: 'New Lead', description: 'When a new lead is captured', icon: Zap },
    },
  ])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [selectedNode, setSelectedNode] = useState(null)
  const [workflowName, setWorkflowName] = useState('My Workflow')
  const [isRunning, setIsRunning] = useState(false)

  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), [setEdges])

  const addNode = (template) => {
    const newNode = {
      id: `${nodes.length + 1}`,
      type: template.type,
      position: { x: 250, y: nodes.length * 120 + 50 },
      data: { label: template.label, description: template.description, icon: template.icon },
    }
    setNodes((nds) => [...nds, newNode])
    toast.success(`Added ${template.label} node`)
  }

  const deleteNode = () => {
    if (selectedNode) {
      setNodes((nds) => nds.filter((n) => n.id !== selectedNode.id))
      setEdges((eds) => eds.filter((e) => e.source !== selectedNode.id && e.target !== selectedNode.id))
      setSelectedNode(null)
      toast.success('Node deleted')
    }
  }

  const runWorkflow = () => {
    setIsRunning(true)
    setTimeout(() => {
      setIsRunning(false)
      toast.success('Workflow executed successfully!')
    }, 2000)
  }

  const saveWorkflow = () => {
    toast.success('Workflow saved!')
  }

  return (
    <div className="space-y-6 h-[calc(100vh-120px)]">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold mb-2">Automation Workflows</h1>
        <p className="text-dark-400">Build visual workflows that run automatically. Drag, connect, and deploy.</p>
      </motion.div>

      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-3">
        <input
          type="text"
          value={workflowName}
          onChange={(e) => setWorkflowName(e.target.value)}
          className="input-field w-64"
        />
        <button onClick={runWorkflow} disabled={isRunning} className="btn-primary flex items-center gap-2 disabled:opacity-50">
          {isRunning ? <><Loader2 size={16} className="animate-spin" /> Running...</> : <><Play size={16} /> Run</>}
        </button>
        <button onClick={saveWorkflow} className="btn-secondary flex items-center gap-2">
          <Save size={16} /> Save
        </button>
        {selectedNode && (
          <button onClick={deleteNode} className="px-4 py-2 bg-red-500/10 text-red-400 rounded-xl hover:bg-red-500/20 transition-colors flex items-center gap-2">
            <Trash2 size={16} /> Delete Node
          </button>
        )}
      </div>

      <div className="flex gap-4 h-full">
        {/* Node Palette */}
        <div className="w-64 glass-panel p-4 overflow-y-auto">
          <h3 className="font-bold mb-4">Node Library</h3>
          <div className="space-y-2">
            {nodeTemplates.map((template, i) => (
              <button
                key={i}
                onClick={() => addNode(template)}
                className="w-full text-left p-3 bg-dark-700/50 rounded-xl hover:bg-dark-600 transition-colors flex items-center gap-3"
              >
                <template.icon size={18} className={
                  template.type === 'trigger' ? 'text-green-400' :
                  template.type === 'condition' ? 'text-yellow-400' : 'text-primary-400'
                } />
                <div>
                  <p className="font-medium text-sm">{template.label}</p>
                  <p className="text-xs text-dark-500">{template.description}</p>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Canvas */}
        <div className="flex-1 glass-panel rounded-2xl overflow-hidden">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={(_, node) => setSelectedNode(node)}
            nodeTypes={nodeTypes}
            fitView
          >
            <Controls />
            <MiniMap 
              nodeColor={(n) => {
                if (n.type === 'trigger') return '#22c55e'
                if (n.type === 'condition') return '#f59e0b'
                return '#3b82f6'
              }}
              maskColor="rgba(15, 23, 42, 0.8)"
            />
            <Background color="#334155" gap={16} />
          </ReactFlow>
        </div>
      </div>
    </div>
  )
}