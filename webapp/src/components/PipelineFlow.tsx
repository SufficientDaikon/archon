import type { Pipeline } from "@/lib/types";

interface PipelineFlowProps {
  pipeline: Pipeline;
}

export default function PipelineFlow({ pipeline }: PipelineFlowProps) {
  return (
    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:border-brand-purple/40 hover:bg-white/[0.07] transition-all duration-300">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-brand-text">
          {pipeline.name}
        </h3>
        <p className="text-sm text-brand-muted mt-1">{pipeline.description}</p>
      </div>

      {/* Trigger */}
      <div className="mb-5 flex items-center gap-2">
        <span className="text-xs text-brand-muted">Trigger:</span>
        <code className="text-xs font-mono text-brand-cyan bg-black/30 px-2 py-1 rounded border border-white/10">
          &quot;{pipeline.trigger}&quot;
        </code>
      </div>

      {/* Visual Flow */}
      <div className="relative">
        {/* Steps */}
        <div className="flex flex-wrap gap-2 items-center">
          {pipeline.steps.map((step, i) => (
            <div key={step.name} className="flex items-center gap-2">
              <div className="group relative">
                <div className="bg-gradient-to-br from-brand-purple/20 to-brand-cyan/20 border border-white/10 rounded-lg px-3 py-2 text-center min-w-[100px] hover:border-brand-purple/40 transition-all cursor-default">
                  <p className="text-[10px] text-brand-muted mb-0.5">
                    Step {i + 1}
                  </p>
                  <p className="text-xs font-semibold text-brand-text">
                    {step.name}
                  </p>
                  <p className="text-[10px] text-brand-purple mt-0.5">
                    {step.agent}
                  </p>
                </div>
                {/* Tooltip */}
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-brand-bg border border-white/10 rounded-lg text-xs text-brand-muted whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 shadow-xl">
                  {step.description}
                </div>
              </div>
              {i < pipeline.steps.length - 1 && (
                <svg
                  className="w-4 h-4 text-brand-muted shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Run command */}
      <div className="mt-5 pt-4 border-t border-white/10">
        <p className="text-xs text-brand-muted mb-1">Run it:</p>
        <code className="text-xs font-mono text-brand-cyan bg-black/30 px-3 py-1.5 rounded border border-white/10 block">
          omniskill run {pipeline.slug}
        </code>
      </div>
    </div>
  );
}
