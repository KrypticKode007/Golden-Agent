import React, { useEffect, useState } from 'react';
import { 
  Activity, 
  Cpu, 
  Radio, 
  Sliders, 
  Zap, 
  ShieldCheck, 
  BatteryMedium,
  Clock,
  Crosshair,
  MapPin,
  Plane
} from 'lucide-react';
import { SystemTelemetryState } from '../types';

interface HeaderProps {
  telemetry: SystemTelemetryState;
  activeTab: 'flightdeck' | 'telemetry' | 'map' | 'benchmark' | 'streaming' | 'config';
  setActiveTab: (tab: 'flightdeck' | 'telemetry' | 'map' | 'benchmark' | 'streaming' | 'config') => void;
  onManualCycle: () => void;
  isRunningAutoLoop: boolean;
  toggleAutoLoop: () => void;
}

export const AegisHeader: React.FC<HeaderProps> = ({
  telemetry,
  activeTab,
  setActiveTab,
  onManualCycle,
  isRunningAutoLoop,
  toggleAutoLoop,
}) => {
  const [timeStr, setTimeStr] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toTimeString().split(' ')[0]);
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="border-b border-cyan-900/60 bg-slate-950/90 backdrop-blur sticky top-0 z-50">
      {/* Monolith Header Banner Layout from gui_dashboard.py */}
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="relative flex items-center justify-center w-8 h-8 rounded border border-emerald-500/40 bg-emerald-950/30 text-emerald-400">
              <Activity className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-base font-bold tracking-wider text-slate-100 uppercase">
                  Offline Conscious Drone <span className="text-cyan-400">|</span> Aegis Agency Dashboard
                </h1>
                <span className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] uppercase font-bold tracking-widest bg-cyan-950 text-cyan-400 border border-cyan-800 rounded">
                  v2.4-Edge
                </span>
              </div>
              <p className="text-xs text-slate-400 flex items-center space-x-2 mt-0.5">
                <span>Node: <strong className="text-slate-300">AEGIS-CORE-01</strong></span>
                <span>•</span>
                <span className="text-emerald-400">Zero-Cloud Local Isolation</span>
              </p>
            </div>
          </div>

          {/* Quick Metrics Bar */}
          <div className="flex items-center space-x-3 sm:space-x-5 text-xs">
            <div className="flex items-center space-x-1.5 text-slate-400 bg-slate-900/80 px-2.5 py-1 rounded border border-slate-800">
              <Clock className="w-3.5 h-3.5 text-cyan-400" />
              <span className="font-mono text-slate-200">{timeStr}</span>
            </div>

            <div className="flex items-center space-x-1.5 bg-slate-900/80 px-2.5 py-1 rounded border border-slate-800">
              <BatteryMedium className={`w-3.5 h-3.5 ${
                telemetry.batteryPercentage < 20 ? 'text-red-400' : 'text-emerald-400'
              }`} />
              <span className="text-slate-300 font-bold">{telemetry.batteryPercentage}%</span>
              <span className="text-[10px] text-slate-400 uppercase">({telemetry.powerStatus})</span>
            </div>

            <div className="flex items-center space-x-2 bg-slate-900/80 px-3 py-1 rounded border border-slate-800">
              <span className="text-slate-400 text-xs uppercase">Status:</span>
              <span className="inline-flex items-center px-1.5 py-0.5 text-xs font-bold rounded uppercase tracking-wider bg-emerald-950 text-emerald-400 border border-emerald-500/50 glow-green">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-ping" />
                {telemetry.coreStatus}
              </span>
            </div>

            {/* Quick Actions */}
            <div className="flex items-center space-x-2">
              <button
                onClick={onManualCycle}
                title="Execute single C++17 native acceleration cycle"
                className="flex items-center space-x-1 bg-cyan-950/80 hover:bg-cyan-900 text-cyan-300 hover:text-cyan-100 border border-cyan-700/70 px-2.5 py-1 rounded text-xs transition cursor-pointer font-semibold"
              >
                <Zap className="w-3.5 h-3.5 text-cyan-400" />
                <span>Trigger Cycle</span>
              </button>

              <button
                onClick={toggleAutoLoop}
                className={`flex items-center space-x-1 px-2.5 py-1 rounded text-xs transition cursor-pointer font-semibold border ${
                  isRunningAutoLoop
                    ? 'bg-amber-950/80 text-amber-300 border-amber-600/70 hover:bg-amber-900'
                    : 'bg-emerald-950/80 text-emerald-300 border-emerald-600/70 hover:bg-emerald-900'
                }`}
              >
                <span>{isRunningAutoLoop ? 'Pause Loop' : 'Start Loop'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex space-x-1 sm:space-x-2 mt-3 pt-2 border-t border-slate-800/80 overflow-x-auto">
          {[
            { id: 'flightdeck', label: 'Drone Flight Display (5D & 360°)', icon: Plane },
            { id: 'telemetry', label: 'Agency Mission Control', icon: Activity },
            { id: 'map', label: 'Tactical Geo Map (GPS)', icon: MapPin },
            { id: 'benchmark', label: 'Native Latency Bench', icon: Cpu },
            { id: 'streaming', label: 'Telemetry Streamer', icon: Radio },
            { id: 'config', label: 'Hardware & Calibration', icon: Sliders },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 px-3 py-1.5 text-xs font-semibold rounded border transition whitespace-nowrap cursor-pointer ${
                  isActive
                    ? 'bg-cyan-950/90 text-cyan-300 border-cyan-500/80 shadow-[0_0_12px_rgba(6,182,212,0.2)]'
                    : 'bg-slate-900/40 text-slate-400 border-transparent hover:text-slate-200 hover:bg-slate-900 hover:border-slate-800'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
