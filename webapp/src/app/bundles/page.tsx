import { Metadata } from "next";
import BundleCard from "@/components/BundleCard";
import { getAllBundles } from "@/lib/registry";

export const metadata: Metadata = {
  title: "Bundle Showcase",
  description:
    "Explore 8 curated skill bundles — install entire skill packs for Django, Godot, UX design, testing, and more.",
  openGraph: {
    title: "Bundle Showcase — Archon",
    description:
      "8 curated bundles — install entire skill packs with one command.",
  },
};

export default function BundlesPage() {
  const bundles = getAllBundles();

  return (
    <div className="px-4 sm:px-6 lg:px-8 py-12">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-3xl sm:text-4xl font-bold text-brand-text mb-2">
            Bundle Showcase
          </h1>
          <p className="text-brand-muted max-w-2xl">
            {bundles.length} curated skill packs for specific domains. Install
            everything you need with a single command — no cherry-picking
            required.
          </p>
        </div>

        {/* Bundles Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {bundles.map((bundle) => (
            <BundleCard key={bundle.slug} bundle={bundle} />
          ))}
        </div>
      </div>
    </div>
  );
}
