import { NextRequest, NextResponse } from 'next/server';

// 简单的语言检测逻辑
function detectLanguage(text: string): string {
  // 中文字符范围
  const chineseRegex = /[\u4e00-\u9fff]/;
  // 日文字符范围（平假名和片假名）
  const japaneseRegex = /[\u3040-\u309f\u30a0-\u30ff]/;
  // 英文字符范围
  const englishRegex = /[a-zA-Z]/;
  // 西班牙文特殊字符
  const spanishRegex = /[áéíóúñ¿¡]/i;
  // 法文特殊字符
  const frenchRegex = /[àâäéèêëîïôöùûüÿçœæ]/i;

  const scores = {
    'zh': 0,  // 中文
    'ja': 0,  // 日文
    'en': 0,  // 英文
    'es': 0,  // 西班牙文
    'fr': 0,  // 法文
  };

  // 计算每种语言的得分
  for (let char of text) {
    if (chineseRegex.test(char)) scores['zh']++;
    if (japaneseRegex.test(char)) scores['ja']++;
    if (englishRegex.test(char)) scores['en']++;
    if (spanishRegex.test(char)) scores['es']++;
    if (frenchRegex.test(char)) scores['fr']++;
  }

  // 找出得分最高的语言
  let maxScore = 0;
  let detectedLang = 'zh';

  for (let [lang, score] of Object.entries(scores)) {
    if (score > maxScore) {
      maxScore = score;
      detectedLang = lang;
    }
  }

  return detectedLang;
}

export async function POST(request: NextRequest) {
  try {
    const { text } = await request.json();

    if (!text || typeof text !== 'string') {
      return NextResponse.json(
        { error: 'Invalid input' },
        { status: 400 }
      );
    }

    const language = detectLanguage(text);

    return NextResponse.json({ language });
  } catch (error) {
    console.error('Language detection error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
