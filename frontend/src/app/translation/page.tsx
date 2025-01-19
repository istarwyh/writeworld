'use client';

import { useState } from 'react';
import { message } from 'antd';
import { TranslationArea } from '@/components/translation/TranslationArea';
import { translateText } from '@/services/translationService';
import type { TranslationParams, TranslationStep } from '@/types/components';

export default function TranslationPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [steps, setSteps] = useState<TranslationStep[]>([]);
  const [currentStep, setCurrentStep] = useState(-1);
  const [targetText, setTargetText] = useState('');

  const handleTranslate = async (params: TranslationParams) => {
    setIsLoading(true);
    setSteps([]);
    setCurrentStep(-1);
    setTargetText('');

    try {
      const response = await translateText(params, (progress) => {
        setSteps(prev => {
          const newStep = {
            type: progress.type,
            content: progress.content,
            timestamp: Date.now()
          };
          return [...prev, newStep];
        });
        setCurrentStep(prev => prev + 1);
      });

      setTargetText(response.translatedText);
    } catch (error) {
      console.error('Translation failed:', error);
      message.error('翻译失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto py-8">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <h1 className="text-2xl font-bold mb-8 text-center">WriteWorld 翻译</h1>
          <TranslationArea
            onTranslate={handleTranslate}
            isLoading={isLoading}
            steps={steps}
            currentStep={currentStep}
            targetText={targetText}
          />
        </div>
      </div>
    </div>
  );
}
