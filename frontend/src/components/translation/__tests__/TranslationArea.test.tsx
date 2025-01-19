import { render, screen, fireEvent, act } from '@testing-library/react';
import { TranslationArea } from '../TranslationArea';
import { detectLanguage } from '@/services/languageDetection';

jest.mock('@/services/languageDetection');

describe('TranslationArea', () => {
  const mockOnTranslate = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders translation areas and buttons', () => {
    render(<TranslationArea onTranslate={mockOnTranslate} />);

    // Check text areas
    expect(screen.getByPlaceholderText('请输入要翻译的文本...')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('翻译结果将在这里显示...')).toBeInTheDocument();

    // Check language selectors
    expect(screen.getAllByRole('combobox')).toHaveLength(2);

    // Check translate button
    expect(screen.getByRole('button', { name: '翻 译' })).toBeInTheDocument();
  });

  it('handles language swap', () => {
    render(<TranslationArea onTranslate={mockOnTranslate} />);

    // Prepare test data
    const sourceInput = screen.getByPlaceholderText('请输入要翻译的文本...');
    fireEvent.change(sourceInput, { target: { value: 'Hello World' } });

    // Get language selectors
    const sourceSelector = screen.getAllByRole('combobox')[0];
    const targetSelector = screen.getAllByRole('combobox')[1];
    
    // Verify initial languages
    expect(screen.getByTitle('中文')).toBeInTheDocument();
    expect(screen.getByTitle('英文')).toBeInTheDocument();

    // Click swap button
    const swapButton = screen.getByRole('button', { name: 'swap' });
    fireEvent.click(swapButton);

    // Verify languages are swapped
    expect(screen.getByTitle('英文')).toBeInTheDocument();
    expect(screen.getByTitle('中文')).toBeInTheDocument();
  });

  it('calls onTranslate with correct parameters', async () => {
    (detectLanguage as jest.Mock).mockReturnValue('英文');

    render(<TranslationArea onTranslate={mockOnTranslate} />);

    // Set source text
    const sourceInput = screen.getByPlaceholderText('请输入要翻译的文本...');
    fireEvent.change(sourceInput, { target: { value: 'Hello World' } });

    // Wait for debounce
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 1000));
    });

    // Click translate button
    const translateButton = screen.getByRole('button', { name: '翻 译' });
    fireEvent.click(translateButton);

    // Verify onTranslate was called with correct parameters
    expect(mockOnTranslate).toHaveBeenCalledWith({
      sourceLang: '英文',
      targetLang: '英文',
      sourceText: 'Hello World',
    });
  });

  it('disables translate button when source text is empty', () => {
    render(<TranslationArea onTranslate={mockOnTranslate} />);

    const translateButton = screen.getByRole('button', { name: '翻 译' });
    expect(translateButton).toBeDisabled();
  });

  it('shows translation process when steps are provided', () => {
    const mockSteps: TranslationStep[] = [
      {
        type: 'init',
        content: '初始翻译：Hello World',
        timestamp: Date.now(),
      },
    ];

    render(
      <TranslationArea
        onTranslate={mockOnTranslate}
        steps={mockSteps}
        currentStep={0}
        isLoading={false}
      />
    );

    expect(screen.getByText('初始翻译：Hello World')).toBeInTheDocument();
  });

  it('hides translation process when no steps', () => {
    render(<TranslationArea onTranslate={mockOnTranslate} />);

    expect(screen.queryByText('等待翻译...')).not.toBeInTheDocument();
  });

  it('shows loading state in translation process', () => {
    render(
      <TranslationArea
        onTranslate={mockOnTranslate}
        isLoading={true}
        steps={[]}
        currentStep={-1}
      />
    );

    expect(screen.getByText('等待翻译...')).toBeInTheDocument();
  });
});
