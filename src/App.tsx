import { useState, type FormEvent } from 'react';

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
  const [showInputModal, setShowInputModal] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);

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
    <div className="min-h-screen w-screen flex flex-col items-center justify-center p-6 bg-[radial-gradient(ellipse_at_center,_#1b4332_0%,_#0d2118_50%,_#060e0a_100%)]">

      {/* Logo VOLTLOGIC */}
      <div className="mb-10 text-center">
        <div className="inline-block px-10 py-3.5 rounded-2xl bg-[#10241b]/90 border border-emerald-500/30 shadow-2xl backdrop-blur-md">
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-wider text-gray-100 font-sans">
            VOLT<span className="text-[#52b788]">LOGIC</span>
          </h1>
        </div>
      </div>

      {/* Kontainer Dropdown & Tombol */}
      <div className="w-full max-w-sm space-y-6">

        {/* Dropdown 1: Nama Perusahaan */}
        <div className="space-y-1">
          <label className="block text-xs font-mono text-gray-300">Nama Perusahaan</label>
          <div className="relative">
            <select
              value={selectedCompany}
              onChange={(e) => {
                setSelectedCompany(e.target.value);
                setSelectedBattery('');
              }}
              className="w-full appearance-none bg-white text-gray-800 font-mono text-sm px-4 py-3 rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-emerald-400 pr-10 cursor-pointer"
            >
              <option value="">PT.</option>
              {COMPANY_DATA.map((comp) => (
                <option key={comp.name} value={comp.name}>{comp.name}</option>
              ))}
            </select>
            <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-500">
              ▼
            </div>
          </div>
        </div>

        {/* Dropdown 2: Jenis Baterai */}
        <div className="space-y-1">
          <label className="block text-xs font-mono text-gray-300">Jenis baterai</label>
          <div className="relative">
            <select
              value={selectedBattery}
              disabled={!selectedCompany}
              onChange={(e) => setSelectedBattery(e.target.value)}
              className="w-full appearance-none bg-white text-gray-800 font-mono text-sm px-4 py-3 rounded-lg shadow focus:outline-none focus:ring-2 focus:ring-emerald-400 pr-10 cursor-pointer disabled:bg-gray-200 disabled:cursor-not-allowed"
            >
              <option value="">jenis baterai</option>
              {availableBatteries.map((type) => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
            <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-500">
              ▼
            </div>
          </div>
        </div>

        {/* Tombol Aksi Bersampingan */}
        <div className="grid grid-cols-2 gap-0 pt-4">
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
      </div>

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