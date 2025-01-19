import React, { useState } from 'react';
import { Timeline } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import type { TranslationStep } from '@/types/components';

interface CollapsibleTextProps {
  text: string;
  maxLength?: number;
}

const CollapsibleText: React.FC<CollapsibleTextProps> = ({ text, maxLength = 300 }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const shouldCollapse = text.length > maxLength;

  if (!shouldCollapse) {
    return <ReactMarkdown>{text}</ReactMarkdown>;
  }

  return (
    <div>
      <ReactMarkdown>
        {isExpanded ? text : text.slice(0, maxLength) + '...'}
      </ReactMarkdown>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="text-primary hover:text-primary-dark text-sm mt-1"
      >
        {isExpanded ? '收起' : '展开全文'}
      </button>
    </div>
  );
};

interface TranslationProcessProps {
  steps: TranslationStep[];
  currentStep: number;
  isLoading: boolean;
}

const getIcon = (type: string) => {
  switch (type) {
    case 'init':
      return '🔍';
    case 'enhance':
      return '✨';
    case 'cultural':
      return '🎯';
    default:
      return '📝';
  }
};

export const TranslationProcess: React.FC<TranslationProcessProps> = ({
  steps,
  currentStep,
  isLoading,
}) => {
  if (steps.length === 0) {
    return (
      <div className="text-center text-gray-500 py-4">
        等待翻译...
      </div>
    );
  }

  return (
    <Timeline
      items={[
        ...steps.map((step, index) => ({
          dot: isLoading && index === currentStep ? (
            <LoadingOutlined className="text-primary" />
          ) : (
            <span className="text-lg">{getIcon(step.type)}</span>
          ),
          children: (
            <div className="py-1">
              <CollapsibleText text={step.content} />
              <div className="text-xs text-gray-400 mt-1">
                {new Date(step.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ),
        })),
      ]}
    />
  );
};
