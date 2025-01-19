import { useState, useCallback, useEffect } from 'react';
import { Button } from 'antd';
import { SwapOutlined } from '@ant-design/icons';
import { TranslationTextArea } from './TranslationTextArea';
import { TranslationProcess } from './TranslationProcess';
import type { TranslationAreaProps, TranslationParams } from '@/types/components';

export const TranslationArea: React.FC<TranslationAreaProps> = ({
  onTranslate,
  isLoading = false,
  steps = [],
  currentStep = -1,
  targetText = '',
}) => {
  const [sourceText, setSourceText] = useState('');
  const [localTargetText, setLocalTargetText] = useState('');
  const [sourceLang, setSourceLang] = useState('中文');
  const [targetLang, setTargetLang] = useState('英文');

  useEffect(() => {
    setLocalTargetText(targetText);
  }, [targetText]);

  const handleSwapLanguages = useCallback(() => {
    setSourceLang(targetLang);
    setTargetLang(sourceLang);
    setSourceText(localTargetText);
    setLocalTargetText(sourceText);
  }, [sourceLang, targetLang, sourceText, localTargetText]);

  const handleTranslate = useCallback(async () => {
    if (!sourceText.trim()) return;

    const params: TranslationParams = {
      sourceLang,
      targetLang,
      sourceText: sourceText.trim(),
    };

    try {
      await onTranslate(params);
    } catch (error) {
      console.error('Translation failed:', error);
    }
  }, [sourceText, sourceLang, targetLang, onTranslate]);

  return (
    <div className="space-y-6 max-w-[1200px] mx-auto">
      <div className="grid grid-cols-[1fr,auto,1fr] gap-4">
        <div className="w-full">
          <TranslationTextArea
            value={sourceText}
            onChange={setSourceText}
            language={sourceLang}
            onLanguageChange={setSourceLang}
            placeholder="请输入要翻译的文本..."
            isSource
          />
        </div>

        <div className="flex items-center justify-center px-4">
          <Button
            type="text"
            icon={<SwapOutlined className="text-xl" />}
            onClick={handleSwapLanguages}
            className="hover:bg-gray-50 transition-colors"
          />
        </div>

        <div className="w-full">
          <TranslationTextArea
            value={localTargetText}
            onChange={setLocalTargetText}
            language={targetLang}
            onLanguageChange={setTargetLang}
            placeholder="翻译结果将在这里显示..."
            readOnly
          />
        </div>
      </div>

      <div className="flex justify-center">
        <Button
          type="primary"
          onClick={handleTranslate}
          loading={isLoading}
          disabled={!sourceText.trim()}
          size="large"
          className="px-8"
        >
          翻 译
        </Button>
      </div>

      {(steps.length > 0 || isLoading) && (
        <TranslationProcess
          steps={steps}
          currentStep={currentStep}
          isLoading={isLoading}
        />
      )}
    </div>
  );
};
