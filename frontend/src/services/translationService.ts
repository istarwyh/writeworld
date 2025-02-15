import { TranslationParams } from '@/types/components';

const API_BASE_URL = '/api';

export interface TranslationResponse {
  translatedText: string;
  detectedLanguage?: string;
}

export interface TranslationEvent {
  result: string;
}

export interface TranslationProgress {
  type: 'init' | 'enhance' | 'cultural';
  content: string;
}

export type TranslationProgressCallback = (progress: TranslationProgress) => void;

interface ProcessResponse {
  init_agent_result?: string;
  reflection_agent_result?: string;
  improve_agent_result?: string;
}

export async function translateText(
  params: TranslationParams,
  onProgress?: TranslationProgressCallback
): Promise<TranslationResponse> {
  const payload = {
    service_id: "translation_service",
    params: {
      source_lang: params.sourceLang,
      target_lang: params.targetLang,
      source_text: params.sourceText
    }
  };

  try {
    const response = await fetch(`${API_BASE_URL}/service_run_stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Translation failed with status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let translatedText = '';

    if (!reader) {
      throw new Error('Failed to create stream reader');
    }

    onProgress?.({
      type: 'init',
      content: '识别翻译语言...'
    });

    let buffer = '';
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      buffer += chunk;

      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data:')) {
          try {
            const eventData = JSON.parse(line.slice(5));

            // 处理进度信息
            if (eventData.process) {
              const process = eventData.process as ProcessResponse;

              if (process.init_agent_result) {
                onProgress?.({
                  type: 'init',
                  content: '初始翻译：\n' + process.init_agent_result
                });
                translatedText = process.init_agent_result;
              }

              if (process.reflection_agent_result) {
                onProgress?.({
                  type: 'enhance',
                  content: '让我想想：\n' + process.reflection_agent_result
                });
              }

              if (process.improve_agent_result) {
                onProgress?.({
                  type: 'cultural',
                  content: '最终翻译：\n' + process.improve_agent_result
                });
                translatedText = process.improve_agent_result;
              }
            }

            // 处理最终结果
            if (eventData.result) {
              try {
                const resultData = JSON.parse(eventData.result);
                if (resultData.output) {
                  translatedText = resultData.output;
                }
              } catch (e) {
                // 如果结果解析失败，使用最后一次翻译结果
                console.warn('Failed to parse final result:', e);
              }
            }
          } catch (e) {
            console.warn('Failed to parse SSE data:', e);
          }
        }
      }
    }

    return {
      translatedText,
      detectedLanguage: params.sourceLang
    };
  } catch (error) {
    console.error('Translation service error:', error);
    throw error;
  }
}
