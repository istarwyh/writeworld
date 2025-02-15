import { Select } from 'antd';
import { GlobalOutlined } from '@ant-design/icons';
import type { HeaderProps, LanguageOption } from '@/types/components';
import Image from 'next/image';

const languageOptions: LanguageOption[] = [
  { label: '简体中文', value: 'zh-CN' },
  { label: 'English', value: 'en-US' },
  { label: '日本語', value: 'ja-JP' },
];

export function Header({ onLanguageChange, currentLanguage = 'zh-CN' }: HeaderProps) {
  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Image
              src="/logo.svg"
              alt="WriteWorld Logo"
              width={32}
              height={32}
              className="mr-2"
            />
            <span className="text-lg font-medium text-primary">WriteWorld</span>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-8">
            <a
              href="#"
              className="text-text-secondary hover:text-primary px-3 py-2
                         text-sm font-medium transition-colors duration-200"
            >
              首页
            </a>
            <a
              href="#"
              className="text-text-secondary hover:text-primary px-3 py-2
                         text-sm font-medium transition-colors duration-200"
            >
              翻译
            </a>
          </nav>

          {/* Actions */}
          <div className="flex items-center space-x-4">
            {/* Language Selector */}
            <Select
              defaultValue={currentLanguage}
              onChange={(value) => onLanguageChange?.(value)}
              options={languageOptions}
              className="w-32"
              suffixIcon={<GlobalOutlined className="text-secondary" />}
            />

            {/* Login Button */}
            <button
              className="inline-flex items-center px-4 py-2 border border-transparent
                         text-sm font-medium rounded-md text-white bg-primary
                         hover:opacity-90 transition-opacity duration-200"
            >
              登录
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
