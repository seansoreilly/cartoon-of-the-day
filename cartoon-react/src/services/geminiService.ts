import type { NewsArticle } from '../types/news';
import type { CartoonConcept, CartoonData, ComicScript, CartoonImage } from '../types/cartoon';
import { createCartoonError } from '../types/error';
import { ImageGenerationRateLimiter } from '../utils/rateLimiter';

const API_KEY = import.meta.env.REACT_APP_GEMINI_API_KEY || '';
const BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent';
const VISION_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent';
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

interface ImageCache {
  data: CartoonImage;
  timestamp: number;
}

class GeminiService {
  private apiKey: string;
  private baseUrl: string;
  private visionBaseUrl: string;
  private imageCache: Map<string, ImageCache> = new Map();
  private readonly CACHE_DURATION_MS = 60 * 60 * 1000; // 1 hour

  constructor() {
    this.apiKey = API_KEY;
    this.baseUrl = BASE_URL;
    this.visionBaseUrl = VISION_BASE_URL;
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

  async generateCartoonImage(concept: CartoonConcept): Promise<CartoonImage> {
    // Check rate limiting
    if (!ImageGenerationRateLimiter.canGenerateImage()) {
      const timeUntilNext = ImageGenerationRateLimiter.getTimeUntilNextGeneration();
      throw createCartoonError(
        `Rate limit exceeded. Try again in ${Math.ceil(timeUntilNext / 1000)} seconds.`,
        { statusCode: 429, code: 'RATE_LIMIT_ERROR' }
      );
    }

    // Check cache
    const cacheKey = this.buildImageCacheKey(concept);
    const cached = this.getFromCache(cacheKey);
    if (cached) {
      return cached;
    }

    const prompt = this.buildImagePrompt(concept);

    try {
      const response = await this.callVisionApi(prompt);
      const imageData = this.parseImageResponse(response);

      // Record rate limit
      ImageGenerationRateLimiter.recordImageGeneration();

      // Cache the result
      const cartoonImage: CartoonImage = {
        base64Data: imageData,
        mimeType: 'image/png',
        generatedAt: Date.now(),
      };
      this.setCache(cacheKey, cartoonImage);

      return cartoonImage;
    } catch (error) {
      throw createCartoonError(
        'Failed to generate cartoon image',
        { originalError: String(error) }
      );
    }
  }

  private buildImageCacheKey(concept: CartoonConcept): string {
    return `image_${concept.title.replace(/\s+/g, '_').toLowerCase()}`;
  }

  private getFromCache(key: string): CartoonImage | null {
    const entry = this.imageCache.get(key);
    if (!entry) {
      return null;
    }

    const isExpired = Date.now() - entry.timestamp > this.CACHE_DURATION_MS;
    if (isExpired) {
      this.imageCache.delete(key);
      return null;
    }

    return entry.data;
  }

  private setCache(key: string, data: CartoonImage): void {
    this.imageCache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }

  clearImageCache(): void {
    this.imageCache.clear();
  }

  private buildImagePrompt(concept: CartoonConcept): string {
    return `Create a professional newspaper political cartoon in the Mark Knight style based on this concept:

Title: ${concept.title}
Premise: ${concept.premise}
Commentary: ${concept.why_funny}

Style guidelines:
- Bold, expressive caricatures with exaggerated features
- Clear, strong line work
- Selective color with emphasis on key elements
- Professional newspaper comic strip format
- Visual metaphors that support the premise

Generate the cartoon image directly.`;
  }

  private async callVisionApi(
    prompt: string,
    retryCount = 0
  ): Promise<string> {
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
      const url = `${this.visionBaseUrl}?key=${this.apiKey}`;
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
          return this.callVisionApi(prompt, retryCount + 1);
        }

        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = (await response.json()) as GeminiResponse;

      if (data.error) {
        throw new Error(`API Error: ${data.error.message}`);
      }

      return data as unknown as string;
    } catch (error) {
      if (retryCount < MAX_RETRIES) {
        await this.sleep(RETRY_DELAY_MS * Math.pow(2, retryCount));
        return this.callVisionApi(prompt, retryCount + 1);
      }

      throw error;
    }
  }

  private parseImageResponse(response: string): string {
    // For Gemini Vision API, the response contains base64 encoded image data
    // This is a placeholder implementation - actual format depends on API response
    // The response should contain the generated image in base64 format
    if (typeof response === 'string' && response.length > 0) {
      return response;
    }

    throw createCartoonError('Could not extract image data from API response');
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
