import { Metadata } from "next";
import PipelineFlow from "@/components/PipelineFlow";
import { getAllPipelines } from "@/lib/registry";

export const metadata: Metadata = {
  title: "Pipeline Gallery",
  description:
    "Explore 5 automated multi-agent pipelines — from idea to shipped feature in a single command.",
  openGraph: {
    title: "Pipeline Gallery — Archon",
    description:
      "5 automated pipelines orchestrating agents for complete workflows.",
  },
};

export default function PipelinesPage() {
  const pipelines = getAllPipelines();

  return (
    <div className="px-4 sm:px-6 lg:px-8 py-12">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-3xl sm:text-4xl font-bold text-brand-text mb-2">
            Pipeline Gallery
          </h1>
          <p className="text-brand-muted max-w-2xl">
            {pipelines.length} automated multi-agent workflows. Each pipeline
            chains specialized agents to complete entire development lifecycles
            — from ideation to deployment.
          </p>
        </div>

        {/* How it works */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 mb-10">
          <h2 className="text-sm font-semibold text-brand-text mb-3">
            How Pipelines Work
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
            <div>
              <p className="font-medium text-brand-purple mb-1">1. Trigger</p>
              <p className="text-brand-muted text-xs">
                Say the trigger phrase and the pipeline activates automatically.
              </p>
            </div>
            <div>
              <p className="font-medium text-brand-cyan mb-1">2. Orchestrate</p>
              <p className="text-brand-muted text-xs">
                Agents execute steps in sequence, with context curation between
                handoffs.
              </p>
            </div>
            <div>
              <p className="font-medium text-pink-400 mb-1">3. Deliver</p>
              <p className="text-brand-muted text-xs">
                Each step produces artifacts that feed the next, ending with
                verified output.
              </p>
            </div>
          </div>
        </div>

        {/* Pipeline Cards */}
        <div className="space-y-6">
          {pipelines.map((pipeline) => (
            <PipelineFlow key={pipeline.slug} pipeline={pipeline} />
          ))}
        </div>
      </div>
    </div>
  );
}
