import { detectLanguage } from '../languageDetection';

// Mock fetch
global.fetch = jest.fn();

describe('languageDetection', () => {
  beforeEach(() => {
    (global.fetch as jest.Mock).mockClear();
  });

  it('returns default language for empty text', async () => {
    const result = await detectLanguage('');
    expect(result).toBe('中文');
  });

  it('returns default language for whitespace', async () => {
    const result = await detectLanguage('   ');
    expect(result).toBe('中文');
  });

  it('detects Chinese text', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ language: 'zh' }),
    });

    const result = await detectLanguage('你好世界');
    expect(result).toBe('中文');
    expect(fetch).toHaveBeenCalledWith('/api/detect-language', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: '你好世界' }),
    });
  });

  it('detects English text', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ language: 'en' }),
    });

    const result = await detectLanguage('Hello World');
    expect(result).toBe('英文');
  });

  it('handles API error gracefully', async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('API Error'));

    const result = await detectLanguage('Hello World');
    expect(result).toBe('中文');
  });

  it('handles non-200 response gracefully', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    const result = await detectLanguage('Hello World');
    expect(result).toBe('中文');
  });
});
