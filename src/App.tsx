import React, { useState, useEffect, useCallback, useRef } from 'react';
import { AegisHeader } from './components/AegisHeader';
import { UnifiedFlightDeck } from './components/UnifiedFlightDeck';
import { TelemetryView } from './components/TelemetryView';
import { GeographicalMapView } from './components/GeographicalMapView';
import { BenchmarkView } from './components/BenchmarkView';
import { StreamingGatewayView } from './components/StreamingGatewayView';
import { SettingsConfigView } from './components/SettingsConfigView';
import { telemetryDb } from './services/telemetryStore';
import { HardwareAccelerator } from './services/hardwareAccelerator';
import { osTelemetry } from './services/osTelemetryProvider';
import { SystemTelemetryState, SystemConfig, TelemetryLog } from './types';

const DEFAULT_CONFIG: SystemConfig = {
  deployment_mode: 'OFFLINE_LOCAL',
  debug_logging: false,
  loop_throttle_seconds: 1.5,
  db_path: 'agency_sentience.db',
  connection_timeout_seconds: 5.0,
  max_retry_attempts: 3,
  library_path: './libkryptic_core.so',
  fallback_latency_micros: 14.2,
  max_allowed_latency_micros: 50.0,
};

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'flightdeck' | 'telemetry' | 'map' | 'benchmark' | 'streaming' | 'config'>('flightdeck');
  const [isRunningAutoLoop, setIsRunningAutoLoop] = useState<boolean>(true);
  const [config, setConfig] = useState<SystemConfig>(() => {
    try {
      const saved = localStorage.getItem('golden_agent_config');
      return saved ? JSON.parse(saved) : DEFAULT_CONFIG;
    } catch {
      return DEFAULT_CONFIG;
    }
  });

  const [telemetry, setTelemetry] = useState<SystemTelemetryState>({
    cpuLoad: 45.2,
    memoryUsedGb: 6.8,
    memoryTotalGb: 16.0,
    gpuTempC: 54.0,
    batteryPercentage: 88,
    powerStatus: 'AC_POWERED',
    powerSource: 'TERMUX_API',
    activeThreads: 64,
    coreStatus: 'ONLINE',
    currentLatencyMicros: 14.2,
    throttlingDelaySeconds: 1.5,
  });

  const [latencyHistory, setLatencyHistory] = useState<number[]>([
    14.2, 14.5, 13.9, 14.8, 15.1, 14.0, 13.8, 14.4, 14.7, 14.2, 14.6, 13.9, 14.1, 14.3, 14.9, 15.2, 14.1, 14.0
  ]);

  const [logs, setLogs] = useState<TelemetryLog[]>(telemetryDb.getLatestLogs(50));
  const autoLoopTimerRef = useRef<any>(null);

  // Sync logs when DB updates
  useEffect(() => {
    const unsub = telemetryDb.subscribe(() => {
      setLogs(telemetryDb.getLatestLogs(50));
    });
    return () => unsub();
  }, []);

  // Trigger single hardware execution cycle
  const triggerCycle = useCallback((logReason?: string) => {
    const tNow = Date.now() / 1000;
    const cpu = osTelemetry.getCpuLoad(tNow);
    const temp = osTelemetry.getGpuTemp(tNow, cpu);
    const battery = osTelemetry.captureBatteryTelemetry();
    const throttleDelay = osTelemetry.determineThrottlingDelay();

    // Execute hardware accelerator
    const { latencyMicros } = HardwareAccelerator.executeHardwareLoop(0);

    setTelemetry((prev) => ({
      ...prev,
      cpuLoad: cpu,
      gpuTempC: temp,
      batteryPercentage: battery.percentage,
      powerStatus: battery.status,
      currentLatencyMicros: latencyMicros,
      throttlingDelaySeconds: throttleDelay,
      coreStatus: battery.percentage < 20 ? 'THROTTLED' : 'ONLINE',
    }));

    setLatencyHistory((prev) => [...prev.slice(-60), latencyMicros]);

    // Log to DB
    telemetryDb.logMetric(
      'HARDWARE_BRIDGE',
      latencyMicros,
      logReason || 'Telemetry packet received [CHKSUM OK].'
    );
  }, []);

  // Continuous auto loop matching main_dashboard_loop
  useEffect(() => {
    if (!isRunningAutoLoop) {
      if (autoLoopTimerRef.current) clearTimeout(autoLoopTimerRef.current);
      return;
    }

    const scheduleNext = () => {
      const delay = Math.max(0.5, telemetry.throttlingDelaySeconds || config.loop_throttle_seconds) * 1000;
      autoLoopTimerRef.current = setTimeout(() => {
        triggerCycle();
        scheduleNext();
      }, delay);
    };

    scheduleNext();

    return () => {
      if (autoLoopTimerRef.current) clearTimeout(autoLoopTimerRef.current);
    };
  }, [isRunningAutoLoop, triggerCycle, telemetry.throttlingDelaySeconds, config.loop_throttle_seconds]);

  // Handle hotkeys (Q to pause/exit, 1-5 for tabs)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't intercept if user is typing in input
      if (['INPUT', 'SELECT', 'TEXTAREA'].includes((e.target as HTMLElement)?.tagName)) {
        return;
      }
      if (e.key === 'q' || e.key === 'Q') {
        setIsRunningAutoLoop((prev) => !prev);
      } else if (e.key === '1') {
        setActiveTab('flightdeck');
      } else if (e.key === '2') {
        setActiveTab('telemetry');
      } else if (e.key === '3') {
        setActiveTab('map');
      } else if (e.key === '4') {
        setActiveTab('benchmark');
      } else if (e.key === '5') {
        setActiveTab('streaming');
      } else if (e.key === '6') {
        setActiveTab('config');
      } else if (e.key === ' ') {
        e.preventDefault();
        triggerCycle('Manual spacebar telemetry cycle triggered');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [triggerCycle]);

  const handleUpdateBattery = (pct: number, status: 'AC_POWERED' | 'CHARGING' | 'DISCHARGING') => {
    osTelemetry.setPowerState(pct, status);
    triggerCycle(`Power telemetry state transition to ${status} (${pct}%)`);
  };

  const handleSaveConfig = (newCfg: SystemConfig) => {
    setConfig(newCfg);
    try {
      localStorage.setItem('golden_agent_config', JSON.stringify(newCfg));
    } catch {}
    telemetryDb.logMetric('CONFIG_MANAGER', 0.5, 'Runtime configuration updated and synced.');
  };

  const handleResetDefaults = () => {
    setConfig(DEFAULT_CONFIG);
    try {
      localStorage.removeItem('golden_agent_config');
    } catch {}
    telemetryDb.resetToDefaults();
  };

  return (
    <div className="min-h-screen bg-black text-slate-100 flex flex-col justify-between selection:bg-cyan-500 selection:text-black">
      {/* Top Header */}
      <AegisHeader
        telemetry={telemetry}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onManualCycle={() => triggerCycle('Operator manual trigger cycle')}
        isRunningAutoLoop={isRunningAutoLoop}
        toggleAutoLoop={() => setIsRunningAutoLoop((v) => !v)}
      />

      {/* Main View Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4">
        {activeTab === 'flightdeck' && (
          <UnifiedFlightDeck
            currentLatencyMicros={telemetry.currentLatencyMicros}
            batteryPct={telemetry.batteryPercentage}
          />
        )}

        {activeTab === 'telemetry' && (
          <TelemetryView
            telemetry={telemetry}
            latencyHistory={latencyHistory}
            logs={logs}
            onManualCycle={() => triggerCycle('Operator step cycle')}
            onClearLogs={() => telemetryDb.clearLogs()}
            onResetDefaults={() => telemetryDb.resetToDefaults()}
            onUpdateBattery={handleUpdateBattery}
          />
        )}

        {activeTab === 'map' && <GeographicalMapView />}

        {activeTab === 'benchmark' && <BenchmarkView />}

        {activeTab === 'streaming' && <StreamingGatewayView />}

        {activeTab === 'config' && (
          <SettingsConfigView
            config={config}
            onSaveConfig={handleSaveConfig}
            onResetDefaults={handleResetDefaults}
          />
        )}
      </main>

      {/* Bottom Navigation Grid Bar from gui_dashboard.py lines 164-170 */}
      <footer className="border-t border-cyan-900/60 bg-slate-950 px-4 py-2 text-xs font-mono">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3 text-slate-400">
          <div className="flex items-center space-x-2 text-emerald-400 font-bold">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>NAVI-TRACK 07B | OFFLINE MODE</span>
            <span className="text-slate-600 font-normal">|</span>
            <span className="text-slate-400 font-normal hidden sm:inline">Contested Local Execution Environment</span>
          </div>

          <div className="flex items-center space-x-4 text-[11px]">
            <span className="hidden md:inline text-slate-500">
              Hotkeys: <span className="text-cyan-400">[1-6]</span> Tabs | <span className="text-cyan-400">[Space]</span> Cycle | <span className="text-cyan-400">[Q]</span> Toggle Loop
            </span>
            <span className="text-slate-400">
              Press <strong className="text-cyan-300">'Q'</strong> to {isRunningAutoLoop ? 'Pause' : 'Resume'} Canvas
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
