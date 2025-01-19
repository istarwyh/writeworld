import { render, screen, fireEvent, act } from '@testing-library/react';
import { TranslationTextArea } from '../TranslationTextArea';

jest.mock('@/services/languageDetection', () => ({
  detectLanguage: jest.fn((text) => {
    if (text.includes('Hello')) return '英文';
    if (text.includes('你好')) return '中文';
    return '中文';
  }),
}));

describe('TranslationTextArea', () => {
  const mockOnChange = jest.fn();
  const mockOnLanguageChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with default placeholder', () => {
    render(
      <TranslationTextArea
        value=""
        onChange={mockOnChange}
        language="中文"
        onLanguageChange={mockOnLanguageChange}
        isSource={true}
      />
    );

    const textarea = screen.getByRole('textbox');
    expect(textarea).toBeInTheDocument();
    expect(textarea.getAttribute('placeholder')).toMatch(/[春眠不觉晓|床前明月光|独在异乡为异客]/);
  });

  it('shows character count', () => {
    render(
      <TranslationTextArea
        value="Hello World"
        onChange={mockOnChange}
        language="英文"
        onLanguageChange={mockOnLanguageChange}
      />
    );

    expect(screen.getByText('11 字')).toBeInTheDocument();
  });

  it('automatically detects language for source text', async () => {
    jest.useFakeTimers();

    render(
      <TranslationTextArea
        value=""
        onChange={mockOnChange}
        language="中文"
        onLanguageChange={mockOnLanguageChange}
        isSource={true}
      />
    );

    const textarea = screen.getByRole('textbox');
    fireEvent.change(textarea, { target: { value: 'Hello World Hello World' } });

    act(() => {
      jest.runAllTimers();
    });

    expect(mockOnLanguageChange).toHaveBeenCalledWith('英文');

    jest.useRealTimers();
  });

  it('disables language selection for target area', () => {
    render(
      <TranslationTextArea
        value=""
        onChange={mockOnChange}
        language="英文"
        onLanguageChange={mockOnLanguageChange}
        readOnly={true}
      />
    );

    const select = screen.getByRole('combobox');
    expect(select).toBeDisabled();
  });
});
