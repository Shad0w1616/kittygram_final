import { render, screen } from '@testing-library/react';
import App from './app';

test('renders sign in under the Kittygram prefix', () => {
  window.history.pushState({}, '', '/kittygram/signin');
  render(<App />);
  expect(screen.getByText(/вход/i)).toBeInTheDocument();
  expect(screen.getByRole('link', { name: /зарегистрируйтесь/i }))
    .toHaveAttribute('href', '/kittygram/signup');
});
