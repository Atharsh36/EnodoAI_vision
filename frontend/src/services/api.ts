import axios from 'axios';
import {
  SystemHealth,
  ModelInfo,
  ExaminationStats,
  ExaminationSummary,
  ReviewCreatePayload,
  ExaminationReport,
} from '../types';

const API_BASE = '/api';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchHealth = async (): Promise<SystemHealth> => {
  const res = await api.get<SystemHealth>('/health');
  return res.data;
};

export const fetchModels = async (): Promise<ModelInfo[]> => {
  const res = await api.get<ModelInfo[]>('/models');
  return res.data;
};

export const fetchStats = async (): Promise<ExaminationStats> => {
  const res = await api.get<ExaminationStats>('/examinations/stats');
  return res.data;
};

export const fetchExaminations = async (): Promise<ExaminationSummary[]> => {
  const res = await api.get<ExaminationSummary[]>('/examinations');
  return res.data;
};

export const fetchExamination = async (id: string): Promise<ExaminationSummary> => {
  const res = await api.get<ExaminationSummary>(`/examinations/${id}`);
  return res.data;
};

export const fetchExaminationReport = async (id: string): Promise<ExaminationReport> => {
  const res = await api.get<ExaminationReport>(`/reports/${id}`);
  return res.data;
};

export const createExamination = async (inputType: 'IMAGE' | 'VIDEO' | 'LIVE' = 'IMAGE'): Promise<ExaminationSummary> => {
  const res = await api.post<ExaminationSummary>('/examinations', {
    input_type: inputType,
    patient_anon_id: `ANON-PATIENT-${Math.floor(1000 + Math.random() * 9000)}`,
  });
  return res.data;
};

export const submitReview = async (payload: ReviewCreatePayload) => {
  const res = await api.post('/reviews', payload);
  return res.data;
};

export const analyzeVideo = async (formData: FormData): Promise<ExaminationReport> => {
  const res = await api.post<ExaminationReport>('/analyze/video', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
};
