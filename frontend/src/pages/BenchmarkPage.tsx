import { FlaskConical } from 'lucide-react';

export function BenchmarkPage() {
  return (
    <div className="flex flex-col gap-5">
      <div className="hw-surface p-0 overflow-hidden">
        <div className="flex items-center gap-3 px-4 py-2.5 border-b border-border">
          <FlaskConical className="w-3.5 h-3.5 text-accent" />
          <span className="text-[11px] font-bold tracking-[0.12em] text-accent uppercase">BENCHMARK</span>
          <span className="text-[10px] text-text-dim">Dashboard benchmark des agents LLM</span>
        </div>
        <div className="p-5">
          <p className="text-[11px] text-text-dim">
            La page benchmark est en cours d'implémentation. Les sections fixtures, runs,
            résultats V1, comparaison modèles et détail run seront ajoutées dans les phases suivantes.
          </p>
        </div>
      </div>
    </div>
  );
}
