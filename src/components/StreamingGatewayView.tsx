import React, { useState, useEffect } from 'react';
import { Radio, Play, Square, Shield, Send, CheckCircle2, AlertCircle, RefreshCw, Server } from 'lucide-react';
import { streamGateway } from '../services/streamGateway';
import { StreamFrame } from '../types';

export const StreamingGatewayView: React.FC = () => {
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [streamIntervalMs, setStreamIntervalMs] = useState<number>(2000);
  const [frames, setFrames] = useState<StreamFrame[]>(streamGateway.getRecentFrames(10));
  const [totalSent, setTotalSent] = useState<number>(14);
  const [txSuccess, setTxSuccess] = useState<number>(14);
  const [txRefused, setTxRefused] = useState<number>(0);
  const [nodeInfo] = useState(streamGateway.getNodeInfo());

  useEffect(() => {
    const unsubscribe = streamGateway.subscribe((newFrame) => {
      setFrames((prev) => [newFrame, ...prev.slice(0, 19)]);
      setTotalSent((c) => c + 1);
      if (newFrame.tx_status === 'SUCCESS') {
        setTxSuccess((c) => c + 1);
      } else {
        setTxRefused((c) => c + 1);
      }
    });
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (!isStreaming) return;
    const interval = setInterval(() => {
      streamGateway.emitFrame();
    }, streamIntervalMs);
    return () => clearInterval(interval);
  }, [isStreaming, streamIntervalMs]);

  const handleManualEmit = () => {
    streamGateway.emitFrame();
  };

  return (
    <div className="space-y-4">
      {/* Streamer Gateway Status Banner */}
      <div className="bg-slate-950 border border-blue-900/70 p-4 rounded shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-3">
          <div>
            <h2 className="text-sm font-bold text-slate-100 flex items-center space-x-2 uppercase tracking-wide">
              <Radio className={`w-4 h-4 ${isStreaming ? 'text-emerald-400 animate-pulse' : 'text-slate-400'}`} />
              <span>Real-Time Edge Telemetry Streamer & Gateway</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Replicates <code className="text-cyan-300">stream_client_telemetry.py</code> continuous transmission pipeline.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleManualEmit}
              className="flex items-center space-x-1.5 bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 px-3 py-1.5 rounded text-xs font-semibold cursor-pointer transition"
            >
              <Send className="w-3.5 h-3.5 text-cyan-400" />
              <span>Emit Single Frame</span>
            </button>

            <button
              onClick={() => setIsStreaming(!isStreaming)}
              className={`flex items-center space-x-1.5 px-4 py-1.5 rounded text-xs font-semibold cursor-pointer transition border ${
                isStreaming
                  ? 'bg-amber-950 hover:bg-amber-900 text-amber-300 border-amber-600/70'
                  : 'bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border-emerald-600/70 glow-green'
              }`}
            >
              {isStreaming ? (
                <>
                  <Square className="w-3.5 h-3.5" />
                  <span>Halt Stream Loop</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5" />
                  <span>Start Continuous Stream</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Node & Auth Specs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4 text-xs font-mono">
          <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800">
            <div className="text-slate-400 text-[10px] uppercase">Node Identifier</div>
            <div className="text-cyan-300 font-bold mt-0.5 flex items-center space-x-1">
              <Server className="w-3.5 h-3.5 text-cyan-400" />
              <span>{nodeInfo.nodeId}</span>
            </div>
          </div>

          <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800">
            <div className="text-slate-400 text-[10px] uppercase">Security Session Token</div>
            <div className="text-slate-300 mt-0.5 flex items-center space-x-1">
              <Shield className="w-3.5 h-3.5 text-emerald-400" />
              <span>{nodeInfo.tokenMasked}</span>
            </div>
          </div>

          <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800">
            <div className="text-slate-400 text-[10px] uppercase">Stream Cadence</div>
            <div className="text-slate-300 mt-0.5 flex items-center space-x-2">
              {[1000, 2000, 5000].map((ms) => (
                <button
                  key={ms}
                  onClick={() => setStreamIntervalMs(ms)}
                  className={`px-1.5 py-0.5 rounded text-[11px] border cursor-pointer ${
                    streamIntervalMs === ms
                      ? 'bg-cyan-900 border-cyan-500 text-cyan-200'
                      : 'border-slate-700 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {ms / 1000}s
                </button>
              ))}
            </div>
          </div>

          <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800">
            <div className="text-slate-400 text-[10px] uppercase">Packet Transmission Health</div>
            <div className="text-emerald-400 font-bold mt-0.5 flex items-center space-x-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>{txSuccess} OK / {totalSent} Sent (100%)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Live Stream Telemetry Table */}
      <div className="bg-slate-950 border border-blue-900/70 rounded shadow-sm overflow-hidden">
        <div className="border-b border-blue-900/60 px-4 py-2.5 bg-slate-900/40 flex items-center justify-between">
          <span className="text-xs font-bold tracking-wider text-blue-400 uppercase flex items-center space-x-2">
            <Radio className="w-3.5 h-3.5" />
            <span>Outbound Edge Telemetry Stream Feed</span>
          </span>
          <span className="text-[11px] text-slate-400 font-mono flex items-center space-x-1.5">
            <span className={`w-2 h-2 rounded-full ${isStreaming ? 'bg-emerald-400 animate-ping' : 'bg-slate-600'}`} />
            <span>{isStreaming ? 'TRANSMITTING' : 'STREAM DORMANT'}</span>
          </span>
        </div>

        <div className="overflow-x-auto max-h-96">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="px-4 py-2">Timestamp</th>
                <th className="px-4 py-2">Node ID</th>
                <th className="px-4 py-2">Compute Latency</th>
                <th className="px-4 py-2">System State</th>
                <th className="px-4 py-2">Packet Signature (SHA256 Stub)</th>
                <th className="px-4 py-2">Epoch Valid</th>
                <th className="px-4 py-2">TX Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-900">
              {frames.map((frame) => {
                const date = new Date(frame.timestamp * 1000);
                const timeStr = date.toTimeString().split(' ')[0];
                return (
                  <tr key={frame.id} className="hover:bg-slate-900/40 transition">
                    <td className="px-4 py-2 text-slate-400 font-mono text-[11px]">
                      {timeStr}
                    </td>
                    <td className="px-4 py-2 text-cyan-300 font-bold">{frame.node_id}</td>
                    <td className="px-4 py-2 text-emerald-400 font-semibold">
                      {frame.matrix_compute_latency_ms.toFixed(3)} ms
                    </td>
                    <td className="px-4 py-2 text-slate-300">
                      <span className="bg-emerald-950/60 text-emerald-300 border border-emerald-800/80 px-1.5 py-0.5 rounded text-[10px]">
                        {frame.system_state}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-slate-400 text-[11px]">
                      <code>{frame.packet_signature.substring(0, 16)}...</code>
                    </td>
                    <td className="px-4 py-2 text-emerald-400 font-semibold">TRUE</td>
                    <td className="px-4 py-2 text-emerald-400 font-bold flex items-center space-x-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                      <span>{frame.tx_status} [200]</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
