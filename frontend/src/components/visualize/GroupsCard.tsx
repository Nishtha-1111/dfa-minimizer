import React from 'react';

interface GroupsCardProps {
  partition: string[][];
  activeSplitterBlock?: string[];
}

export const GroupsCard: React.FC<GroupsCardProps> = ({
  partition,
  activeSplitterBlock = [],
}) => {
  const isSplitter = (block: string[]) => {
    if (!activeSplitterBlock || activeSplitterBlock.length === 0) return false;
    const s1 = [...block].sort().join(',');
    const s2 = [...activeSplitterBlock].sort().join(',');
    return s1 === s2;
  };

  const getGroupStyle = (index: number, isSplitterGroup: boolean) => {
    if (isSplitterGroup) {
      return {
        card: 'bg-amber-100/80 border-amber-400 text-amber-950 shadow-sm ring-2 ring-amber-300/40',
        badge: 'bg-amber-200 text-amber-900 border border-amber-300 font-bold',
        label: 'text-amber-900 font-bold',
      };
    }
    const styles = [
      {
        card: 'bg-blue-50/80 border-blue-200 text-blue-950',
        label: 'text-blue-800 font-semibold',
      },
      {
        card: 'bg-indigo-50/80 border-indigo-200 text-indigo-950',
        label: 'text-indigo-800 font-semibold',
      },
      {
        card: 'bg-teal-50/80 border-teal-200 text-teal-950',
        label: 'text-teal-800 font-semibold',
      },
      {
        card: 'bg-purple-50/80 border-purple-200 text-purple-950',
        label: 'text-purple-800 font-semibold',
      },
    ];
    return styles[index % styles.length];
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-1">
          <h3 className="text-lg font-bold text-slate-800 tracking-tight">Groups of states</h3>
          <span className="text-xs font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full border border-slate-200">
            {partition.length} {partition.length === 1 ? 'group' : 'groups'}
          </span>
        </div>
        <p className="text-sm text-slate-500 mb-4">
          States in the same group behave identically under all strings tested so far.
        </p>

        {/* Group Cards List */}
        <div className="space-y-3">
          {partition.map((group, idx) => {
            const splitterGroup = isSplitter(group);
            const style = getGroupStyle(idx, splitterGroup);
            const formatted = `{${[...group].sort().join(', ')}}`;

            return (
              <div
                key={`group-${idx}`}
                className={`flex items-center justify-between px-4 py-3 rounded-xl border transition-all duration-200 hover:translate-x-1 ${style.card}`}
              >
                <div className="flex items-center gap-5">
                  <span className={`text-xs w-16 ${style.label}`}>
                    Group {idx + 1}
                  </span>
                  <span className="font-mono text-base font-bold tracking-wide">
                    {formatted}
                  </span>
                </div>

                {splitterGroup && (
                  <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-amber-200 text-amber-900 border border-amber-300 shadow-xs">
                    Splitter
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <p className="text-xs text-slate-400 mt-5 pt-3 border-t border-slate-100 flex items-center justify-between">
        <span>Groups merge into one state when the run finishes.</span>
      </p>
    </div>
  );
};
