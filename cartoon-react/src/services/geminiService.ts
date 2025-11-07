import type { NewsArticle } from '../types/news';
import type { CartoonConcept, CartoonData, ComicScript } from '../types/cartoon';
import { createCartoonError } from '../types/error';

const API_KEY = import.meta.env.REACT_APP_GEMINI_API_KEY || '';
const BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent';
const MAX_RETRIES = 2;
const RETRY_DELAY_MS = 1000;

interface GeminiRequest {
  contents: Array<{
    parts: Array<{
      text: string;
    }>;
  }>;
}

interface GeminiResponse {
  candidates?: Array<{
    content: {
      parts: Array<{
        text: string;
      }>;
    };
  }>;
  error?: {
    message: string;
    code?: number;
  };
}

class GeminiService {
  private apiKey: string;
  private baseUrl: string;

  constructor() {
    this.apiKey = API_KEY;
    this.baseUrl = BASE_URL;
  }

  async generateCartoonConcepts(
    articles: NewsArticle[],
    location: string
  ): Promise<CartoonData> {
    if (!articles || articles.length === 0) {
      throw createCartoonError('No articles provided for concept generation');
    }

    const prompt = this.buildConceptPrompt(articles, location);

    try {
      const response = await this.callGeminiApi(prompt);
      const concepts = this.parseConceptResponse(response);

      return {
        topic: articles[0]?.title || 'News Topic',
        location,
        ideas: concepts.slice(0, 5),
        ranking: concepts.slice(0, 5).map((c) => c.title),
        winner: concepts[0]?.title || '',
        generatedAt: Date.now(),
      };
    } catch (error) {
      throw createCartoonError(
        'Failed to generate cartoon concepts',
        { originalError: String(error) }
      );
    }
  }

  async generateComicScript(
    concept: CartoonConcept,
    articles: NewsArticle[]
  ): Promise<ComicScript> {
    const prompt = this.buildScriptPrompt(concept, articles);

    try {
      const response = await this.callGeminiApi(prompt);
      const panels = this.parseScriptResponse(response);

      return {
        panels,
        description: `Comic script for: ${concept.title}`,
        generatedAt: Date.now(),
        newsContext: articles.map((a) => a.title).join('; '),
      };
    } catch (error) {
      throw createCartoonError(
        'Failed to generate comic script',
        { originalError: String(error) }
      );
    }
  }

  private buildConceptPrompt(articles: NewsArticle[], location: string): string {
    const headlines = articles
      .map((a) => {
        const desc = a.description || '';
        return `- ${a.title}\n  ${desc}`;
      })
      .join('\n');

    return `You are a brilliant editorial cartoonist in the style of Mark Knight.

Based on news headlines from ${location}:

${headlines}

Generate 5 cartoon concepts. Each should have title, premise, and why_funny.
Return only valid JSON array.`;
  }

  private buildScriptPrompt(
    concept: CartoonConcept,
    articles: NewsArticle[]
  ): string {
    const context = articles.map((a) => a.title).join('; ');

    return `Create a 4-panel comic script for this cartoon:

Title: ${concept.title}
Premise: ${concept.premise}
Commentary: ${concept.why_funny}

News context: ${context}

Return only valid JSON with panels array.`;
  }

  private async callGeminiApi(
    prompt: string,
    retryCount = 0
  ): Promise<GeminiResponse> {
    if (!this.apiKey) {
      throw createCartoonError(
        'Gemini API key not configured. Set REACT_APP_GEMINI_API_KEY environment variable.'
      );
    }

    const request: GeminiRequest = {
      contents: [
        {
          parts: [
            {
              text: prompt,
            },
          ],
        },
      ],
    };

    try {
      const url = `${this.baseUrl}?key=${this.apiKey}`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        if (response.status === 429 && retryCount < MAX_RETRIES) {
          await this.sleep(RETRY_DELAY_MS * Math.pow(2, retryCount));
          return this.callGeminiApi(prompt, retryCount + 1);
        }

        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = (await response.json()) as GeminiResponse;

      if (data.error) {
        throw new Error(`API Error: ${data.error.message}`);
      }

      return data;
    } catch (error) {
      if (retryCount < MAX_RETRIES) {
        await this.sleep(RETRY_DELAY_MS * Math.pow(2, retryCount));
        return this.callGeminiApi(prompt, retryCount + 1);
      }

      throw error;
    }
  }

  private parseConceptResponse(response: GeminiResponse): CartoonConcept[] {
    const text = response.candidates?.[0]?.content?.parts?.[0]?.text || '';

    const jsonMatch = text.match(/\[[\s\S]*\]/);
    if (!jsonMatch) {
      throw createCartoonError('Could not parse cartoon concepts from API response');
    }

    try {
      const parsed = JSON.parse(jsonMatch[0]) as Array<{
        title?: string;
        premise?: string;
        why_funny?: string;
      }>;

      return parsed.map((concept) => ({
        title: concept.title || 'Untitled',
        premise: concept.premise || 'A cartoon concept',
        why_funny: concept.why_funny || 'Political commentary',
      }));
    } catch (error) {
      throw createCartoonError(
        'Failed to parse cartoon concepts JSON',
        { parseError: String(error) }
      );
    }
  }

  private parseScriptResponse(response: GeminiResponse): string[] {
    const text = response.candidates?.[0]?.content?.parts?.[0]?.text || '';

    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw createCartoonError('Could not parse comic script from API response');
    }

    try {
      const parsed = JSON.parse(jsonMatch[0]) as {
        panels?: Array<{
          description?: string;
        }>;
      };

      if (!parsed.panels || !Array.isArray(parsed.panels)) {
        return [
          'Panel 1: Opening scene introducing the situation',
          'Panel 2: Building tension with character reaction',
          'Panel 3: Escalating the conflict',
          'Panel 4: The punchline reveals the commentary',
        ];
      }

      return parsed.panels
        .map((p) => p.description || 'Visual description goes here')
        .slice(0, 4);
    } catch (error) {
      throw createCartoonError(
        'Failed to parse comic script JSON',
        { parseError: String(error) }
      );
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

export const geminiService = new GeminiService();
