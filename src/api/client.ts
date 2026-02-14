/**
 * VidyaSetu AI - API Client
 * Handles all API calls to the FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface LoginData {
  name: string;
  grade: number;
  subject: string;
}

export interface GameResultData {
  student_id: string;
  game_type: 'pattern' | 'memory' | 'emotion';
  score: number;
  time_taken: number;
}

export interface FeedbackData {
  student_id: string;
  message_id: string;
  feedback_type: 'thumbs_up' | 'thumbs_down';
  timestamp: string;
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
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Authentication
  async login(data: LoginData) {
    return this.request('/api/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Profile & Games
  async submitGameResult(data: GameResultData) {
    return this.request('/api/profile/games/submit', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getProfile(studentId: string) {
    return this.request(`/api/profile/${studentId}`);
  }

  // Textbook Upload
  async uploadTextbook(file: File, studentId: string, subject: string) {
    const formData = new FormData();
    formData.append('file', file);

    const url = `${this.baseURL}/api/textbook/upload?student_id=${studentId}&subject=${subject}`;

    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
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
  async generatePPT(studentId: string, message: string) {
    return this.request('/api/generate/ppt', {
      method: 'POST',
      body: JSON.stringify({
        student_id: studentId,
        message: message,
      }),
    });
  }

  async searchVideos(topic: string, grade: number = 3) {
    return this.request(`/api/video/search?topic=${encodeURIComponent(topic)}&grade=${grade}`);
  }

  // Health Check
  async healthCheck() {
    return this.request('/');
  }
}

export const api = new APIClient();
export default api;
