export interface SystemHealth {
  status: string;
  project_name: string;
  version: string;
  gpu_available: boolean;
  device: string;
  model_status: string;
  database_connected: boolean;
  medical_disclaimer: string;
}

export interface ModelInfo {
  name: string;
  version: string;
  type: string;
  status: 'DEMO' | 'RESEARCH' | 'VALIDATED' | string;
  classes: string[];
  input_size: number[];
  description: string;
  loaded_at?: string;
}

export interface ExaminationStats {
  total_examinations: number;
  frames_processed: number;
  abnormal_regions_detected: number;
  avg_processing_time_ms: number;
  low_confidence_predictions: number;
  pending_reviews: number;
}

export interface ExaminationSummary {
  id: string;
  patient_anon_id?: string;
  input_type: 'IMAGE' | 'VIDEO' | 'LIVE';
  status: string;
  created_at: string;
  frame_count: number;
  total_detections: number;
}

export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface QualityMetrics {
  overall_quality: 'GOOD' | 'WARNING' | 'POOR';
  blur_score: number;
  brightness_score: number;
  warnings: string[];
}

export interface Prediction {
  id?: string;
  predicted_class: string;
  class_confidence: number;
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW';
  raw_softmax_scores: Record<string, number>;
  human_review_recommended?: boolean;
}

export interface Explanation {
  id?: string;
  heatmap_url?: string;
  overlay_url?: string;
  target_layer: string;
}

export interface Detection {
  id?: string;
  region_id: string;
  region_index: number;
  class_name: string;
  confidence: number;
  bbox: BoundingBox;
  prediction?: Prediction;
  explanation?: Explanation;
  review?: {
    status: string;
    notes?: string;
    reviewer_id?: string;
  };
}

export interface FrameAnalysis {
  frame_id: string;
  examination_id: string;
  frame_index: number;
  timestamp_ms: number;
  image_url: string;
  quality: QualityMetrics;
  detections: Detection[];
  review_status: 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'NEEDS_REVIEW';
  created_at: string;
}

export interface ReviewCreatePayload {
  examination_id?: string;
  frame_id?: string;
  detection_id?: string;
  review_status: 'ACCEPTED' | 'REJECTED' | 'NEEDS_REVIEW';
  reviewer_notes?: string;
  reviewer_id?: string;
}

export interface ExaminationReport {
  id: string;
  patient_anon_id: string;
  input_type: 'IMAGE' | 'VIDEO' | 'LIVE';
  status: string;
  created_at: string;
  frames: Array<{
    frame_id: string;
    frame_index: number;
    image_url: string;
    detections: Detection[];
  }>;
  detections: Detection[];
  quality?: QualityMetrics;
}
