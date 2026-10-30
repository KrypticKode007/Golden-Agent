import { StreamFrame } from '../types';

export class StreamClientGateway {
  private nodeId: string = 'EXTERNAL_CLIENT_NODE_SF_09';
  private secureToken: string = 'kryptic_token_session_prod_alpha_007';
  private frames: StreamFrame[] = [];
  private listeners: Array<(frame: StreamFrame) => void> = [];

  constructor() {
    // Generate initial frames
    for (let i = 4; i >= 0; i--) {
      this.frames.push(this.generateFrame(Date.now() - i * 2000));
    }
  }

  public subscribe(listener: (frame: StreamFrame) => void) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== listener);
    };
  }

  public getRecentFrames(limit: number = 10): StreamFrame[] {
    return this.frames.slice(0, limit);
  }

  private generateFrame(customTimestamp?: number): StreamFrame {
    const timestamp = customTimestamp || Date.now();
    const latency = Number((0.39 + Math.random() * 0.06).toFixed(3));
    
    // Hash simulation
    const hashSeed = `${this.nodeId}-${timestamp}-${latency}`;
    let hash = 0;
    for (let i = 0; i < hashSeed.length; i++) {
      hash = (hash << 5) - hash + hashSeed.charCodeAt(i);
      hash |= 0;
    }
    const signature = Math.abs(hash).toString(16).padStart(16, 'a') + '8bf942e1';

    return {
      id: Math.random().toString(36).substring(2, 9),
      node_id: this.nodeId,
      timestamp: timestamp / 1000,
      system_state: 'HOMEOSTATIC_HEALTHY',
      matrix_compute_latency_ms: latency,
      security_epoch_valid: true,
      packet_signature: signature,
      tx_status: 'SUCCESS',
    };
  }

  public emitFrame(): StreamFrame {
    const frame = this.generateFrame();
    this.frames.unshift(frame);
    if (this.frames.length > 50) {
      this.frames.pop();
    }
    this.listeners.forEach((l) => l(frame));
    return frame;
  }

  public getNodeInfo() {
    return {
      nodeId: this.nodeId,
      tokenMasked: this.secureToken.substring(0, 14) + '...' + this.secureToken.slice(-4),
      endpointUrl: 'http://localhost:8000/api/v1/secure-stream',
    };
  }
}

export const streamGateway = new StreamClientGateway();
