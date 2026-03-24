"use client";

import { useState, useMemo } from "react";
import SkillCard from "@/components/SkillCard";
import SearchBar from "@/components/SearchBar";
import CategoryFilter from "@/components/CategoryFilter";
import {
  getAllSkills,
  getSkillCategories,
  getCategoryColor,
} from "@/lib/registry";
import type { Skill, SkillCategory } from "@/lib/types";

const allSkills = getAllSkills();
const categories = getSkillCategories();

export default function SkillsPage() {
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const filtered = useMemo(() => {
    let result: Skill[] = allSkills;

    if (selectedCategory) {
      result = result.filter((s) => s.category === selectedCategory);
    }

    if (search) {
      const q = search.toLowerCase();
      result = result.filter(
        (s) =>
          s.name.toLowerCase().includes(q) ||
          s.description.toLowerCase().includes(q) ||
          s.tags.some((t) => t.toLowerCase().includes(q)),
      );
    }

    return result;
  }, [search, selectedCategory]);

  return (
    <div className="px-4 sm:px-6 lg:px-8 py-12">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-brand-text mb-2">
            Skill Marketplace
          </h1>
          <p className="text-brand-muted">
            Discover and install {allSkills.length} expert AI skills across{" "}
            {categories.length} categories.
          </p>
        </div>

        {/* Search + Filters */}
        <div className="space-y-4 mb-8">
          <SearchBar
            value={search}
            onChange={setSearch}
            placeholder="Search skills by name, description, or tags..."
          />
          <CategoryFilter
            categories={categories}
            selected={selectedCategory}
            onSelect={(cat) => setSelectedCategory(cat)}
            getCategoryColor={getCategoryColor}
          />
        </div>

        {/* Results count */}
        <p className="text-sm text-brand-muted mb-4">
          Showing{" "}
          <span className="font-medium text-brand-text">{filtered.length}</span>{" "}
          {filtered.length === 1 ? "skill" : "skills"}
          {selectedCategory && (
            <>
              {" "}
              in{" "}
              <span className="font-medium text-brand-purple">
                {selectedCategory}
              </span>
            </>
          )}
          {search && (
            <>
              {" "}
              matching &ldquo;
              <span className="font-medium text-brand-cyan">{search}</span>
              &rdquo;
            </>
          )}
        </p>

        {/* Skills Grid */}
        {filtered.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filtered.map((skill) => (
              <SkillCard key={skill.slug} skill={skill} />
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <p className="text-xl text-brand-muted mb-2">No skills found</p>
            <p className="text-sm text-brand-muted">
              Try adjusting your search or filters.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
