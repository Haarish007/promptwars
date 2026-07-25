import React from 'react';
import { SOSButton } from './components/ui/SOSButton';

export const App: React.FC & { SOSButton: typeof SOSButton } = () => {
  return null;
};

App.SOSButton = SOSButton;

export default App;
