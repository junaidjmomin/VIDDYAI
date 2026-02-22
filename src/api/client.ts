import type { StudentProfile } from '../store/useAppStore';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface LoginData {
  name: string;
  grade: number;
  subject: string;
}

export interface GameResultData {
  student_id: string;
  game_type: string;
  score: number;
  time_taken: number;
  is_dynamic?: boolean;
}

export interface FeedbackData {
  student_id: string;
  message_id: string;
  feedback_type: 'thumbs_up' | 'thumbs_down';
  timestamp: string;
}

export interface LoginResponse {
  success: boolean;
  profile: StudentProfile;
  message?: string;
}

export interface GameSubmitResponse {
  success: boolean;
  xp_earned: number;
  total_xp: number;
  level: number;
  confidence_band: string;
  iq_avg: number;
  eq_avg: number;
  profile: StudentProfile;
}

export interface ChallengeResponse {
  success: boolean;
  challenge: {
    question: string;
    options: string[];
    correct: string;
    explanation: string;
    trait: string;
  };
}

export interface UploadResponse {
  success: boolean;
  chunks_indexed: number;
  textbook_id?: string;
}

export interface VideoResponse {
  success: boolean;
  video_id: string;
  embed_url: string;
  watch_url: string;
  title: string;
  thumbnail: string;
  description: string;
  message?: string;
}

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        let message = `HTTP error! status: ${response.status}`;

        if (error.detail) {
          if (Array.isArray(error.detail)) {
            message = error.detail.map((d: any) => `${d.loc.join('.')}: ${d.msg}`).join(', ');
          } else if (typeof error.detail === 'string') {
            message = error.detail;
          } else {
            message = JSON.stringify(error.detail);
          }
        }

        throw new Error(message);
      }

      return await response.json();
    } catch (error: any) {
      console.error('API request failed:', error.message || error);
      throw error;
    }
  }

  // Authentication
  async login(data: LoginData): Promise<LoginResponse> {
    return this.request<LoginResponse>('/api/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Profile & Games
  async submitGameResult(data: GameResultData): Promise<GameSubmitResponse> {
    return this.request<GameSubmitResponse>('/api/profile/games/submit', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async generateDynamicChallenge(studentId: string, subject: string, grade: number, type: 'iq' | 'eq' | 'concept'): Promise<ChallengeResponse> {
    return this.request<ChallengeResponse>('/api/profile/game/generate', {
      method: 'POST',
      body: JSON.stringify({
        student_id: studentId,
        subject: subject,
        grade: grade,
        challenge_type: type
      }),
    });
  }

  async getProfile(studentId: string) {
    return this.request(`/api/profile/${studentId}`);
  }

  // Textbook Upload
  async uploadTextbook(file: File, studentId: string, subject: string, grade: number): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('student_id', studentId);
    formData.append('subject', subject);
    formData.append('grade', grade.toString());

    const url = `${this.baseURL}/api/textbook/upload`;

    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Upload failed: ${response.statusText}`);
    }

    return await response.json();
  }

  async getTextbookStatus(textbookId: string) {
    return this.request(`/api/textbook/status/${textbookId}`);
  }

  // Chat - SSE Stream
  createChatStream(query: string, studentId: string): EventSource {
    const url = `${this.baseURL}/api/chat/stream?query=${encodeURIComponent(query)}&student_id=${studentId}`;
    return new EventSource(url);
  }

  async getChatHistory(studentId: string) {
    return this.request(`/api/chat/history/${studentId}`);
  }

  // Feedback
  async logFeedback(data: FeedbackData) {
    return this.request('/api/feedback', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Analytics
  async getSatisfactionChart(studentId: string) {
    return this.request(`/api/satisfaction/${studentId}`);
  }

  // Content Generation
  async generatePPT(concept: string, grade: number, subject: string, keyPoints: string[]) {
  return fetch('http://localhost:8000/api/generate/ppt', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      concept,
      grade,
      subject,
      key_points: keyPoints,
      include_activity: true
    })
  });
}

  async searchVideos(
  concept: string,
  grade: number = 3,
  subject: string = 'Science',
  iqScore: number = 50,
  eqScore: number = 50
): Promise<VideoResponse> {

  const params = new URLSearchParams({
    concept: concept,
    grade: grade.toString(),
    subject: subject,
    iq_score: iqScore.toString(),
    eq_score: eqScore.toString()
  });

  return this.request<VideoResponse>(
    `/api/video/search?${params.toString()}`
  );
}

  // Health Check
  async healthCheck() {
    return this.request('/');
  }
}

export const api = new APIClient();
export default api;
