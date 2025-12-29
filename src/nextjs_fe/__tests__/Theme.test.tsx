import { render } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { useTheme } from '@mui/material/styles';
import theme from '../styles/theme';

function ThemeTester() {
  const theme = useTheme();
  return (
    <div>
      <span data-testid="primary-main">{theme.palette.primary.main}</span>
      <span data-testid="secondary-main">{theme.palette.secondary.main}</span>
    </div>
  );
}

describe('Portal Green Theme', () => {
  it('should have the correct primary color', () => {
    const { getByTestId } = render(
      <ThemeProvider theme={theme}>
        <ThemeTester />
      </ThemeProvider>
    );

    const primaryMain = getByTestId('primary-main');
    // Expecting the neon green color defined in the spec
    expect(primaryMain.textContent).toBe('#39FF14');
  });
});
