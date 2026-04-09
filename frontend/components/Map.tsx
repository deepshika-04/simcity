'use client'

import React, { useMemo } from 'react'
import { Map as MapGL, Marker } from 'react-map-gl/maplibre'
import 'maplibre-gl/dist/maplibre-gl.css'

interface TrafficData {
  _id: string
  avg_speed: number
  avg_congestion: number
}

interface MapProps {
  trafficData: TrafficData[]
}

export default function Map({ trafficData }: MapProps) {
  // Map tactical zones to actual NYC geocoordinates
  const nodes = useMemo(() => {
    const baseNodes = [
      { id: 'Sector Alpha', lon: -73.985, lat: 40.758, congestion: 0.2 },
      { id: 'Sector Bravo', lon: -74.006, lat: 40.712, congestion: 0.4 },
      { id: 'Sector Charlie', lon: -73.977, lat: 40.761, congestion: 0.1 },
      { id: 'Sector Delta', lon: -74.015, lat: 40.705, congestion: 0.6 },
    ]

    const activeNodes = trafficData.map((d, i) => {
      // Deterministic offset within ~5km of NYC center
      const lonOffset = -0.04 + ((i * 37) % 80) / 1000
      const latOffset = -0.04 + ((i * 23) % 80) / 1000
      return {
        id: `Zone ${d._id}`,
        lon: -74.0060 + lonOffset,
        lat: 40.7128 + latOffset,
        congestion: d.avg_congestion || 0
      }
    })

    return activeNodes.length > 0 ? activeNodes : baseNodes
  }, [trafficData])

  return (
    <div className="absolute inset-0 overflow-hidden group rounded-xl border border-sky-900/30">
      
      {/* MapLibre 3D Map */}
      <MapGL
        initialViewState={{
          longitude: -74.0060,
          latitude: 40.7128,
          zoom: 12.5,
          pitch: 60,
          bearing: -20
        }}
        mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
        style={{ width: '100%', height: '100%', position: 'absolute', inset: 0 }}
        attributionControl={false}
      >
        {/* Map Nodes/Pings based on live data */}
        {nodes.map((node, i) => {
          let colorClass = 'bg-sky-400'
          let glowColor = 'rgba(56,189,248,0.8)'
          let pingColor = 'bg-sky-400'
          
          if (node.congestion > 0.8) {
            colorClass = 'bg-red-500'
            glowColor = 'rgba(239,68,68,0.8)'
            pingColor = 'bg-red-500'
          } else if (node.congestion > 0.5) {
            colorClass = 'bg-yellow-400'
            glowColor = 'rgba(250,204,21,0.8)'
            pingColor = 'bg-yellow-400'
          }

          return (
            <Marker 
              key={i} 
              longitude={node.lon} 
              latitude={node.lat} 
              anchor="center"
            >
              <div className="relative group/node cursor-crosshair">
                {/* Ping animation rings */}
                <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 rounded-full radar-ping ${pingColor} opacity-40`} />
                <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 rounded-full radar-ping ${pingColor} opacity-20`} style={{ animationDelay: '1s' }} />
                
                {/* Core Node Identifier */}
                <div 
                  className={`relative w-4 h-4 rounded-full border-[2px] border-slate-900 ${colorClass}`}
                  style={{ boxShadow: `0 0 20px ${glowColor}, inset 0 0 5px rgba(255,255,255,0.8)` }}
                />
                
                {/* Holographic Tooltip */}
                <div className="absolute top-4 left-1/2 -translate-x-1/2 mt-3 bg-slate-900/95 backdrop-blur-md border border-slate-700/80 p-3 rounded text-[10px] font-mono whitespace-nowrap opacity-0 group-hover/node:opacity-100 transition-opacity shadow-2xl z-50 pointer-events-none">
                  <div className="flex justify-between items-center gap-4 border-b border-slate-700 pb-1 mb-1">
                    <p className="text-white font-bold tracking-wider">{node.id.toUpperCase()}</p>
                    <div className={`w-2 h-2 rounded-full animate-pulse ${colorClass}`} />
                  </div>
                  <div className="space-y-1">
                    <p className="text-slate-300">STATUS: <span className={node.congestion > 0.8 ? 'text-red-400' : 'text-sky-400'}>
                      {node.congestion > 0.8 ? 'CRITICAL' : node.congestion > 0.5 ? 'WARNING' : 'NORMAL'}
                    </span></p>
                    <p className="text-slate-400">LOAD: {(node.congestion * 100).toFixed(1)}%</p>
                    <p className="text-slate-500 text-[8px] mt-1 pt-1 border-t border-slate-800">
                      COORD: {node.lat.toFixed(4)}N, {Math.abs(node.lon).toFixed(4)}W
                    </p>
                  </div>
                </div>
              </div>
            </Marker>
          )
        })}
      </MapGL>
      
      {/* Sci-fi Overlay: Holographic Grid */}
      <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(56,189,248,0.15)_1px,transparent_1px),linear-gradient(90deg,rgba(56,189,248,0.15)_1px,transparent_1px)] bg-[size:40px_40px] opacity-20 z-10" />
      
      {/* Scanline Animation */}
      <div className="map-scanline z-20 pointer-events-none" />
      
      {/* Measurements: UI HUD */}
      <div className="absolute top-6 left-6 z-30 font-mono text-xs text-sky-400 opacity-80 backdrop-blur-sm bg-slate-900/40 p-3 rounded-lg border border-sky-500/20 shadow-[0_0_15px_rgba(14,165,233,0.1)] pointer-events-none">
        <div className="flex items-center gap-2 mb-2">
          <span className="w-2 h-2 rounded-full bg-sky-400 animate-pulse" />
          <span className="tracking-widest font-bold">LIVE TELEMETRY</span>
        </div>
        <p className="text-[10px] text-sky-200/70">LAT: 40.7128° N</p>
        <p className="text-[10px] text-sky-200/70">LON: 74.0060° W</p>
        <p className="text-[10px] text-sky-200/70">RAD: 5.0km SECURE</p>
        
        <div className="w-32 border-b border-sky-400/50 mt-4 flex justify-between pt-1 text-[9px] font-bold text-sky-300">
          <span>0km</span>
          <span className="text-center">|</span>
          <span>5km</span>
        </div>
      </div>
      
      {/* Target Reticle Center */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[180px] h-[180px] rounded-full border border-sky-500/20 border-dashed z-20 pointer-events-none animate-[spin_40s_linear_infinite]" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] rounded-full border border-sky-500/10 z-20 pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-6 h-6 z-20 pointer-events-none flex items-center justify-center mb-1">
        <div className="w-px h-full bg-sky-400/80" />
        <div className="h-px w-full absolute bg-sky-400/80" />
      </div>

    </div>
  )
}