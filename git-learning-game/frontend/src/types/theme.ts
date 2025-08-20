// Theme types for styled-components

export interface Theme {
  colors: {
    primary: string;
    primaryHover: string;
    secondary: string;
    background: string;
    backgroundSecondary: string;
    surface: string;
    text: string;
    textSecondary: string;
    success: string;
    warning: string;
    error: string;
    border: string;
  };
  fonts: {
    mono: string;
    sans: string;
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
    xxl: string;
  };
}

// Extend styled-components theme
declare module 'styled-components' {
  export interface DefaultTheme extends Theme {}
}
