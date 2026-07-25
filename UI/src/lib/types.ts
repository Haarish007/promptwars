/**
 * Anchor — Shared Frontend TypeScript Definitions.
 */

export type UserRole = 'member' | 'guardian';

export interface User {
  id: string;
  email: string;
  role: UserRole;
}

export type SafetyLabel =
  | 'none'
  | 'distress'
  | 'crisis'
  | 'self_harm'
  | 'harm_to_others'
  | 'medical_emergency';

export type SteadyScoreBand = 'low' | 'guarded' | 'elevated' | 'high';

export interface SteadyFactor {
  factor: string;
  impact: string;
  detail: string;
}

export interface SteadyScore {
  score: number;
  band: SteadyScoreBand;
  factors: SteadyFactor[];
}

export interface CrisisResource {
  name: string;
  phone?: string;
  text?: string;
  url?: string;
  description: string;
}
