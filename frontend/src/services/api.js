/**
 * CALIP API Service Client
 * Centralized, typed, and easily debuggable API communication layer.
 * All endpoints match FastAPI backend routes.
 */

const BASE_URL = ''; // Relative path leverages Vite dev proxy & FastAPI static serve

// Debug logger helper (easy to toggle when debugging)
const DEBUG_API = true;
const logApi = (action, data) => {
  if (DEBUG_API) {
    console.log(`[CALIP API] ${action}:`, data);
  }
};

async function handleResponse(response) {
  if (!response.ok) {
    let errorDetail = 'API request failed';
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || errorJson.message || JSON.stringify(errorJson);
    } catch {
      errorDetail = await response.text() || response.statusText;
    }
    throw new Error(errorDetail);
  }
  return response.json();
}

export const api = {
  // --- Platform Statistics & Health ---
  async getHealth() {
    logApi('getHealth', {});
    const res = await fetch(`${BASE_URL}/health`);
    return handleResponse(res);
  },

  async getPlatformStats() {
    logApi('getPlatformStats', {});
    try {
      const res = await fetch(`${BASE_URL}/api/stats`);
      if (res.ok) return handleResponse(res);
    } catch (e) {
      console.warn('Failed /api/stats, trying /api', e);
    }
    try {
      const res = await fetch(`${BASE_URL}/api`);
      if (res.ok) return handleResponse(res);
    } catch (e) {
      console.warn('Failed /api, trying /health', e);
    }
    const res = await fetch(`${BASE_URL}/health`);
    return handleResponse(res);
  },

  // --- Search ---
  async searchLegal(query, searchType = 'hybrid', court = '', limit = 20) {
    const params = new URLSearchParams({
      query,
      search_type: searchType,
      limit: limit.toString(),
    });
    if (court) params.append('court', court);
    logApi('searchLegal', { query, searchType, court });
    const res = await fetch(`${BASE_URL}/api/search?${params.toString()}`);
    return handleResponse(res);
  },

  // --- Cases ---
  async getCases(court = '', status = '', limit = 100) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (court) params.append('court', court);
    if (status) params.append('status', status);
    logApi('getCases', { court, status });
    const res = await fetch(`${BASE_URL}/api/cases?${params.toString()}`);
    return handleResponse(res);
  },

  async getCaseById(caseId) {
    logApi('getCaseById', caseId);
    const res = await fetch(`${BASE_URL}/api/cases/${encodeURIComponent(caseId)}`);
    return handleResponse(res);
  },

  async getCaseDocuments(caseId) {
    logApi('getCaseDocuments', caseId);
    const res = await fetch(`${BASE_URL}/api/cases/${encodeURIComponent(caseId)}/documents`);
    return handleResponse(res);
  },

  async getCaseRelationships(caseId) {
    logApi('getCaseRelationships', caseId);
    const res = await fetch(`${BASE_URL}/api/cases/${encodeURIComponent(caseId)}/relationships`);
    return handleResponse(res);
  },

  async getCaseLinkages(caseId) {
    logApi('getCaseLinkages', caseId);
    const res = await fetch(`${BASE_URL}/api/cases/${encodeURIComponent(caseId)}/linkages`);
    return handleResponse(res);
  },

  // --- Documents ---
  async getDocuments(court = '', docType = '', limit = 1000) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (court) params.append('court', court);
    if (docType) params.append('doc_type', docType);
    logApi('getDocuments', { court, docType });
    const res = await fetch(`${BASE_URL}/api/documents?${params.toString()}`);
    return handleResponse(res);
  },

  async getDocumentById(documentId) {
    logApi('getDocumentById', documentId);
    const res = await fetch(`${BASE_URL}/api/documents/${encodeURIComponent(documentId)}`);
    return handleResponse(res);
  },

  async getDocumentOcr(documentId) {
    logApi('getDocumentOcr', documentId);
    const res = await fetch(`${BASE_URL}/api/documents/${encodeURIComponent(documentId)}/ocr`);
    return handleResponse(res);
  },

  async summarizeDocument(documentId) {
    logApi('summarizeDocument', documentId);
    const res = await fetch(`${BASE_URL}/api/documents/${encodeURIComponent(documentId)}/summarize`, {
      method: 'POST',
    });
    return handleResponse(res);
  },

  async reExtractDocument(documentId) {
    logApi('reExtractDocument', documentId);
    const res = await fetch(`${BASE_URL}/api/documents/${encodeURIComponent(documentId)}/re-extract`, {
      method: 'POST',
    });
    return handleResponse(res);
  },

  async uploadDocument(formData) {
    logApi('uploadDocument', 'FormData');
    const res = await fetch(`${BASE_URL}/api/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(res);
  },

  // --- Judgments & Orders ---
  async getJudgments(court = '', limit = 50) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (court) params.append('court', court);
    const res = await fetch(`${BASE_URL}/api/judgments?${params.toString()}`);
    return handleResponse(res);
  },

  async getOrders(court = '', limit = 50) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (court) params.append('court', court);
    const res = await fetch(`${BASE_URL}/api/orders?${params.toString()}`);
    return handleResponse(res);
  },

  // --- Courts ---
  async getCourts() {
    logApi('getCourts', {});
    const res = await fetch(`${BASE_URL}/api/courts`);
    return handleResponse(res);
  },

  // --- Atoms (25-Layer Atomic Intelligence) ---
  async getAtoms(limit = 50) {
    logApi('getAtoms', { limit });
    const res = await fetch(`${BASE_URL}/api/atoms?limit=${limit}`);
    return handleResponse(res);
  },

  async getAtomById(atomId) {
    logApi('getAtomById', atomId);
    const res = await fetch(`${BASE_URL}/api/atoms/${encodeURIComponent(atomId)}`);
    return handleResponse(res);
  },

  async getCanonicalAtom(atomId) {
    logApi('getCanonicalAtom', atomId);
    const res = await fetch(`${BASE_URL}/api/atoms/canonical/${encodeURIComponent(atomId)}`);
    return handleResponse(res);
  },

  async getAtomHydration(atomId) {
    logApi('getAtomHydration', atomId);
    const res = await fetch(`${BASE_URL}/api/atoms/${encodeURIComponent(atomId)}/hydration`);
    return handleResponse(res);
  },

  async reasonWithAtom(question, atomId = null, canonicalFirId = null) {
    logApi('reasonWithAtom', { question, atomId, canonicalFirId });
    const res = await fetch(`${BASE_URL}/api/reason`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, atom_id: atomId, canonical_fir_id: canonicalFirId }),
    });
    return handleResponse(res);
  },

  async getReviewQueue() {
    logApi('getReviewQueue', {});
    const res = await fetch(`${BASE_URL}/api/review-queue`);
    return handleResponse(res);
  },

  // --- AI Research / RAG ---
  async askLegalAI(query, court = null, docType = null) {
    logApi('askLegalAI', { query, court, docType });
    const res = await fetch(`${BASE_URL}/api/rag/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, court, doc_type: docType }),
    });
    return handleResponse(res);
  },

  // --- Longtail & District Courts ---
  async getLongtailCatalog() {
    logApi('getLongtailCatalog', {});
    const res = await fetch(`${BASE_URL}/api/longtail/catalog`);
    return handleResponse(res);
  },

  async harvestLongtail(state = 'delhi', district = 'south') {
    logApi('harvestLongtail', { state, district });
    const res = await fetch(`${BASE_URL}/api/longtail/harvest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ state, district }),
    });
    return handleResponse(res);
  },

  // --- Admin & Pipeline Operations ---
  async triggerSync() {
    logApi('triggerSync', {});
    const res = await fetch(`${BASE_URL}/api/sync/trigger`, { method: 'POST' });
    return handleResponse(res);
  },

  async extractAllPipeline(limit = null) {
    logApi('extractAllPipeline', { limit });
    const url = limit ? `${BASE_URL}/api/pipeline/extract-all?limit=${limit}` : `${BASE_URL}/api/pipeline/extract-all`;
    const res = await fetch(url, { method: 'POST' });
    return handleResponse(res);
  },
};
