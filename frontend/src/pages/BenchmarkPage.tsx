import { FlaskConical } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { FixturesTable } from './benchmark/FixturesTable';
import { useBenchmarkPageState } from './benchmark/useBenchmarkPageState';

export function BenchmarkPage() {
  const { token } = useAuth();
  const state = useBenchmarkPageState(token);

  return (
    <div className="flex flex-col gap-5">
      <div className="hw-surface p-0 overflow-hidden">
        <div className="flex items-center gap-3 px-4 py-2.5 border-b border-border">
          <FlaskConical className="w-3.5 h-3.5 text-accent" />
          <span className="text-[11px] font-bold tracking-[0.12em] text-accent uppercase">BENCHMARK</span>
          <span className="text-[10px] text-text-dim">Dashboard fixtures, runs, scores V1 et comparaison modèles</span>
        </div>
      </div>

      <div className="hw-surface p-0 overflow-hidden">
        <div className="flex items-center gap-3 px-4 py-2.5 border-b border-border">
          <span className="text-[11px] font-bold tracking-[0.12em] text-accent uppercase">FIXTURES</span>
        </div>
        <div className="p-5">
          <FixturesTable
            fixtures={state.fixtures}
            selectedFixtureId={state.selectedFixtureId}
            loading={state.fixturesLoading}
            error={state.fixturesError}
            onSelectFixture={(fixtureId) => {
              state.setSelectedFixtureId(fixtureId);
            }}
          />
        </div>
      </div>

      <div className="hw-surface p-0 overflow-hidden">
        <div className="flex items-center gap-3 px-4 py-2.5 border-b border-border">
          <span className="text-[11px] font-bold tracking-[0.12em] text-accent uppercase">RUN_CONFIGURATION</span>
        </div>
        <div className="p-5">
          <p className="text-[11px] text-text-dim">
            Prochaine étape: formulaire de lancement de run, liste des runs et tableau des résultats V1.
          </p>
          {state.selectedFixture && (
            <p className="text-[11px] text-text mt-2">
              Fixture sélectionnée: <strong>{state.selectedFixture.name}</strong>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
