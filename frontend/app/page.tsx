'use client'

import { useEffect, useState, useRef } from 'react'
import Map from '@/components/Map'
import MetricCard from '@/components/MetricCard'
import Loading from '@/components/Loading'
import { fetchStatus, setupWebSocket, triggerScenario } from '@/lib/api'

interface AlertItem {
  type: string
  severity: 'high' | 'medium' | 'low'
  facility_id?: string
  zone?: string
  warehouse?: string
}

interface TrafficItem {
  _id: string
  avg_speed: number
  avg_congestion: number
}

interface DashboardData {
  traffic?: TrafficItem[]
  hospitals?: any[]
  supply?: any[]
  alerts?: AlertItem[]
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeScenario, setActiveScenario] = useState<string | null>(null)
  const [logs, setLogs] = useState<string[]>(['[SYS] Secure connection established...', '[SYS] Awaiting command overrides...'])
  const logsEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchStatus().then(res => {
      setData(res)
      setLoading(false)
    }).catch(console.error)

    const interval = setInterval(() => {
      fetchStatus().then(setData).catch(console.error)
    }, 5000)

    const ws = setupWebSocket((message) => {
      if (message.type === 'status_update') {
        setData(message.data)
      }
    })

    return () => {
      clearInterval(interval)
      ws?.close()
    }
  }, [])

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs, data?.alerts])

  const handleTriggerDisaster = async () => {
    try {
      setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] [WARN] COMMAND: INITIALIZING DISASTER ROUTINE...`])
      await triggerScenario('earthquake')
      setActiveScenario('earthquake')
      setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] [CRITICAL] SIMULATION STARTED: EARTHQUAKE IN PROGRESS`])
    } catch (e) {
      setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] [ERR] Failed to initiate simulation protocols.`])
    }
  }

  if (loading) return <Loading />

  return (
    <div className="min-h-screen w-full p-4 md:p-8 font-sans flex flex-col gap-8 relative z-0">
      
      {/* Background Decorators */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-blue-900/20 blur-[120px] pointer-events-none -z-10" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-cyan-900/20 blur-[120px] pointer-events-none -z-10" />

      {/* Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="relative">
          <div className="absolute -inset-1 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 opacity-20 blur-lg pointer-events-none" />
          <h1 className="relative text-4xl md:text-5xl font-extrabold bg-gradient-to-r from-blue-300 via-cyan-300 to-indigo-300 bg-clip-text text-transparent drop-shadow-[0_0_10px_rgba(56,189,248,0.5)]">
            CITY COMMAND CENTER
          </h1>
          <p className="text-sky-200/60 mt-2 text-xs md:text-sm tracking-[0.3em] font-mono uppercase font-bold flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse shadow-[0_0_8px_#4ade80]" />
            Real-time Telemetry Live
          </p>
        </div>
        <div className="flex items-center gap-6">
          {activeScenario && (
            <div className="glass-panel px-6 py-3 rounded-xl border border-red-500/50 flex items-center gap-3">
               <span className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
               <span className="font-bold text-red-400 text-sm tracking-widest uppercase text-shadow-sm shadow-red-500/50">ACTIVE: {activeScenario}</span>
            </div>
          )}
          <button
            onClick={handleTriggerDisaster}
            className="group relative px-10 py-4 bg-gradient-to-br from-red-600 to-rose-900 text-white font-black tracking-widest rounded-xl overflow-hidden transition-all active:scale-95 border border-red-500/50 shadow-[0_0_30px_rgba(220,38,38,0.3)] hover:shadow-[0_0_50px_rgba(220,38,38,0.6)]"
          >
            <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-20 mix-blend-overlay" />
            <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 -translate-x-[150%] group-hover:animate-[shimmer_1.5s_infinite] skew-x-12" />
            <span className="relative z-10 flex items-center gap-2 text-shadow-lg shadow-black/50">
              <svg className="w-5 h-5 text-red-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
              TRIGGER DISASTER
            </span>
          </button>
        </div>
      </header>

      {/* Main Map Area */}
      <div className="w-full glass-panel flex flex-col p-6 rounded-3xl shadow-2xl relative min-h-[600px] border border-slate-700/50">
        {/* Decorative corner brackets */}
        <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-cyan-500/50 rounded-tl-3xl z-10" />
        <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-cyan-500/50 rounded-tr-3xl z-10" />
        <div className="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-cyan-500/50 rounded-bl-3xl z-10" />
        <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-cyan-500/50 rounded-br-3xl z-10" />

        <div className="flex-1 w-full rounded-2xl overflow-hidden relative z-0 shadow-inner bg-slate-950">
          <Map trafficData={data?.traffic ?? []} />
        </div>
      </div>

      {/* Bottom Layout: Sidebar | Metrics | Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Sidebar (Alerts) */}
        <div className="card flex flex-col h-[450px]">
          <h2 className="text-lg font-bold mb-5 flex items-center justify-between border-b border-slate-700/50 pb-3">
            <div className="flex items-center gap-3 text-slate-200">
              <span className="w-2 h-2 rounded-full bg-yellow-400 shadow-[0_0_10px_#facc15]" />
              <span className="tracking-widest">ACTIVE ALERTS</span>
            </div>
            {data?.alerts && data.alerts.length > 0 && (
              <span className="bg-red-500/10 border border-red-500/50 text-red-400 text-xs px-3 py-1 rounded-full font-bold shadow-[0_0_10px_rgba(239,68,68,0.2)]">
                {data.alerts.length} CRITICAL
              </span>
            )}
          </h2>
          <div className="flex-1 overflow-y-auto pr-2 space-y-4 custom-scrollbar">
            {data?.alerts && data.alerts.length > 0 ? (
              data.alerts.map((alert, idx) => (
                <div
                  key={idx}
                  className={`p-5 rounded-2xl border ${
                    alert.severity === 'high'
                      ? 'bg-red-950/40 border-red-500/50 shadow-[0_4px_20px_rgba(239,68,68,0.15)] text-red-50'
                      : alert.severity === 'medium'
                      ? 'bg-yellow-950/40 border-yellow-500/50 shadow-[0_4px_20px_rgba(234,179,8,0.15)] text-yellow-50'
                      : 'bg-blue-950/40 border-blue-500/50 shadow-[0_4px_20px_rgba(59,130,246,0.15)] text-blue-50'
                  } transition-transform hover:-translate-y-1 cursor-default relative overflow-hidden`}
                >
                  {/* Subtle shine effect on cards */}
                  <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
                  
                  <div className="flex justify-between items-start mb-2 relative z-10">
                    <p className="font-bold text-sm tracking-wider flex items-center gap-2 drop-shadow-md">
                      {alert.severity === 'high' && <span className="text-red-400">⚠️</span>}
                      {alert.type}
                    </p>
                    <span className={`text-[9px] px-2 py-1 rounded tracking-wider font-bold uppercase ${
                      alert.severity === 'high' ? 'bg-red-500/20 text-red-300 border border-red-500/30' : 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30'
                    }`}>
                      LVL: {alert.severity}
                    </span>
                  </div>
                  <p className="opacity-70 text-xs font-mono mt-3 flex items-center gap-2 relative z-10">
                    <svg className="w-3 h-3 opacity-50" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" /></svg>
                    {alert.facility_id || alert.zone || alert.warehouse || 'UNKNOWN'}
                  </p>
                </div>
              ))
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-500/60">
                <div className="w-16 h-16 rounded-full border border-slate-700 flex items-center justify-center mb-4">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                </div>
                <p className="font-mono text-sm tracking-widest uppercase">No active alerts</p>
                <p className="text-xs mt-2 opacity-50">Grid is secure</p>
              </div>
            )}
          </div>
        </div>

        {/* Metrics Cards */}
        <div className="card flex flex-col h-[450px]">
          <h2 className="text-lg font-bold mb-5 flex items-center gap-3 border-b border-slate-700/50 pb-3 text-slate-200">
            <span className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_10px_#22d3ee]" />
            <span className="tracking-widest">SYSTEM METRICS</span>
          </h2>
          <div className="flex-1 overflow-y-auto pr-2 space-y-5 custom-scrollbar">
            <MetricCard 
              icon="⚠️" 
              title="Total Critical Nodes" 
              value={data?.alerts?.length.toString() || "0"} 
              subValue="Nodes requiring immediate attention" 
              status={data?.alerts && data.alerts.length > 0 ? 'critical' : 'normal'} 
            />
            <MetricCard 
              icon="⚡" 
              title="Grid Health" 
              value={data?.alerts && data.alerts.length > 0 ? `${Math.max(10, 100 - data.alerts.length * 5)}%` : "100%"} 
              subValue="Overall system operational capacity" 
              status={data?.alerts && data.alerts.length > 5 ? 'critical' : data?.alerts && data.alerts.length > 0 ? 'warning' : 'normal'} 
            />
            <MetricCard 
              icon="🏥" 
              title="Active Hospitals" 
              value={data?.hospitals?.length?.toString() || "4"} 
              subValue="Facilities accepting patients right now" 
              status={data?.hospitals?.length === 0 ? 'critical' : 'normal'} 
            />
          </div>
        </div>

        {/* Logs */}
        <div className="glass-panel rounded-3xl p-6 shadow-2xl flex flex-col h-[450px] relative overflow-hidden border border-slate-700/50 bg-[#0a0a0a]/80 backdrop-blur-2xl">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-400 to-teal-600 opacity-60" />
          <h2 className="text-lg font-bold mb-5 flex items-center gap-3 border-b border-slate-800 pb-3 text-emerald-400 font-mono tracking-widest">
            <span className="animate-pulse shadow-[0_0_8px_#34d399] w-2 h-2 bg-emerald-400" />
            SYS_LOGS //>
          </h2>
          <div className="flex-1 overflow-y-auto font-mono text-[11px] md:text-xs space-y-2 text-emerald-500/80 pr-2 custom-scrollbar">
            {logs.map((log, i) => (
              <p key={i} className={`leading-relaxed opacity-90 transition-opacity hover:opacity-100 p-1.5 rounded ${log.includes('CRITICAL') || log.includes('ERR') || log.includes('COMMAND:') ? 'text-rose-400 bg-rose-950/20' : 'hover:bg-emerald-950/30'}`}>
                <span className="opacity-50 mr-2">{'>'}</span>{log}
              </p>
            ))}
            {data?.alerts?.map((a, i) => (
              <p key={`alert-${i}`} className="leading-relaxed text-rose-400 font-bold bg-rose-950/20 p-1.5 rounded">
                <span className="opacity-50 mr-2">{'>'}</span>[{new Date().toLocaleTimeString()}] ALERT_DETECTION_SYS: {a.type.toUpperCase()} @ {a.facility_id || a.zone || a.warehouse}
              </p>
            ))}
            <div ref={logsEndRef} className="h-4" />
          </div>
        </div>

      </div>
    </div>
  )
}