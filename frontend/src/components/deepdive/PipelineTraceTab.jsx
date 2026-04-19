import { motion } from 'framer-motion';
import { Clock, Zap, CheckCircle2, Timer } from 'lucide-react';
import { formatDuration } from '../../utils/formatters';

/* Tool icon/emoji mapping */
const TOOL_ICONS = {
  ProfileUserTool: '👤',
  CalculateRiskTool: '📊',
  SimulateScenarioTool: '⚡',
  EvaluatePoliciesTool: '📋',
  ValidateCriticTool: '🔍',
  LearnAdaptiveTool: '🧠',
  CheckComplianceTool: '✅',
  PersistMemoryTool: '💾',
};

const PipelineTraceTab = ({ result }) => {
  const trace = result.agent_trace || [];
  const totalMs = trace.reduce((sum, t) => sum + t.duration_ms, 0);

  return (
    <div className="space-y-8 pb-10">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <h2 className="text-[32px] font-black text-white tracking-tight mb-1">Pipeline Trace</h2>
        <p className="text-[13px] text-white/20 font-medium">Execution timeline of the multi-agent pipeline</p>
      </motion.div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 gap-5">
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.08 }}
          className="pipeline-stat-card">
          <Timer className="w-4 h-4 text-white/15 mb-2" />
          <p className="text-[9px] text-white/15 uppercase tracking-[3px] font-bold mb-1">Steps</p>
          <p className="text-3xl font-black font-mono-num text-white/80">{trace.length}</p>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.14 }}
          className="pipeline-stat-card">
          <Clock className="w-4 h-4 text-white/15 mb-2" />
          <p className="text-[9px] text-white/15 uppercase tracking-[3px] font-bold mb-1">Duration</p>
          <p className="text-3xl font-black font-mono-num text-white/80">{formatDuration(totalMs)}</p>
        </motion.div>
      </div>

      {/* Timeline */}
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-5 top-0 bottom-0 w-px"
          style={{ background: 'linear-gradient(180deg, rgba(99,102,241,0.15), rgba(99,102,241,0.02))' }} />

        <div className="space-y-1">
          {trace.map((entry, i) => {
            const emoji = TOOL_ICONS[entry.agent_name] || '⚙️';
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 + i * 0.04, ease: [0.4, 0, 0.2, 1] }}
                className="relative pl-14 py-3"
              >
                {/* Timeline dot */}
                <div className="absolute left-[14px] top-[18px] w-[11px] h-[11px] rounded-full z-10 flex items-center justify-center"
                  style={{
                    background: '#0A0A0A',
                    border: '2px solid rgba(99,102,241,0.25)',
                    boxShadow: '0 0 6px rgba(99,102,241,0.15)',
                  }}
                />

                {/* Card */}
                <div className="pipeline-entry-card">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-sm">{emoji}</span>
                      <span className="text-[13px] font-bold text-white/65">{entry.agent_name}</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-[11px] text-white/20 font-mono-num">
                      <Clock className="w-3 h-3" />
                      {formatDuration(entry.duration_ms)}
                    </div>
                  </div>
                  <div className="mt-2 text-[11px] text-white/20 space-y-0.5">
                    <p><span className="text-white/30 font-medium">In:</span> {entry.input_summary}</p>
                    <p><span className="text-white/30 font-medium">Out:</span> {entry.output_summary}</p>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>

      {trace.length === 0 && (
        <div className="text-center py-16 text-white/10 text-sm">No trace data available.</div>
      )}
    </div>
  );
};

export default PipelineTraceTab;
