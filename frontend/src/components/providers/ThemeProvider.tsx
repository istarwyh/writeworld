import { ConfigProvider } from 'antd';
import { ReactNode } from 'react';
import themeConfig from '@/theme/themeConfig';

interface ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  return (
    <ConfigProvider theme={themeConfig}>
      {children}
    </ConfigProvider>
  );
}
