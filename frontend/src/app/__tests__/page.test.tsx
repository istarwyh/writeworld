import { render, screen, fireEvent } from '@testing-library/react';
import Home from '../page';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

describe('Home', () => {
  it('renders WriteWorld title', () => {
    render(<Home />);
    expect(screen.getByText('WriteWorld')).toBeInTheDocument();
  });

  it('renders translation and writing buttons', () => {
    render(<Home />);
    expect(screen.getByText('翻 译')).toBeInTheDocument();
    expect(screen.getByText('写 作')).toBeInTheDocument();
  });

  it('disables writing button', () => {
    render(<Home />);
    const writingButton = screen.getByText('写 作').closest('button');
    expect(writingButton).toBeDisabled();
  });

  it('enables translation button', () => {
    render(<Home />);
    const translationButton = screen.getByText('翻 译').closest('button');
    expect(translationButton).not.toBeDisabled();
  });

  it('navigates to translation page when clicking translation button', () => {
    const mockRouter = { push: jest.fn() };
    jest.spyOn(require('next/navigation'), 'useRouter').mockReturnValue(mockRouter);

    render(<Home />);
    const translationButton = screen.getByText('翻 译');
    fireEvent.click(translationButton);

    expect(mockRouter.push).toHaveBeenCalledWith('/translation');
  });
});
