import { Input, Select } from 'antd';
import type { TranslationTextAreaProps } from '@/types/components';
import { useMemo, useCallback } from 'react';
import { detectLanguage } from '@/services/languageDetection';
import { debounce } from 'lodash';

const { TextArea } = Input;

const languageOptions = [
  { label: '中文', value: '中文' },
  { label: '英文', value: '英文' },
  { label: '日文', value: '日文' },
  { label: '西班牙文', value: '西班牙文' },
  { label: '法文', value: '法文' },
];

const literaryPlaceholders = {
  '中文': [
    '春眠不觉晓，处处闻啼鸟。',
    '床前明月光，疑是地上霜。',
    '独在异乡为异客，每逢佳节倍思亲。',
  ],
  '英文': [
    'To be, or not to be, that is the question.',
    'All that glitters is not gold.',
    'A thing of beauty is a joy forever.',
  ],
  '日文': [
    '古池や蛙飛び込む水の音',
    '柿食えば鐘が鳴るなり法隆寺',
  ],
  '西班牙文': [
    'En un lugar de la Mancha...',
    'Caminante, no hay camino...',
  ],
  '法文': [
    'La vie est belle.',
    'Je pense, donc je suis.',
  ],
};

export function TranslationTextArea({
  value,
  onChange,
  language,
  onLanguageChange,
  placeholder,
  readOnly = false,
  isSource = false,
}: TranslationTextAreaProps) {
  const defaultPlaceholder = useMemo(() => {
    const placeholders = literaryPlaceholders[language] || [];
    return placeholders[Math.floor(Math.random() * placeholders.length)] || placeholder;
  }, [language, placeholder]);

  const debouncedDetectLanguage = useCallback(
    debounce(async (text: string) => {
      if (!isSource || !text.trim()) return;
      try {
        const detectedLang = await detectLanguage(text);
        if (detectedLang && detectedLang !== language) {
          onLanguageChange(detectedLang);
        }
      } catch (error) {
        console.error('Language detection failed:', error);
      }
    }, 500),
    [isSource, language, onLanguageChange]
  );

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
    debouncedDetectLanguage(newValue);
  };

  return (
    <div className="flex flex-col gap-2">
      <Select
        value={language}
        onChange={onLanguageChange}
        options={languageOptions}
        className="w-32"
        size="large"
      />
      <TextArea
        value={value}
        onChange={handleChange}
        placeholder={defaultPlaceholder}
        autoSize={{ minRows: 8, maxRows: 12 }}
        className="text-base leading-relaxed"
        readOnly={readOnly}
        status={readOnly ? undefined : 'success'}
      />
    </div>
  );
}
