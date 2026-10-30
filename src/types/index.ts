export interface TelemetryLog {
  id: number;
  timestamp: number;
  module_name: string;
  latency_micros: number;
  status_msg: string;
}

export interface SystemTelemetryState {
  cpuLoad: number; // percentage (e.g. 45.2%)
  memoryUsedGb: number; // e.g. 6.8
  memoryTotalGb: number; // 16.0
  gpuTempC: number; // e.g. 54
  batteryPercentage: number; // 0-100
  powerStatus: 'AC_POWERED' | 'CHARGING' | 'DISCHARGING';
  powerSource: 'TERMUX_API' | 'SYSTEM_FALLBACK' | 'HARDWARE_REGISTER';
  activeThreads: number;
  coreStatus: 'ONLINE' | 'THROTTLED' | 'ADAPTIVE' | 'BENCHMARKING';
  currentLatencyMicros: number;
  throttlingDelaySeconds: number;
}

export interface CalibrationProfile {
  name: string;
  matrix_loop_bounds: number;
  collection_interval_seconds: number;
  enforce_strict_memory_isolation: boolean;
}

export interface SystemConfig {
  deployment_mode: string;
  debug_logging: boolean;
  loop_throttle_seconds: number;
  db_path: string;
  connection_timeout_seconds: number;
  max_retry_attempts: number;
  library_path: string;
  fallback_latency_micros: number;
  max_allowed_latency_micros: number;
}

export interface StreamFrame {
  id: string;
  node_id: string;
  timestamp: number;
  system_state: string;
  matrix_compute_latency_ms: number;
  security_epoch_valid: boolean;
  packet_signature: string;
  tx_status: 'SUCCESS' | 'REFUSED' | 'PENDING';
}

export interface BenchmarkResult {
  tick: number;
  computedLatencyMicros: number;
  startMemoryMb: number;
  endMemoryMb: number;
  varianceDeltaMb: number;
  timestamp: number;
}
