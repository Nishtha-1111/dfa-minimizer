import React, { useEffect, useState, useRef } from 'react';
import { Play, Pause, ChevronLeft, ChevronRight, ChevronDown } from 'lucide-react';

interface PlaybackBarProps {
  currentStep: number;
  totalSteps: number;
  isPlaying: boolean;
  onPlayToggle: () => void;
  onNext: () => void;
  onPrev: () => void;
  onSeek: (step: number) => void;
  speed: number;
  onSpeedChange: (speed: number) => void;
}

export const PlaybackBar: React.FC<PlaybackBarProps> = ({
  currentStep,
  totalSteps,
  isPlaying,
  onPlayToggle,
  onNext,
  onPrev,
  onSeek,
  speed,
  onSpeedChange,
}) => {
  const [showSpeedMenu, setShowSpeedMenu] = useState(false);
  const scrubberRef = useRef<HTMLDivElement>(null);

  const speedOptions = [0.5, 1, 2];

  // Keyboard shortcut listener (Space = Play/Pause, ArrowLeft = Prev, ArrowRight = Next)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const activeTag = (document.activeElement?.tagName || '').toLowerCase();
      if (activeTag === 'input' || activeTag === 'textarea' || activeTag === 'select') {
        return;
      }

      if (e.code === 'Space') {
        e.preventDefault();
        onPlayToggle();
      } else if (e.code === 'ArrowLeft') {
        e.preventDefault();
        onPrev();
      } else if (e.code === 'ArrowRight') {
        e.preventDefault();
        onNext();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onPlayToggle, onPrev, onNext]);

  const handleScrubberClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!scrubberRef.current || totalSteps <= 1) return;
    const rect = scrubberRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const ratio = Math.max(0, Math.min(1, clickX / rect.width));
    const targetStep = Math.round(ratio * (totalSteps - 1));
    onSeek(targetStep);
  };

  const progressPercent = totalSteps > 1 ? (currentStep / (totalSteps - 1)) * 100 : 0;

  return (
    <div className="bg-white border-t border-slate-200 px-8 py-3.5 flex items-center gap-6 shadow-sm select-none">
      {/* Playback Button Controls */}
      <div className="flex items-center gap-3">
        {/* Back Button */}
        <button
          onClick={onPrev}
          disabled={currentStep === 0}
          className="flex items-center gap-1.5 px-4 py-2 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all active:scale-95 shadow-2xs"
          title="Step back (Left arrow)"
        >
          <ChevronLeft className="w-4 h-4 fill-current" />
          <span>Back</span>
        </button>

        {/* Play / Pause Primary Button */}
        <button
          onClick={onPlayToggle}
          className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-bold shadow-sm transition-all active:scale-95"
          title="Play / Pause (Space)"
        >
          {isPlaying ? (
            <>
              <Pause className="w-4 h-4 fill-current" />
              <span>Pause</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>Play</span>
            </>
          )}
        </button>

        {/* Next Button */}
        <button
          onClick={onNext}
          disabled={currentStep >= totalSteps - 1}
          className="flex items-center gap-1.5 px-4 py-2 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all active:scale-95 shadow-2xs"
          title="Step forward (Right arrow)"
        >
          <span>Next</span>
          <ChevronRight className="w-4 h-4 fill-current" />
        </button>
      </div>

      {/* Step Counter Indicator */}
      <div className="text-xs font-semibold text-slate-500 whitespace-nowrap min-w-[85px]">
        Step {totalSteps > 0 ? currentStep + 1 : 0} of {totalSteps}
      </div>

      {/* Scrubber Progress Bar */}
      <div
        ref={scrubberRef}
        onClick={handleScrubberClick}
        className="flex-1 relative py-3 cursor-pointer group"
      >
        <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-600 transition-all duration-150 rounded-full"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        <div
          className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-blue-600 border-2 border-white rounded-full shadow transition-all duration-150 group-hover:scale-125"
          style={{ left: `calc(${progressPercent}% - 8px)` }}
        />
      </div>

      {/* Speed Dropdown */}
      <div className="relative">
        <button
          onClick={() => setShowSpeedMenu(!showSpeedMenu)}
          className="flex items-center gap-1.5 px-3.5 py-1.5 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 bg-white hover:bg-slate-50 transition-all shadow-2xs"
        >
          <span>{speed}x</span>
          <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
        </button>

        {showSpeedMenu && (
          <div className="absolute right-0 bottom-full mb-2 bg-white border border-slate-200 rounded-xl shadow-lg py-1 w-24 z-50 text-sm">
            {speedOptions.map((s) => (
              <button
                key={s}
                onClick={() => {
                  onSpeedChange(s);
                  setShowSpeedMenu(false);
                }}
                className={`w-full text-left px-3.5 py-1.5 hover:bg-slate-100 ${
                  speed === s ? 'text-blue-600 font-bold bg-blue-50' : 'text-slate-700'
                }`}
              >
                {s}x speed
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
