import { useState, useRef, useEffect, type FormEvent } from 'react';
import voltlogicLogo from './assets/voltlogic-logo.svg';

// Data Perusahaan & Tipe Baterai
const COMPANY_DATA = [
  {
    name: 'PT. Logistik Nusantara Express',
    batteryTypes: ['Lithium-Ion 400V (NMC)', 'LFP 72V Standard Pack', 'Solid-State Proto 800V']
  },
  {
    name: 'PT. Fast Track Kuririndo',
    batteryTypes: ['Lithium-Ion 350V High-Output', 'LFP 48V Micro-Delivery']
  },
  {
    name: 'PT. Armada Hijau Sentosa',
    batteryTypes: ['LFP 72V Heavy-Duty Pack', 'Lithium-Ion 400V Long-Range']
  }
];

export default function App() {
  const [selectedCompany, setSelectedCompany] = useState('');
  const [selectedBattery, setSelectedBattery] = useState('');
  const [isCompanyOpen, setIsCompanyOpen] = useState(false);
  const [isBatteryOpen, setIsBatteryOpen] = useState(false);
  const [showInputModal, setShowInputModal] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);

  const dropdownContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownContainerRef.current &&
        !dropdownContainerRef.current.contains(event.target as Node)
      ) {
        setIsCompanyOpen(false);
        setIsBatteryOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Form Telemetri State
  const [telemetry, setTelemetry] = useState({
    vehicleId: 'EV-402',
    voltage: '384.2',
    current: '12.5',
    temperature: '31.4',
    resistance: '0.038'
  });

  // State Hasil Prediksi AI
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [predictionResult, setPredictionResult] = useState<null | {
    status: 'HEALTHY' | 'WARNING' | 'CRITICAL';
    confidence: string;
    route: string;
  }>(null);

  const availableBatteries = COMPANY_DATA.find((c) => c.name === selectedCompany)?.batteryTypes || [];

  const handleRunInference = (e: FormEvent) => {
    e.preventDefault();
    setIsAnalyzing(true);
    setPredictionResult(null);

    setTimeout(() => {
      setIsAnalyzing(false);
      const tempNum = parseFloat(telemetry.temperature);
      if (tempNum > 45) {
        setPredictionResult({
          status: 'CRITICAL',
          confidence: '99.1%',
          route: 'GROUNDED: Kendaraan dilarang beroperasi. Segera kirim ke unit servis.'
        });
      } else if (tempNum > 35) {
        setPredictionResult({
          status: 'WARNING',
          confidence: '94.6%',
          route: 'RESTRICTED: Khusus rute pendek dalam kota (micro-delivery) & jadwalkan servis.'
        });
      } else {
        setPredictionResult({
          status: 'HEALTHY',
          confidence: '98.4%',
          route: 'AUTHORIZED: Diizinkan muatan penuh untuk rute jarak jauh antarkota.'
        });
      }
    }, 500);
  };

  return (
    <div className="min-h-[125vh] w-full flex flex-col justify-between items-center p-6 bg-[radial-gradient(ellipse_at_top,_#1b4332_0%,_#0d2118_45%,_#060e0a_100%)] text-gray-100 selection:bg-emerald-500 selection:text-gray-950">

      {/* Central Content (Elevated slightly higher on the page) */}
      <div className="w-full flex-1 flex flex-col items-center justify-center pt-2 pb-24 transition-all duration-300">

        {/* Logo VOLTLOGIC SVG */}
        <div className="mb-8 flex justify-center">
          <img
            src={voltlogicLogo}
            alt="VOLTLOGIC Logo"
            className="h-20 sm:h-24 w-auto drop-shadow-2xl hover:scale-105 transition-transform duration-300"
          />
        </div>

        {/* Kontainer Dropdown & Tombol */}
        <main ref={dropdownContainerRef} className="w-full max-w-sm space-y-6 transition-all duration-300">

          {/* Dropdown 1: Nama Perusahaan */}
          <div className="space-y-1">
            <label className="block text-xs font-mono text-gray-300">Nama Perusahaan</label>
            <div className="transition-all duration-300">
              <button
                type="button"
                onClick={() => {
                  setIsCompanyOpen(!isCompanyOpen);
                  setIsBatteryOpen(false);
                }}
                className={`w-full bg-white text-gray-800 font-mono text-sm px-4 py-3 rounded-lg shadow flex items-center justify-between cursor-pointer transition-all duration-200 ${isCompanyOpen ? 'ring-2 ring-emerald-400' : 'hover:bg-gray-50'
                  }`}
              >
                <span className={`truncate ${!selectedCompany ? 'text-gray-500' : 'text-gray-900 font-medium'}`}>
                  {selectedCompany || 'PT.'}
                </span>
                <span className={`text-xs text-gray-500 transition-transform duration-300 ${isCompanyOpen ? 'rotate-180' : ''}`}>
                  ▼
                </span>
              </button>

              {/* In-Flow Options (Pushes downstream items downward) */}
              {isCompanyOpen && (
                <div className="mt-2 bg-white text-gray-800 font-mono text-sm rounded-lg shadow-xl overflow-hidden border border-emerald-500/20 divide-y divide-gray-100 animate-in fade-in slide-in-from-top-2 duration-200">
                  <div
                    onClick={() => {
                      setSelectedCompany('');
                      setSelectedBattery('');
                      setIsCompanyOpen(false);
                    }}
                    className="px-4 py-2.5 hover:bg-emerald-50 hover:text-emerald-800 text-gray-500 cursor-pointer transition-colors"
                  >
                    PT. (Reset)
                  </div>
                  {COMPANY_DATA.map((comp) => (
                    <div
                      key={comp.name}
                      onClick={() => {
                        setSelectedCompany(comp.name);
                        setSelectedBattery('');
                        setIsCompanyOpen(false);
                      }}
                      className={`px-4 py-2.5 hover:bg-emerald-50 hover:text-emerald-900 cursor-pointer flex items-center justify-between transition-colors ${
                        selectedCompany === comp.name ? 'bg-emerald-50/80 font-bold text-emerald-900' : ''
                      }`}
                    >
                      <span className="truncate">{comp.name}</span>
                      {selectedCompany === comp.name && (
                        <span className="text-emerald-600 text-xs">✓</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Dropdown 2: Jenis Baterai */}
          <div className="space-y-1">
            <label className="block text-xs font-mono text-gray-300">Jenis baterai</label>
            <div className="transition-all duration-300">
              <button
                type="button"
                disabled={!selectedCompany}
                onClick={() => {
                  if (selectedCompany) {
                    setIsBatteryOpen(!isBatteryOpen);
                    setIsCompanyOpen(false);
                  }
                }}
                className={`w-full font-mono text-sm px-4 py-3 rounded-lg shadow flex items-center justify-between transition-all duration-200 ${
                  !selectedCompany
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : isBatteryOpen
                    ? 'bg-white text-gray-800 ring-2 ring-emerald-400 cursor-pointer'
                    : 'bg-white text-gray-800 hover:bg-gray-50 cursor-pointer'
                }`}
              >
                <span className={`truncate ${!selectedBattery ? 'text-gray-500' : 'text-gray-900 font-medium'}`}>
                  {selectedBattery || 'jenis baterai'}
                </span>
                <span className={`text-xs text-gray-500 transition-transform duration-300 ${isBatteryOpen ? 'rotate-180' : ''}`}>
                  ▼
                </span>
              </button>

              {/* In-Flow Options (Pushes downstream items downward) */}
              {isBatteryOpen && selectedCompany && (
                <div className="mt-2 bg-white text-gray-800 font-mono text-sm rounded-lg shadow-xl overflow-hidden border border-emerald-500/20 divide-y divide-gray-100 animate-in fade-in slide-in-from-top-2 duration-200">
                  <div
                    onClick={() => {
                      setSelectedBattery('');
                      setIsBatteryOpen(false);
                    }}
                    className="px-4 py-2.5 hover:bg-emerald-50 hover:text-emerald-800 text-gray-500 cursor-pointer transition-colors"
                  >
                    jenis baterai (Reset)
                  </div>
                  {availableBatteries.map((type) => (
                    <div
                      key={type}
                      onClick={() => {
                        setSelectedBattery(type);
                        setIsBatteryOpen(false);
                      }}
                      className={`px-4 py-2.5 hover:bg-emerald-50 hover:text-emerald-900 cursor-pointer flex items-center justify-between transition-colors ${
                        selectedBattery === type ? 'bg-emerald-50/80 font-bold text-emerald-900' : ''
                      }`}
                    >
                      <span className="truncate">{type}</span>
                      {selectedBattery === type && (
                        <span className="text-emerald-600 text-xs">✓</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Tombol Aksi Bersampingan */}
          <div className="grid grid-cols-2 gap-0 pt-4 transition-all duration-300">
            <button
              onClick={() => setShowHistoryModal(true)}
              disabled={!selectedCompany || !selectedBattery}
              className="bg-[#61a986] hover:bg-[#529474] text-white font-medium text-xs sm:text-sm py-4 rounded-l-2xl border-r border-emerald-950/20 transition shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Riwayat Database
            </button>

            <button
              onClick={() => setShowInputModal(true)}
              disabled={!selectedCompany || !selectedBattery}
              className="bg-[#61a986] hover:bg-[#529474] text-white font-medium text-xs sm:text-sm py-4 rounded-r-2xl transition shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cek/Input Baterai
            </button>
          </div>
        </main>
      </div>

      {/* Footer Section */}
      <footer className="w-full max-w-2xl mt-auto pt-8 pb-4 border-t border-emerald-500/15 flex flex-col items-center gap-3 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-[11px] font-mono text-emerald-400 backdrop-blur-sm">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span>DEVELOPMENTAL BUILD • v0.1.0-alpha</span>
        </div>

        <p className="text-xs text-gray-400 max-w-md font-sans">
          VoltLogic Pre-Dispatch Battery Diagnostics System. For internal testing and vehicle telemetry simulation only.
        </p>

        <div className="flex items-center justify-center gap-1.5 text-[11px] font-mono text-amber-400/80 bg-amber-950/30 border border-amber-500/20 px-3 py-1 rounded-md">
          <span>⚠</span>
          <span>Notice: This is an active developmental build. Features and data models may change without notice.</span>
        </div>
      </footer>

      {/* MODAL 1: Input Telemetri Baterai */}
      {showInputModal && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-[#0f231a] border border-emerald-500/30 rounded-2xl w-full max-w-lg p-6 relative shadow-2xl">
            <button
              onClick={() => { setShowInputModal(false); setPredictionResult(null); }}
              className="absolute right-4 top-4 text-gray-400 hover:text-white font-bold text-lg"
            >
              ✕
            </button>

            <h3 className="text-lg font-semibold text-emerald-300 mb-1">
              ⚡ Input Telemetri Pre-Dispatch
            </h3>
            <p className="text-xs text-gray-400 mb-4">{selectedCompany} — {selectedBattery}</p>

            <form onSubmit={handleRunInference} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-gray-300">Vehicle ID</label>
                  <input
                    type="text"
                    value={telemetry.vehicleId}
                    onChange={(e) => setTelemetry({ ...telemetry, vehicleId: e.target.value })}
                    className="w-full bg-[#173326] border border-emerald-500/20 rounded p-2 text-sm text-white focus:outline-none focus:border-emerald-400"
                    required
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-300">Tegangan / Voltage (V)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={telemetry.voltage}
                    onChange={(e) => setTelemetry({ ...telemetry, voltage: e.target.value })}
                    className="w-full bg-[#173326] border border-emerald-500/20 rounded p-2 text-sm text-white focus:outline-none focus:border-emerald-400"
                    required
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-300">Arus / Current (A)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={telemetry.current}
                    onChange={(e) => setTelemetry({ ...telemetry, current: e.target.value })}
                    className="w-full bg-[#173326] border border-emerald-500/20 rounded p-2 text-sm text-white focus:outline-none focus:border-emerald-400"
                    required
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-300">Suhu / Temp (°C)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={telemetry.temperature}
                    onChange={(e) => setTelemetry({ ...telemetry, temperature: e.target.value })}
                    className="w-full bg-[#173326] border border-emerald-500/20 rounded p-2 text-sm text-white focus:outline-none focus:border-emerald-400"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="text-xs text-gray-300">Internal Resistance (Ω)</label>
                <input
                  type="number"
                  step="0.001"
                  value={telemetry.resistance}
                  onChange={(e) => setTelemetry({ ...telemetry, resistance: e.target.value })}
                  className="w-full bg-[#173326] border border-emerald-500/20 rounded p-2 text-sm text-white focus:outline-none focus:border-emerald-400"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={isAnalyzing}
                className="w-full mt-4 bg-emerald-500 hover:bg-emerald-400 text-gray-950 font-bold py-2.5 rounded-lg transition"
              >
                {isAnalyzing ? 'Memproses AI Inference (<100ms)...' : 'Jalankan AI Health Check'}
              </button>
            </form>

            {predictionResult && (
              <div className={`mt-5 p-4 rounded-xl border ${predictionResult.status === 'HEALTHY'
                ? 'bg-emerald-950/60 border-emerald-500 text-emerald-200'
                : predictionResult.status === 'WARNING'
                  ? 'bg-amber-950/60 border-amber-500 text-amber-200'
                  : 'bg-rose-950/60 border-rose-500 text-rose-200'
                }`}>
                <div className="font-bold text-sm">
                  STATUS: {predictionResult.status} (Keyakinan: {predictionResult.confidence})
                </div>
                <p className="text-xs mt-1.5 leading-relaxed opacity-90">
                  <strong>Tindakan Preskriptif:</strong> {predictionResult.route}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* MODAL 2: Riwayat Database */}
      {showHistoryModal && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-[#0f231a] border border-emerald-500/30 rounded-2xl w-full max-w-xl p-6 relative shadow-2xl">
            <button
              onClick={() => setShowHistoryModal(false)}
              className="absolute right-4 top-4 text-gray-400 hover:text-white font-bold text-lg"
            >
              ✕
            </button>

            <h3 className="text-lg font-semibold text-emerald-300 mb-1">
              📊 Riwayat Inspeksi Baterai
            </h3>
            <p className="text-xs text-gray-400 mb-4">{selectedCompany} — {selectedBattery}</p>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-gray-300">
                <thead className="bg-[#173326] text-emerald-300 font-mono">
                  <tr>
                    <th className="p-2">Vehicle ID</th>
                    <th className="p-2">Waktu</th>
                    <th className="p-2">Tegangan</th>
                    <th className="p-2">Status AI</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-emerald-900/40">
                  <tr>
                    <td className="p-2 font-mono">EV-402</td>
                    <td className="p-2">Hari ini, 06:15</td>
                    <td className="p-2">384.2 V</td>
                    <td className="p-2"><span className="px-2 py-0.5 rounded bg-emerald-950 border border-emerald-500 text-emerald-400 text-[10px] font-bold">HEALTHY</span></td>
                  </tr>
                  <tr>
                    <td className="p-2 font-mono">EV-108</td>
                    <td className="p-2">Kemarin, 14:20</td>
                    <td className="p-2">362.0 V</td>
                    <td className="p-2"><span className="px-2 py-0.5 rounded bg-amber-950 border border-amber-500 text-amber-400 text-[10px] font-bold">WARNING</span></td>
                  </tr>
                  <tr>
                    <td className="p-2 font-mono">EV-215</td>
                    <td className="p-2">18 Agu 2026</td>
                    <td className="p-2">310.5 V</td>
                    <td className="p-2"><span className="px-2 py-0.5 rounded bg-rose-950 border border-rose-500 text-rose-400 text-[10px] font-bold">CRITICAL</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}