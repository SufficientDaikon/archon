"use client";

interface CategoryFilterProps {
  categories: string[];
  selected: string | null;
  onSelect: (category: string | null) => void;
  getCategoryColor?: (category: string) => string;
}

export default function CategoryFilter({
  categories,
  selected,
  onSelect,
  getCategoryColor,
}: CategoryFilterProps) {
  return (
    <div
      className="flex flex-wrap gap-2"
      role="group"
      aria-label="Filter by category"
    >
      <button
        onClick={() => onSelect(null)}
        className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-all ${
          selected === null
            ? "bg-gradient-to-r from-brand-purple to-brand-cyan text-white border-transparent"
            : "text-brand-muted border-white/10 hover:border-white/20 hover:text-brand-text hover:bg-white/5"
        }`}
      >
        All
      </button>
      {categories.map((cat) => (
        <button
          key={cat}
          onClick={() => onSelect(cat === selected ? null : cat)}
          className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-all ${
            cat === selected
              ? getCategoryColor
                ? getCategoryColor(cat) + " border"
                : "bg-gradient-to-r from-brand-purple to-brand-cyan text-white border-transparent"
              : "text-brand-muted border-white/10 hover:border-white/20 hover:text-brand-text hover:bg-white/5"
          }`}
        >
          {cat}
        </button>
      ))}
    </div>
  );
}
