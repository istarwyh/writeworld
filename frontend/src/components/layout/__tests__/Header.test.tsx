import { render, screen } from '@testing-library/react';
import { Header } from '../Header';

// Mock next/image
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: any) => {
    return <img {...props} />;
  },
}));

// Mock antd Select component
jest.mock('antd', () => {
  const antd = jest.requireActual('antd');
  return {
    ...antd,
    Select: ({ children, ...props }: any) => {
      return <select {...props}>{children}</select>;
    },
  };
});

describe('Header Component', () => {
  it('renders logo and navigation links', () => {
    render(<Header />);

    // Check logo
    expect(screen.getByText('WriteWorld')).toBeInTheDocument();

    // Check navigation links
    expect(screen.getByText('首页')).toBeInTheDocument();
    expect(screen.getByText('翻译')).toBeInTheDocument();
  });

  it('shows login button', () => {
    render(<Header />);
    expect(screen.getByText('登录')).toBeInTheDocument();
  });
});
