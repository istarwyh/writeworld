/**
 * Language detection service using backend API
 * Copyright (c) 2010-2014 Cybozu Labs, Inc. All rights reserved.
 * Licensed under the Apache License, Version 2.0
 */

const languageMap: Record<string, string> = {
  'zh': '中文',
  'en': '英文',
  'ja': '日文',
  'es': '西班牙文',
  'fr': '法文',
};

export async function detectLanguage(text: string): Promise<string> {
  if (!text.trim()) return '中文'; // 默认语言

  try {
    const response = await fetch('/api/detect-language', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error('Language detection failed');
    }

    const data = await response.json();
    return languageMap[data.language] || '中文';
  } catch (error) {
    console.error('Language detection failed:', error);
    return '中文';
  }
}
