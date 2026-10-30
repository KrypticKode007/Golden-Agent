import React, { useState } from 'react';
import { Sliders, Save, RotateCcw, Shield, Check, Database, Cpu } from 'lucide-react';
import { SystemConfig } from '../types';

interface SettingsProps {
  config: SystemConfig;
  onSaveConfig: (newCfg: SystemConfig) => void;
  onResetDefaults: () => void;
}

export const SettingsConfigView: React.FC<SettingsProps> = ({
  config,
  onSaveConfig,
  onResetDefaults,
}) => {
  const [formData, setFormData] = useState<SystemConfig>({ ...config });
  const [savedNotice, setSavedNotice] = useState<boolean>(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSaveConfig(formData);
    setSavedNotice(true);
    setTimeout(() => setSavedNotice(false), 2000);
  };

  return (
    <div className="space-y-4">
      <div className="bg-slate-950 border border-blue-900/70 p-4 rounded shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div>
            <h2 className="text-sm font-bold text-slate-100 flex items-center space-x-2 uppercase tracking-wide">
              <Sliders className="w-4 h-4 text-cyan-400" />
              <span>Hardware Acceleration & Daemon Configuration</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Direct interface to <code className="text-cyan-300">config.json</code> and <code className="text-cyan-300">calibration_profile.json</code> runtime parameters.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={onResetDefaults}
              className="flex items-center space-x-1 bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 px-3 py-1.5 rounded text-xs font-semibold cursor-pointer transition"
            >
              <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
              <span>Reset to Defaults</span>
            </button>

            <button
              onClick={handleSubmit}
              className="flex items-center space-x-1.5 bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-600/70 px-4 py-1.5 rounded text-xs font-semibold cursor-pointer transition glow-green"
            >
              {savedNotice ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Save className="w-3.5 h-3.5" />}
              <span>{savedNotice ? 'Parameters Saved' : 'Save Configuration'}</span>
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="mt-4 space-y-6 text-xs font-mono">
          {/* System Group */}
          <div>
            <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
              <Cpu className="w-3.5 h-3.5" />
              <span>System Section</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-slate-900/40 p-3 rounded border border-slate-800">
              <div>
                <label className="block text-slate-400 mb-1">deployment_mode</label>
                <select
                  value={formData.deployment_mode}
                  onChange={(e) => setFormData({ ...formData, deployment_mode: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 text-slate-200 px-2.5 py-1.5 rounded focus:border-cyan-500 focus:outline-none"
                >
                  <option value="OFFLINE_LOCAL">OFFLINE_LOCAL (Zero-Cloud)</option>
                  <option value="EDGE_ADAPTIVE">EDGE_ADAPTIVE (Dynamic Throttling)</option>
                  <option value="TEST_HARNESS">TEST_HARNESS (Benchmarking)</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">loop_throttle_seconds</label>
                <input
                  type="number"
                  step="0.1"
                  min="0.1"
                  max="10.0"
                  value={formData.loop_throttle_seconds}
                  onChange={(e) => setFormData({ ...formData, loop_throttle_seconds: Number(e.target.value) })}
                  className="w-full bg-slate-950 border border-slate-700 text-slate-200 px-2.5 py-1.5 rounded focus:border-cyan-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">debug_logging</label>
                <div className="pt-1.5">
                  <label className="inline-flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.debug_logging}
                      onChange={(e) => setFormData({ ...formData, debug_logging: e.target.checked })}
                      className="rounded bg-slate-950 border-slate-700 text-cyan-500 focus:ring-0"
                    />
                    <span className="text-slate-300">Enable verbose debug stderr logs</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Hardware Bridge Group */}
          <div>
            <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
              <Shield className="w-3.5 h-3.5" />
              <span>Hardware Bridge Section (Native C++17)</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-slate-900/40 p-3 rounded border border-slate-800">
              <div>
                <label className="block text-slate-400 mb-1">library_path</label>
                <input
                  type="text"
                  value={formData.library_path}
                  onChange={(e) => setFormData({ ...formData, library_path: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 text-slate-200 px-2.5 py-1.5 rounded focus:border-cyan-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">fallback_latency_micros (μs)</label>
                <input
                  type="number"
                  step="0.1"
                  value={formData.fallback_latency_micros}
                  onChange={(e) => setFormData({ ...formData, fallback_latency_micros: Number(e.target.value) })}
                  className="w-full bg-slate-950 border border-slate-700 text-slate-200 px-2.5 py-1.5 rounded focus:border-cyan-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">max_allowed_latency_micros (μs)</label>
                <input
                  type="number"
                  step="1.0"
                  value={formData.max_allowed_latency_micros}
                  onChange={(e) => setFormData({ ...formData, max_allowed_latency_micros: Number(e.target.value) })}
                  className="w-full bg-slate-950 border border-slate-700 text-slate-200 px-2.5 py-1.5 rounded focus:border-cyan-500 focus:outline-none"
                />
              </div>
            </div>
          </div>

          {/* Database Group */}
          <div>
            <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
              <Database className="w-3.5 h-3.5" />
              <span>Database Persistence Ring</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-slate-900/40 p-3 rounded border border-slate-800">
              <div>
                <label className="block text-slate-400 mb-1">db_path</label>
                <input
                  type="text"
                  value={formData.db_path}
                  onChange={(e) => setFormData({ ...formData, db_path: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 text-slate-200 px-2.5 py-1.5 rounded focus:border-cyan-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">connection_timeout_seconds</label>
                <input
                  type="number"
                  step="0.5"
                  value={formData.connection_timeout_seconds}
                  onChange={(e) => setFormData({ ...formData, connection_timeout_seconds: Number(e.target.value) })}
                  className="w-full bg-slate-950 border border-slate-700 text-slate-200 px-2.5 py-1.5 rounded focus:border-cyan-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">max_retry_attempts</label>
                <input
                  type="number"
                  step="1"
                  value={formData.max_retry_attempts}
                  onChange={(e) => setFormData({ ...formData, max_retry_attempts: Number(e.target.value) })}
                  className="w-full bg-slate-950 border border-slate-700 text-slate-200 px-2.5 py-1.5 rounded focus:border-cyan-500 focus:outline-none"
                />
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
