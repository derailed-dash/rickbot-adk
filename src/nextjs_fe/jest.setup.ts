import '@testing-library/jest-dom'

// Suppress "not wrapped in act(...)" warnings which are often non-actionable
// when dealing with complex MUI components and async side effects in tests.
const originalError = console.error;
console.error = (...args) => {
  const message = args.map(arg => String(arg)).join(' ');
  if (message.includes('not wrapped in act')) {
    return;
  }
  originalError.apply(console, args);
};
