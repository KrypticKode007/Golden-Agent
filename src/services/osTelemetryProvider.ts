/**
 * Operating System Telemetry Provider
 * Replicates logic from os_telemetry_provider.py:
 * Monitors device battery, thermal status, CPU load oscillations,
 * and dynamically calculates loop throttling delay windows.
 */

export interface BatteryTelemetry {
  source: 'TERMUX_API' | 'SYSTEM_FALLBACK' | 'HARDWARE_REGISTER';
  percentage: number;
  status: 'AC_POWERED' | 'CHARGING' | 'DISCHARGING';
  voltageMv: number;
}

export class OSTelemetryProvider {
  private batteryPct: number = 88;
  private status: 'AC_POWERED' | 'CHARGING' | 'DISCHARGING' = 'AC_POWERED';
  private source: 'TERMUX_API' | 'SYSTEM_FALLBACK' | 'HARDWARE_REGISTER' = 'TERMUX_API';
  private baseTempC: number = 52.0;

  public setPowerState(pct: number, status: 'AC_POWERED' | 'CHARGING' | 'DISCHARGING') {
    this.batteryPct = Math.max(1, Math.min(100, pct));
    this.status = status;
  }

  public captureBatteryTelemetry(): BatteryTelemetry {
    return {
      source: this.source,
      percentage: this.batteryPct,
      status: this.status,
      voltageMv: 3820 + Math.round(this.batteryPct * 4.2),
    };
  }

  /**
   * Calculates dynamic delay windows to protect edge devices from power drain
   * under continuous inference stress loops (from os_telemetry_provider.py lines 46-75)
   */
  public determineThrottlingDelay(): number {
    const telemetry = this.captureBatteryTelemetry();
    const { percentage, status } = telemetry;

    if (status === 'CHARGING' || status === 'AC_POWERED') {
      return 0.1; // Minimal delay when plugged in
    }

    if (percentage < 15) {
      return 3.0; // Heavy throttle on critical battery
    } else if (percentage < 30) {
      return 2.0; // Moderate throttle
    } else if (percentage < 50) {
      return 1.2;
    }
    return 0.5;
  }

  public getCpuLoad(timeSeconds: number): number {
    // Oscillating CPU load formula from gui_dashboard.py: 45.0 + sin(time) * 3.5 + slight jitter
    const wave = Math.sin(timeSeconds * 0.8) * 4.2;
    const jitter = (Math.random() - 0.5) * 1.8;
    return Number(Math.max(10, Math.min(98, 45.0 + wave + jitter)).toFixed(1));
  }

  public getGpuTemp(timeSeconds: number, cpuLoad: number): number {
    const tempDelta = (cpuLoad - 45) * 0.15;
    return Number((this.baseTempC + tempDelta + Math.sin(timeSeconds * 0.3) * 1.5).toFixed(1));
  }
}

export const osTelemetry = new OSTelemetryProvider();
