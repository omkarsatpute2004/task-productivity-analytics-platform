import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from '../App';

describe('App Routing', () => {
  it('redirects unauthenticated users to /login page', async () => {
    render(<App />);
    expect(await screen.findByText(/Welcome Back/i)).toBeInTheDocument();
  });
});
