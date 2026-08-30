import React from 'react';
export interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'md' | 'lg';
  disabled?: boolean;
  className?: string;
}
export interface PrimaryButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'xs' | 'sm' | 'md' | 'lg';
  color?: 'orange' | 'gray' | 'green' | 'red' | 'yellow';
  disabled?: boolean;
  className?: string;
}

export interface SecondaryButtonProps {
  children: React.ReactNode;
  variant: 'focusResult' | 'learningEffect' | 'mailShare' | 'logout';
  onClick?: () => void;
  className?: string;
}
