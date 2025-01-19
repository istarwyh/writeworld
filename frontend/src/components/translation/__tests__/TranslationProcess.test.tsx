import { render, screen } from '@testing-library/react';
import { TranslationProcess } from '../TranslationProcess';
import type { TranslationStep } from '@/types/components';

describe('TranslationProcess', () => {
  const mockSteps: TranslationStep[] = [
    {
      type: 'init',
      content: '初始翻译：Hello World',
      timestamp: Date.now(),
    },
    {
      type: 'enhance',
      content: '文学优化：Greetings, World',
      timestamp: Date.now() + 1000,
    },
    {
      type: 'cultural',
      content: '文化适应：你好，世界',
      timestamp: Date.now() + 2000,
    },
  ];

  it('renders all translation steps', () => {
    render(
      <TranslationProcess
        steps={mockSteps}
        currentStep={2}
        isLoading={false}
      />
    );

    // 检查所有步骤是否都显示
    mockSteps.forEach(step => {
      expect(screen.getByText(step.content)).toBeInTheDocument();
    });
  });

  it('highlights current step', () => {
    const { container } = render(
      <TranslationProcess
        steps={mockSteps}
        currentStep={1}
        isLoading={false}
      />
    );

    // 检查当前步骤是否高亮显示
    const currentStepContent = screen.getByText(mockSteps[1].content);
    const stepContainer = currentStepContent.closest('.flex.items-start');
    expect(stepContainer).toHaveClass('bg-primary/10');
  });

  it('shows loading indicator for current step', () => {
    render(
      <TranslationProcess
        steps={mockSteps}
        currentStep={1}
        isLoading={true}
      />
    );

    // 检查加载指示器是否显示
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders empty state when no steps', () => {
    render(
      <TranslationProcess
        steps={[]}
        currentStep={0}
        isLoading={false}
      />
    );

    // 检查空状态提示
    expect(screen.getByText('等待翻译...')).toBeInTheDocument();
  });

  it('shows step icons based on type', () => {
    render(
      <TranslationProcess
        steps={mockSteps}
        currentStep={2}
        isLoading={false}
      />
    );

    // 检查每个步骤的图标
    expect(screen.getByLabelText('初始翻译')).toBeInTheDocument();
    expect(screen.getByLabelText('文学优化')).toBeInTheDocument();
    expect(screen.getByLabelText('文化适应')).toBeInTheDocument();
  });
});
