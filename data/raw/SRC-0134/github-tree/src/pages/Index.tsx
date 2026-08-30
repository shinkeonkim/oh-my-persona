import { useState, useCallback, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import CitySkyline from "@/components/CitySkyline";
import CityStats from "@/components/CityStats";
import { fetchContributions, contributionsToCity, CityBlock } from "@/lib/github";
import { Building2, Search, Loader2, Github, Download, ChevronLeft, ChevronRight, Box, Layers } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { lazy, Suspense } from "react";

const City3D = lazy(() => import("@/components/City3D"));

const CURRENT_YEAR = new Date().getFullYear();
const AVAILABLE_YEARS = Array.from({ length: 10 }, (_, i) => CURRENT_YEAR - i);

// Resolve CSS variable to computed HSL value
function resolveCssColor(cssVar: string): string {
  const el = document.documentElement;
  const style = getComputedStyle(el);
  // cssVar like "var(--building)" or just "--building"
  const varName = cssVar.replace(/^var\(/, "").replace(/\)$/, "").trim();
  const value = style.getPropertyValue(varName).trim();
  if (value) return `hsl(${value})`;
  return cssVar;
}

function inlineSvgStyles(svgEl: SVGSVGElement): string {
  const clone = svgEl.cloneNode(true) as SVGSVGElement;

  // Replace all hsl(var(--...)) patterns with computed values
  const serialized = new XMLSerializer().serializeToString(clone);
  const resolved = serialized.replace(/hsl\(var\(--([^)]+)\)\)/g, (_match, varName) => {
    return resolveCssColor(`--${varName}`);
  });

  // Also resolve any remaining CSS animations - remove them for static export
  // and set opacity to final values
  const parser = new DOMParser();
  const doc = parser.parseFromString(resolved, "image/svg+xml");

  // Remove all <animate> elements and set parent opacity
  const animates = doc.querySelectorAll("animate");
  animates.forEach((anim) => {
    const parent = anim.parentElement;
    if (parent) {
      // For opacity animations, set a static value
      const attr = anim.getAttribute("attributeName");
      if (attr === "opacity") {
        const values = anim.getAttribute("values")?.split(";");
        if (values && values.length > 0) {
          parent.setAttribute("opacity", values[0]);
        }
      }
    }
    anim.remove();
  });

  // Remove CSS class-based animations by adding inline styles
  const allElements = doc.querySelectorAll("[class]");
  allElements.forEach((el) => {
    const cls = el.getAttribute("class") || "";
    if (cls.includes("animate-building-rise")) {
      (el as HTMLElement).style.transform = "scaleY(1)";
      (el as HTMLElement).style.transformOrigin = "bottom";
    }
  });

  return new XMLSerializer().serializeToString(doc);
}

export default function Index() {
  const [username, setUsername] = useState("");
  const [blocks, setBlocks] = useState<CityBlock[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeUser, setActiveUser] = useState("");
  const [selectedYear, setSelectedYear] = useState<number | "last">("last");
  const [viewMode, setViewMode] = useState<"2d" | "3d">("2d");
  const svgRef = useRef<SVGSVGElement>(null);
  const { toast } = useToast();

  const handleGenerate = useCallback(async (year?: number | "last") => {
    const name = username.trim() || activeUser;
    if (!name) return;

    const y = year ?? selectedYear;
    setLoading(true);
    try {
      const contributions = await fetchContributions(name, y === "last" ? undefined : y);
      const city = contributionsToCity(contributions);
      setBlocks(city);
      setActiveUser(name);
      setSelectedYear(y);
    } catch {
      toast({
        title: "User not found",
        description: `Could not fetch contributions for "${name}". Check the username and try again.`,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }, [username, activeUser, selectedYear, toast]);

  const handleDownload = useCallback(() => {
    if (viewMode === "3d") {
      // For 3D, capture the canvas
      const canvas = document.querySelector("canvas") as HTMLCanvasElement;
      if (!canvas) return;
      const link = document.createElement("a");
      link.download = `commitcity-${activeUser}-${selectedYear}-3d.png`;
      link.href = canvas.toDataURL("image/png");
      link.click();
      return;
    }

    const svg = svgRef.current;
    if (!svg) return;

    // Inline all CSS variables and remove animations for proper rendering
    const inlinedSvg = inlineSvgStyles(svg);
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const img = new Image();
    const svgBlob = new Blob([inlinedSvg], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(svgBlob);

    img.onload = () => {
      canvas.width = img.width * 2;
      canvas.height = img.height * 2;
      ctx.scale(2, 2);
      ctx.drawImage(img, 0, 0);
      URL.revokeObjectURL(url);

      const link = document.createElement("a");
      link.download = `commitcity-${activeUser}-${selectedYear}.png`;
      link.href = canvas.toDataURL("image/png");
      link.click();
    };
    img.src = url;
  }, [activeUser, selectedYear, viewMode]);

  const yearLabel = selectedYear === "last" ? "Last 12 months" : `${selectedYear}`;

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Parallax background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-20 left-1/4 w-64 h-32 bg-primary/5 rounded-full blur-3xl animate-float-clouds" />
        <div className="absolute top-40 right-1/4 w-48 h-24 bg-accent/5 rounded-full blur-3xl animate-float-clouds" style={{ animationDelay: "3s" }} />
      </div>

      {/* Hero */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-[60vh] px-4 pt-16">
        <div className="flex items-center gap-3 mb-6">
          <Building2 className="w-10 h-10 text-primary" />
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-foreground">
            Commit<span className="text-primary">City</span>
          </h1>
        </div>

        <p className="text-muted-foreground text-lg md:text-xl text-center max-w-xl mb-10">
          Your GitHub contributions, reimagined as a city skyline.
          <br />
          <span className="text-sm">More commits = taller buildings. Zero days = parks. Bridges connect streaks.</span>
        </p>

        <div className="flex gap-3 w-full max-w-md">
          <div className="relative flex-1">
            <Github className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="GitHub username"
              value={username}
              onChange={e => setUsername(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleGenerate()}
              className="pl-10 bg-secondary border-border text-foreground placeholder:text-muted-foreground h-12 font-mono"
            />
          </div>
          <Button variant="hero" size="lg" onClick={() => handleGenerate()}
            disabled={loading || (!username.trim() && !activeUser)} className="h-12 px-6">
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
            Build
          </Button>
        </div>
      </div>

      {/* City */}
      {blocks && (
        <div className="relative z-10 px-4 pb-20 max-w-7xl mx-auto mt-8">
          {/* Controls bar */}
          <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
            {/* Year selector */}
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="icon" className="h-8 w-8"
                onClick={() => {
                  const idx = selectedYear === "last" ? 0 : AVAILABLE_YEARS.indexOf(selectedYear);
                  const next = AVAILABLE_YEARS[Math.min(idx + 1, AVAILABLE_YEARS.length - 1)];
                  handleGenerate(next);
                }}
                disabled={loading || (selectedYear !== "last" && selectedYear === AVAILABLE_YEARS[AVAILABLE_YEARS.length - 1])}>
                <ChevronLeft className="w-4 h-4" />
              </Button>

              <div className="flex gap-1.5 overflow-x-auto max-w-[300px] md:max-w-none scrollbar-none">
                <Button variant={selectedYear === "last" ? "hero" : "ghost"} size="sm"
                  className="h-7 px-2.5 text-xs font-mono shrink-0"
                  onClick={() => handleGenerate("last")} disabled={loading}>
                  Recent
                </Button>
                {AVAILABLE_YEARS.map(y => (
                  <Button key={y} variant={selectedYear === y ? "hero" : "ghost"} size="sm"
                    className="h-7 px-2.5 text-xs font-mono shrink-0"
                    onClick={() => handleGenerate(y)} disabled={loading}>
                    {y}
                  </Button>
                ))}
              </div>

              <Button variant="ghost" size="icon" className="h-8 w-8"
                onClick={() => {
                  if (selectedYear === "last") return;
                  const idx = AVAILABLE_YEARS.indexOf(selectedYear);
                  if (idx <= 0) { handleGenerate("last"); return; }
                  handleGenerate(AVAILABLE_YEARS[idx - 1]);
                }}
                disabled={loading || selectedYear === "last"}>
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>

            {/* View toggle + download */}
            <div className="flex items-center gap-2">
              <div className="flex border border-border rounded-md overflow-hidden">
                <Button
                  variant={viewMode === "2d" ? "hero" : "ghost"}
                  size="sm"
                  className="h-8 px-3 text-xs rounded-none gap-1.5"
                  onClick={() => setViewMode("2d")}
                >
                  <Layers className="w-3.5 h-3.5" />
                  2D
                </Button>
                <Button
                  variant={viewMode === "3d" ? "hero" : "ghost"}
                  size="sm"
                  className="h-8 px-3 text-xs rounded-none gap-1.5"
                  onClick={() => setViewMode("3d")}
                >
                  <Box className="w-3.5 h-3.5" />
                  3D
                </Button>
              </div>

              <Button variant="outline" size="sm" onClick={handleDownload} className="gap-1.5 h-8 text-xs">
                <Download className="w-3.5 h-3.5" />
                PNG
              </Button>
            </div>
          </div>

          <div className="text-xs text-muted-foreground mb-2 font-mono text-center">{yearLabel}</div>

          {/* View */}
          {viewMode === "2d" ? (
            <CitySkyline ref={svgRef} blocks={blocks} id="city-svg" />
          ) : (
            <Suspense fallback={
              <div className="w-full h-[500px] rounded-lg border border-border flex items-center justify-center bg-secondary/20">
                <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
              </div>
            }>
              <City3D blocks={blocks} />
            </Suspense>
          )}

          <CityStats blocks={blocks} username={activeUser} />

          {/* Legend */}
          <div className="mt-6 flex flex-wrap gap-4 justify-center text-xs text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-6 bg-building rounded-sm border border-border" />
              <span>Building (commits)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full bg-accent" />
              <span>Park (0 commits)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-6 h-1 bg-bridge rounded" />
              <span>Bridge (connecting)</span>
            </div>
            {viewMode === "3d" && (
              <div className="text-muted-foreground/60">
                Drag to rotate • Scroll to zoom • Right-click to pan
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
