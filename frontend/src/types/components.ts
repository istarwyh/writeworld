export interface HeaderProps {
  onLanguageChange?: (lang: string) => void;
  currentLanguage?: string;
}

export interface LanguageOption {
  label: string;
  value: string;
  flag?: string;
}

export interface TranslationParams {
  sourceLang: string;
  targetLang: string;
  sourceText: string;
}

export interface TranslationTextAreaProps {
  value: string;
  onChange: (value: string) => void;
  language: string;
  onLanguageChange: (lang: string) => void;
  placeholder?: string;
  readOnly?: boolean;
  isSource?: boolean;
}

export interface TranslationStep {
  type: 'init' | 'enhance' | 'cultural';
  content: string;
  timestamp: number;
}

export interface TranslationProcessProps {
  steps: TranslationStep[];
  currentStep: number;
  isLoading: boolean;
}

export interface TranslationAreaProps {
  onTranslate: (params: TranslationParams) => Promise<void>;
  isLoading?: boolean;
  steps?: TranslationStep[];
  currentStep?: number;
  targetText?: string;
}
