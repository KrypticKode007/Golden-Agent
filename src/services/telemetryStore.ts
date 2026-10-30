import { TelemetryLog } from '../types';

const STORAGE_KEY = 'golden_agent_telemetry_db';
const MAX_STORED_LOGS = 300;

// Seed initial log entries matching robotic_database_core.py telemetry logs
const initialSeedLogs: TelemetryLog[] = [
  {
    id: 1,
    timestamp: Date.now() / 1000 - 36,
    module_name: 'HARDWARE_BRIDGE',
    latency_micros: 14.2,
    status_msg: 'Telemetry packet received [CHKSUM OK]. Native link active.',
  },
  {
    id: 2,
    timestamp: Date.now() / 1000 - 28,
    module_name: 'POWER_DAEMON',
    latency_micros: 2.1,
    status_msg: 'Battery telemetry evaluated: 88% AC_POWERED, no loop throttle.',
  },
  {
    id: 3,
    timestamp: Date.now() / 1000 - 20,
    module_name: 'HARDWARE_BRIDGE',
    latency_micros: 13.9,
    status_msg: 'Matrix accumulator cycle evaluated: bounds=5000 [CHKSUM OK].',
  },
  {
    id: 4,
    timestamp: Date.now() / 1000 - 15,
    module_name: 'SENTIENCE_CORE',
    latency_micros: 0.8,
    status_msg: 'Homeostatic state check: STABLE (temp=54°C, vCore=1.12V).',
  },
  {
    id: 5,
    timestamp: Date.now() / 1000 - 9,
    module_name: 'HARDWARE_BRIDGE',
    latency_micros: 14.6,
    status_msg: 'Telemetry packet received [CHKSUM OK].',
  },
  {
    id: 6,
    timestamp: Date.now() / 1000 - 3,
    module_name: 'SECURITY_CRYPTO',
    latency_micros: 1.4,
    status_msg: 'Persistence ring verified with SHA256 integrity check.',
  },
];

class TelemetryDatabase {
  private logs: TelemetryLog[] = [];
  private nextId: number = 7;
  private listeners: Array<() => void> = [];

  constructor() {
    this.loadFromStorage();
  }

  private loadFromStorage() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        this.logs = JSON.parse(saved);
        if (this.logs.length > 0) {
          this.nextId = Math.max(...this.logs.map((l) => l.id)) + 1;
        }
      } else {
        this.logs = [...initialSeedLogs];
        this.persist();
      }
    } catch {
      this.logs = [...initialSeedLogs];
    }
  }

  private persist() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.logs));
    } catch {
      // Storage quota or privacy restriction
    }
    this.notify();
  }

  public subscribe(listener: () => void) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== listener);
    };
  }

  private notify() {
    this.listeners.forEach((cb) => cb());
  }

  public logMetric(module_name: string, latency_micros: number, status_msg: string): TelemetryLog {
    const entry: TelemetryLog = {
      id: this.nextId++,
      timestamp: Date.now() / 1000,
      module_name,
      latency_micros: Number(latency_micros.toFixed(2)),
      status_msg,
    };

    this.logs.unshift(entry);
    if (this.logs.length > MAX_STORED_LOGS) {
      this.logs = this.logs.slice(0, MAX_STORED_LOGS);
    }
    this.persist();
    return entry;
  }

  public getLatestLogs(limit: number = 20): TelemetryLog[] {
    return this.logs.slice(0, limit);
  }

  public getAllLogs(): TelemetryLog[] {
    return [...this.logs];
  }

  public clearLogs() {
    this.logs = [];
    this.persist();
  }

  public resetToDefaults() {
    this.logs = [...initialSeedLogs];
    this.persist();
  }
}

export const telemetryDb = new TelemetryDatabase();
