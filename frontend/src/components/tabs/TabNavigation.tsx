import React from 'react';

export type ActiveTab = 'input' | 'visualize' | 'test';

interface TabNavigationProps {
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
  hasMinimizedResult: boolean;
}

export const TabNavigation: React.FC<TabNavigationProps> = ({
  activeTab,
  onTabChange,
}) => {
  const tabs: { id: ActiveTab; label: string; hint: string }[] = [
    {
      id: 'input',
      label: '1. Input',
      hint: 'Define states, alphabet, and transition table δ',
    },
    {
      id: 'visualize',
      label: '2. Visualize',
      hint: 'Step-by-step partition refinement and state equivalence',
    },
    {
      id: 'test',
      label: '3. Test strings',
      hint: 'Simulate string acceptance on original vs minimal DFA',
    },
  ];

  return (
    <div className="flex items-center gap-10 border-b border-slate-200 select-none">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`pb-3.5 text-left transition-all relative ${
              isActive
                ? 'text-blue-600 font-bold'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            <div className={`text-sm ${isActive ? 'font-bold' : 'font-semibold'}`}>
              {tab.label}
            </div>
            <div className="text-xs text-slate-400 font-normal mt-0.5">
              {tab.hint}
            </div>
            {isActive && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 rounded-full" />
            )}
          </button>
        );
      })}
    </div>
  );
};
