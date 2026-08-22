/**
 * VOLT-LOGIC API Client
 * Typed service to interface with FastAPI Backend & ML Model
 * Features: Capacity, Re, Rct, ambient_temperature
 */

export interface TelemetryPayload {
  vehicle_id: string;
  company: string;
  battery_type: string;
  capacity: number;
  re: number;
  rct: number;
  ambient_temperature: number;
  voltage?: number;
  current?: number;
}

export interface PredictionResult {
  status: 'HEALTHY' | 'WARNING' | 'CRITICAL';
  status_id?: string; // 'aman' | 'perlu di test lebih lanjut' | 'tidak aman'
  confidence: string;
  route: string;
  model_version: string;
  features?: {
    capacity: number;
    re: number;
    rct: number;
    ambient_temperature: number;
  };
  timestamp?: string;
}

export interface HistoryRecord {
  id?: number;
  vehicle_id: string;
  company: string;
  battery_type: string;
  capacity?: number | null;
  re?: number | null;
  rct?: number | null;
  ambient_temperature?: number | null;
  voltage?: number | null;
  current?: number | null;
  temperature?: number | null;
  resistance?: number | null;
  status: 'HEALTHY' | 'WARNING' | 'CRITICAL';
  confidence?: string | null;
  model_version?: string | null;
  created_at?: string;
}

export interface HealthStatus {
  ok: boolean;
  app?: string;
  version?: string;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

class ApiClient {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorMessage = `API Error: ${response.status} ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.error) {
          errorMessage = errorData.error;
        } else if (errorData.detail) {
          errorMessage = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
        }
      } catch {
        // Fallback to response status text
      }
      throw new Error(errorMessage);
    }

    return response.json();
  }

  /**
   * Liveness health check
   */
  async checkHealth(): Promise<HealthStatus> {
    return this.request<HealthStatus>('/health', { method: 'GET' });
  }

  /**
   * Run ML inference on telemetry with 4 features (Capacity, Re, Rct, ambient_temperature)
   */
  async predict(telemetry: TelemetryPayload): Promise<PredictionResult> {
    return this.request<PredictionResult>('/predict', {
      method: 'POST',
      body: JSON.stringify(telemetry),
    });
  }

  /**
   * Fetch inspection history scoped to company & batteryType
   */
  async getHistory(company: string, batteryType: string): Promise<HistoryRecord[]> {
    const params = new URLSearchParams({
      company: company.trim(),
      batteryType: batteryType.trim(),
    });
    return this.request<HistoryRecord[]>(`/history?${params.toString()}`, {
      method: 'GET',
    });
  }

  /**
   * Save a completed inspection record to the database
   */
  async saveHistory(record: HistoryRecord): Promise<HistoryRecord> {
    return this.request<HistoryRecord>('/history', {
      method: 'POST',
      body: JSON.stringify(record),
    });
  }
}

export const api = new ApiClient();
