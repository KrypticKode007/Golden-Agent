import React, { useState } from 'react';
import { 
  Activity, 
  Cpu, 
  HardDrive, 
  Thermometer, 
  BatteryCharging, 
  Layers, 
  Terminal, 
  Clock, 
  Trash2, 
  RefreshCw, 
  Filter, 
  Zap,
  Gauge,
  Download,
  Check
} from 'lucide-react';
import { SystemTelemetryState, TelemetryLog } from '../types';

interface TelemetryViewProps {
  telemetry: SystemTelemetryState;
  latencyHistory: number[];
  logs: TelemetryLog[];
  onManualCycle: () => void;
  onClearLogs: () => void;
  onResetDefaults: () => void;
  onUpdateBattery: (pct: number, status: 'AC_POWERED' | 'CHARGING' | 'DISCHARGING') => void;
}

export const TelemetryView: React.FC<TelemetryViewProps> = ({
  telemetry,
  latencyHistory,
  logs,
  onManualCycle,
  onClearLogs,
  onResetDefaults,
  onUpdateBattery,
}) => {
  const [selectedModuleFilter, setSelectedModuleFilter] = useState<string>('ALL');
  const [isExporting, setIsExporting] = useState<boolean>(false);

  const handleExportJSON = () => {
    const exportData = {
      export_timestamp: new Date().toISOString(),
      system_telemetry: {
        node_id: 'AEGIS-CORE-01',
        cpu_load_pct: telemetry.cpuLoad,
        memory_used_gb: telemetry.memoryUsedGb,
        memory_total_gb: telemetry.memoryTotalGb,
        gpu_temp_c: telemetry.gpuTempC,
        battery_pct: telemetry.batteryPercentage,
        power_status: telemetry.powerStatus,
        current_latency_micros: telemetry.currentLatencyMicros,
        throttling_delay_seconds: telemetry.throttlingDelaySeconds,
        core_status: telemetry.coreStatus,
        active_threads: telemetry.activeThreads,
      },
      latency_history_micros: latencyHistory,
      telemetry_logs: logs,
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `golden_agent_telemetry_export_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    setIsExporting(true);
    setTimeout(() => setIsExporting(false), 2000);
  };

  const avgLatency = latencyHistory.length > 0
    ? (latencyHistory.reduce((a, b) => a + b, 0) / latencyHistory.length).toFixed(1)
    : '14.2';
  const maxLatency = latencyHistory.length > 0
    ? Math.max(...latencyHistory).toFixed(1)
    : '18.6';
  const minLatency = latencyHistory.length > 0
    ? Math.min(...latencyHistory).toFixed(1)
    : '11.8';

  const filteredLogs = selectedModuleFilter === 'ALL'
    ? logs
    : logs.filter((l) => l.module_name === selectedModuleFilter);

  const modules = ['ALL', ...Array.from(new Set(logs.map((l) => l.module_name)))];

  // Micro-graph / sparkline calculation
  const historySlice = latencyHistory.slice(-48);
  const minVal = historySlice.length > 0 ? Math.min(...historySlice) : 0;
  const maxVal = historySlice.length > 0 ? Math.max(...historySlice) : 25;
  const range = maxVal - minVal || 1;

  return (
    <div className="space-y-4">
      {/* Top Banner Notice */}
      <div className="flex flex-wrap items-center justify-between text-xs bg-slate-900/60 border border-slate-800 px-3.5 py-2 rounded">
        <div className="flex items-center space-x-2 text-slate-300">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          <span>AEGIS SENTIENCE ENGINE — LOCAL ZERO-TRUST DISCONNECTED EXECUTION MATRIX</span>
        </div>
        <div className="flex items-center space-x-3 text-slate-400 mt-1 sm:mt-0 font-mono">
          <span>THROTTLE: <strong className="text-cyan-300">{telemetry.throttlingDelaySeconds}s</strong></span>
          <span>•</span>
          <span>LATENCY TARGET: <strong className="text-emerald-300">&lt; 50.0 μs</strong></span>
        </div>
      </div>

      {/* Grid: Matches 4 windows from gui_dashboard.py */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* WINDOW 1: SYSTEM TELEMETRY (Left Top) */}
        <div className="lg:col-span-4 bg-slate-950 border border-blue-900/70 rounded shadow-sm relative overflow-hidden flex flex-col justify-between">
          <div className="border-b border-blue-900/60 px-3 py-2 bg-slate-900/40 flex items-center justify-between">
            <span className="text-xs font-bold tracking-wider text-blue-400 uppercase flex items-center space-x-1.5">
              <Activity className="w-3.5 h-3.5" />
              <span>SYSTEM TELEMETRY</span>
            </span>
            <span className="text-[10px] text-slate-400 font-mono">LIVE /SYS</span>
          </div>

          <div className="p-4 space-y-4">
            {/* CPU Load */}
            <div>
              <div className="flex justify-between items-center text-xs mb-1">
                <span className="text-slate-300 flex items-center space-x-1">
                  <Cpu className="w-3.5 h-3.5 text-cyan-400" />
                  <span>CPU Load</span>
                </span>
                <span className="text-emerald-400 font-bold font-mono text-sm">
                  {telemetry.cpuLoad}%
                </span>
              </div>
              <div className="w-full bg-slate-900 h-2 rounded-sm overflow-hidden border border-slate-800">
                <div 
                  className="bg-emerald-500 h-full transition-all duration-300"
                  style={{ width: `${Math.min(100, telemetry.cpuLoad)}%` }}
                />
              </div>
            </div>

            {/* Memory Usage */}
            <div>
              <div className="flex justify-between items-center text-xs mb-1">
                <span className="text-slate-300 flex items-center space-x-1">
                  <HardDrive className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Memory Usage</span>
                </span>
                <span className="text-emerald-400 font-bold font-mono">
                  {telemetry.memoryUsedGb} GB / {telemetry.memoryTotalGb} GB
                </span>
              </div>
              <div className="w-full bg-slate-900 h-2 rounded-sm overflow-hidden border border-slate-800">
                <div 
                  className="bg-cyan-500 h-full transition-all duration-300"
                  style={{ width: `${(telemetry.memoryUsedGb / telemetry.memoryTotalGb) * 100}%` }}
                />
              </div>
            </div>

            {/* GPU Temp */}
            <div className="flex justify-between items-center text-xs border-t border-slate-900 pt-2">
              <span className="text-slate-300 flex items-center space-x-1">
                <Thermometer className="w-3.5 h-3.5 text-cyan-400" />
                <span>GPU Temp</span>
              </span>
              <span className="text-emerald-400 font-bold font-mono text-sm">
                {telemetry.gpuTempC}°C
              </span>
            </div>

            {/* Battery & Power Source */}
            <div className="border-t border-slate-900 pt-2 space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-300 flex items-center space-x-1">
                  <BatteryCharging className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Battery</span>
                </span>
                <span className="text-emerald-400 font-bold font-mono text-sm">
                  {telemetry.batteryPercentage}%
                </span>
              </div>

              {/* Simulation Controls for Power States */}
              <div className="pt-1">
                <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1">Power State Simulation:</div>
                <div className="grid grid-cols-3 gap-1">
                  {[
                    { label: 'AC Plugged', pct: 95, status: 'AC_POWERED' as const },
                    { label: 'Discharging', pct: 45, status: 'DISCHARGING' as const },
                    { label: 'Low (<20%)', pct: 14, status: 'DISCHARGING' as const },
                  ].map((btn) => (
                    <button
                      key={btn.label}
                      onClick={() => onUpdateBattery(btn.pct, btn.status)}
                      className={`text-[10px] py-1 px-1 rounded border transition font-mono cursor-pointer ${
                        telemetry.powerStatus === btn.status && Math.abs(telemetry.batteryPercentage - btn.pct) < 15
                          ? 'bg-cyan-900/60 border-cyan-500 text-cyan-200'
                          : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      {btn.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="border-t border-blue-900/40 px-3 py-1.5 bg-slate-900/30 text-[10px] text-slate-400 flex justify-between">
            <span>REGISTER: /sys/class/power_supply/</span>
            <span className="text-emerald-400 font-mono">OK</span>
          </div>
        </div>

        {/* WINDOW 2: LOOP LATENCY TRACKING (Right Top) */}
        <div className="lg:col-span-8 bg-slate-950 border border-blue-900/70 rounded shadow-sm flex flex-col justify-between">
          <div className="border-b border-blue-900/60 px-3 py-2 bg-slate-900/40 flex items-center justify-between">
            <span className="text-xs font-bold tracking-wider text-blue-400 uppercase flex items-center space-x-1.5">
              <Gauge className="w-3.5 h-3.5" />
              <span>LOOP LATENCY TRACKING | (μs)</span>
            </span>
            <div className="flex items-center space-x-3 text-xs font-mono">
              <span className="text-slate-400">Current: <strong className="text-cyan-300">{telemetry.currentLatencyMicros.toFixed(1)} μs</strong></span>
              <span className="text-slate-500">|</span>
              <span className="text-slate-400">Avg: <strong className="text-emerald-300">{avgLatency} μs</strong></span>
              <span className="text-slate-500">|</span>
              <span className="text-slate-400">Max: <strong className="text-amber-300">{maxLatency} μs</strong></span>
              <span className="text-slate-500">|</span>
              <span className="text-slate-400">Min: <strong className="text-emerald-400">{minLatency} μs</strong></span>
            </div>
          </div>

          <div className="p-4 flex-1 flex flex-col justify-center">
            {/* Visual Vector Sparkline Graph representing Curses Sparkline */}
            <div className="h-32 w-full flex items-end gap-1 bg-slate-900/40 p-2 rounded border border-slate-800/80">
              {historySlice.map((val, idx) => {
                const normHeight = Math.max(8, Math.min(100, ((val - minVal) / range) * 100));
                const isLatest = idx === historySlice.length - 1;
                return (
                  <div
                    key={idx}
                    className="flex-1 flex flex-col items-center justify-end h-full group relative"
                  >
                    <div
                      className={`w-full rounded-t-xs transition-all duration-150 ${
                        isLatest 
                          ? 'bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.8)]' 
                          : val > 20 
                            ? 'bg-amber-400/80' 
                            : 'bg-emerald-500/80 hover:bg-emerald-400'
                      }`}
                      style={{ height: `${normHeight}%` }}
                    />
                    {/* Tooltip on hover */}
                    <div className="absolute bottom-full mb-1 hidden group-hover:block z-20 bg-slate-900 text-[10px] text-cyan-300 px-1.5 py-0.5 rounded border border-cyan-800 whitespace-nowrap font-mono">
                      {val.toFixed(1)} μs
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Sparkline ASCII representation matching curses character matrix */}
            <div className="mt-3 flex items-center justify-between text-xs text-slate-400 font-mono">
              <span className="text-[11px] text-slate-500">VECTOR STREAM:</span>
              <span className="text-emerald-400 tracking-widest text-sm overflow-hidden text-ellipsis whitespace-nowrap">
                {historySlice.map((v) => {
                  const chars = [" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"];
                  const n = Math.max(0, Math.min(1, (v - minVal) / range));
                  return chars[Math.floor(n * (chars.length - 1))];
                }).join('')}
              </span>
            </div>
          </div>

          <div className="border-t border-blue-900/40 px-3 py-2 bg-slate-900/30 flex items-center justify-between text-xs">
            <span className="text-slate-400 text-[11px]">
              C++17 Accelerator Bridge: <span className="text-emerald-400">./libkryptic_core.so</span> (Active)
            </span>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleExportJSON}
                title="Export telemetry logs & latency history JSON"
                className="flex items-center space-x-1 text-slate-300 hover:text-cyan-200 bg-slate-900 hover:bg-slate-800 border border-slate-700 px-2 py-0.5 rounded text-[11px] cursor-pointer"
              >
                <Download className="w-3 h-3 text-cyan-400" />
                <span>Export Telemetry</span>
              </button>

              <button
                onClick={onManualCycle}
                className="flex items-center space-x-1 text-cyan-300 hover:text-cyan-100 bg-cyan-950/70 hover:bg-cyan-900 border border-cyan-700/60 px-2 py-0.5 rounded text-[11px] cursor-pointer"
              >
                <Zap className="w-3 h-3" />
                <span>Step 1 Cycle</span>
              </button>
            </div>
          </div>
        </div>

        {/* WINDOW 3: LOCAL AGENCY STATUS (Left Bottom) */}
        <div className="lg:col-span-4 bg-slate-950 border border-blue-900/70 rounded shadow-sm flex flex-col justify-between">
          <div className="border-b border-blue-900/60 px-3 py-2 bg-slate-900/40 flex items-center justify-between">
            <span className="text-xs font-bold tracking-wider text-blue-400 uppercase flex items-center space-x-1.5">
              <Layers className="w-3.5 h-3.5" />
              <span>LOCAL AGENCY STATUS</span>
            </span>
            <span className="text-[10px] text-emerald-400 font-mono">DAEMON</span>
          </div>

          <div className="p-4 space-y-3.5 text-xs">
            <div className="flex justify-between items-center border-b border-slate-900 pb-2">
              <span className="text-slate-400">Agency Core</span>
              <span className="text-emerald-400 font-bold font-mono tracking-wider glow-green">
                ONLINE
              </span>
            </div>

            <div className="flex justify-between items-center border-b border-slate-900 pb-2">
              <span className="text-slate-400">Active Execution Threads</span>
              <span className="text-emerald-400 font-bold font-mono">
                {telemetry.activeThreads} (Thread-Safe Ring)
              </span>
            </div>

            <div className="flex justify-between items-center border-b border-slate-900 pb-2">
              <span className="text-slate-400">Native Loop Latency</span>
              <span className="text-emerald-400 font-bold font-mono">
                {telemetry.currentLatencyMicros.toFixed(1)} μs
              </span>
            </div>

            <div className="flex justify-between items-center border-b border-slate-900 pb-2">
              <span className="text-slate-400">Power Throttling Policy</span>
              <span className="text-cyan-400 font-mono font-bold">
                {telemetry.powerStatus === 'AC_POWERED' ? 'MINIMAL_LATENCY (0.1s)' : `POWER_PRESERVE (${telemetry.throttlingDelaySeconds}s)`}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-slate-400">State Persistence Ring</span>
              <span className="text-emerald-400 font-mono">
                agency_sentience.db [OK]
              </span>
            </div>
          </div>

          <div className="border-t border-blue-900/40 px-3 py-2 bg-slate-900/30 text-[10px] text-slate-400 flex justify-between items-center">
            <span>SELF-HEALING CONTROLLER:</span>
            <span className="text-emerald-400 font-mono font-semibold">HOMEOSTATIC</span>
          </div>
        </div>

        {/* WINDOW 4: LOG CONSOLE LOGS (Right Bottom) */}
        <div className="lg:col-span-8 bg-slate-950 border border-blue-900/70 rounded shadow-sm flex flex-col justify-between">
          <div className="border-b border-blue-900/60 px-3 py-2 bg-slate-900/40 flex flex-wrap items-center justify-between gap-2">
            <span className="text-xs font-bold tracking-wider text-blue-400 uppercase flex items-center space-x-1.5">
              <Terminal className="w-3.5 h-3.5" />
              <span>LOG CONSOLE | PERSISTENT TELEMETRY</span>
            </span>

            <div className="flex items-center space-x-2">
              {/* Filter */}
              <div className="flex items-center space-x-1 bg-slate-900 px-2 py-0.5 rounded border border-slate-800 text-[11px]">
                <Filter className="w-3 h-3 text-slate-400" />
                <select
                  value={selectedModuleFilter}
                  onChange={(e) => setSelectedModuleFilter(e.target.value)}
                  className="bg-transparent text-slate-300 focus:outline-none cursor-pointer text-[11px]"
                >
                  {modules.map((m) => (
                    <option key={m} value={m} className="bg-slate-900 text-slate-200">
                      {m}
                    </option>
                  ))}
                </select>
              </div>

              {/* Export JSON Button */}
              <button
                onClick={handleExportJSON}
                title="Export current telemetry logs and latency history as a JSON file"
                className="flex items-center space-x-1 px-2.5 py-1 text-[11px] font-mono font-semibold rounded border transition cursor-pointer bg-cyan-950/80 hover:bg-cyan-900 border-cyan-600/70 text-cyan-300 hover:text-cyan-100 shadow-xs"
              >
                {isExporting ? (
                  <>
                    <Check className="w-3 h-3 text-emerald-400" />
                    <span className="text-emerald-400">Exported</span>
                  </>
                ) : (
                  <>
                    <Download className="w-3 h-3 text-cyan-400" />
                    <span>Export JSON</span>
                  </>
                )}
              </button>

              {/* Reset to defaults */}
              <button
                onClick={onResetDefaults}
                title="Reset database to default seed logs"
                className="p-1 text-slate-400 hover:text-slate-200 rounded border border-slate-800 hover:bg-slate-900 transition cursor-pointer"
              >
                <RefreshCw className="w-3 h-3" />
              </button>

              {/* Clear */}
              <button
                onClick={onClearLogs}
                title="Clear telemetry logs"
                className="p-1 text-slate-400 hover:text-red-400 rounded border border-slate-800 hover:bg-slate-900 transition cursor-pointer"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          </div>

          {/* Logs feed list */}
          <div className="p-3 font-mono text-xs overflow-y-auto max-h-64 min-h-56 space-y-1.5">
            {filteredLogs.length === 0 ? (
              <div className="text-slate-500 italic py-6 text-center">No telemetry logs found for current filter.</div>
            ) : (
              filteredLogs.slice(0, 15).map((log) => {
                const date = new Date(log.timestamp * 1000);
                const timeStr = date.toTimeString().split(' ')[0];
                return (
                  <div
                    key={log.id}
                    className="flex items-start space-x-2 py-1 px-2 rounded hover:bg-slate-900/50 transition border border-transparent hover:border-slate-800/80"
                  >
                    <span className="text-slate-500 text-[11px] whitespace-nowrap">
                      [{timeStr}]
                    </span>
                    <span className="px-1.5 py-0.2 rounded text-[10px] font-bold tracking-wide uppercase bg-slate-900 border border-slate-700 text-cyan-400 whitespace-nowrap">
                      {log.module_name}
                    </span>
                    <span className="text-emerald-400 text-[11px] font-semibold whitespace-nowrap">
                      {log.latency_micros.toFixed(1)} μs
                    </span>
                    <span className="text-slate-300 text-[11px] flex-1 break-words">
                      {log.status_msg}
                    </span>
                  </div>
                );
              })
            )}
          </div>

          <div className="border-t border-blue-900/40 px-3 py-1.5 bg-slate-900/30 text-[10px] text-slate-400 flex justify-between">
            <span>SHOWING {Math.min(15, filteredLogs.length)} OF {filteredLogs.length} LOGS</span>
            <span className="text-slate-400">DATABASE: SQLite3 / local storage equivalent</span>
          </div>
        </div>
      </div>
    </div>
  );
};
