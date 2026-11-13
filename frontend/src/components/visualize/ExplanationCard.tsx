import React, { useState } from 'react';
import katex from 'katex';
import { ChevronRight, ChevronDown, BookOpen } from 'lucide-react';

interface ExplanationCardProps {
  stepNumber: number;
  totalSteps: number;
  title: string;
  explanation: string;
  formalNotation?: string;
}

export const ExplanationCard: React.FC<ExplanationCardProps> = ({
  stepNumber,
  totalSteps,
  title,
  explanation,
  formalNotation,
}) => {
  const [showFormal, setShowFormal] = useState(false);

  const renderMath = (tex: string) => {
    try {
      return {
        __html: katex.renderToString(tex, {
          throwOnError: false,
          displayMode: true,
        }),
      };
    } catch {
      return { __html: tex };
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 flex flex-col justify-between">
      <div>
        {/* Step Indicator Header */}
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Step {stepNumber} of {totalSteps}
          </span>
          <div className="w-20 h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 rounded-full"
              style={{ width: `${totalSteps > 0 ? (stepNumber / totalSteps) * 100 : 0}%` }}
            />
          </div>
        </div>

        <h3 className="text-lg font-bold text-slate-900 mb-2.5 tracking-tight leading-snug">
          {title}
        </h3>

        <p className="text-base text-slate-700 leading-relaxed font-normal">
          {explanation}
        </p>

        {/* Collapsible Formal Mathematical Notation */}
        {formalNotation && (
          <div className="mt-5 pt-4 border-t border-slate-100">
            <button
              onClick={() => setShowFormal(!showFormal)}
              className="text-sm font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1.5 transition-colors group"
            >
              {showFormal ? (
                <ChevronDown className="w-4 h-4 text-blue-600 group-hover:translate-y-0.5 transition-transform" />
              ) : (
                <ChevronRight className="w-4 h-4 text-blue-600 group-hover:translate-x-0.5 transition-transform" />
              )}
              <span>{showFormal ? 'Hide formal notation' : 'Show formal notation'}</span>
            </button>

            {showFormal && (
              <div className="mt-3 p-4 bg-slate-50 border border-slate-200/80 rounded-xl text-sm overflow-x-auto shadow-inner">
                <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5" />
                  <span>Mathematical Specification</span>
                </div>
                <div
                  className="katex-display-container text-slate-800 text-sm"
                  dangerouslySetInnerHTML={renderMath(formalNotation)}
                />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
