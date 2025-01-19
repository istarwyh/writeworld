import { TranslationProcessProps } from '@/types/components';
import { Spin } from 'antd';
import { TranslationOutlined, BulbOutlined, GlobalOutlined } from '@ant-design/icons';

const stepIcons = {
  init: <TranslationOutlined aria-label="初始翻译" />,
  enhance: <BulbOutlined aria-label="文学优化" />,
  cultural: <GlobalOutlined aria-label="文化适应" />,
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
    <div className="space-y-4 p-4">
      {steps.map((step, index) => (
        <div
          key={step.timestamp}
          className={`flex items-start space-x-3 p-3 rounded-lg transition-colors duration-200 ${
            index === currentStep ? 'bg-primary/10' : ''
          }`}
        >
          <div className="flex-shrink-0 text-xl text-primary">
            {stepIcons[step.type]}
          </div>
          <div className="flex-grow">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">
                {step.content}
              </span>
              {index === currentStep && isLoading && (
                <Spin size="small" role="progressbar" />
              )}
            </div>
            <div className="text-xs text-gray-400 mt-1">
              {new Date(step.timestamp).toLocaleTimeString()}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
