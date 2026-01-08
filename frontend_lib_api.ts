// lib/api.ts - API client for Velinor backend

import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Game API calls
export const gameApi = {
  startGame: async (playerName: string = 'Traveler') => {
    const response = await api.post('/api/game/start', {
      player_name: playerName,
    });
    return response.data;
  },

  takeAction: async (sessionId: string, choiceIndex?: number, playerInput?: string) => {
    const response = await api.post(`/api/game/${sessionId}/action`, {
      choice_index: choiceIndex,
      player_input: playerInput,
    });
    return response.data;
  },

  getGameState: async (sessionId: string) => {
    const response = await api.get(`/api/game/${sessionId}`);
    return response.data;
  },

  saveGame: async (sessionId: string) => {
    const response = await api.post(`/api/game/${sessionId}/save`);
    return response.data;
  },

  loadGame: async (sessionId: string) => {
    const response = await api.post(`/api/game/${sessionId}/load`);
    return response.data;
  },

  endSession: async (sessionId: string) => {
    const response = await api.delete(`/api/game/${sessionId}`);
    return response.data;
  },
};

export default api;
