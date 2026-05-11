import { Plus } from 'lucide-react';
import { ButtonSpinner } from '../../components/LoadingIndicators';

const BENCHMARK_AGENTS = [
  'technical-analyst',
  'news-analyst',
  'market-context-analyst',
  'bullish-researcher',
  'bearish-researcher',
  'trader-agent',
  'risk-manager',
  'execution-manager',
] as const;

interface CreateFixturePanelProps {
  open: boolean;
  fixtureName: string;
  fixtureAgentName: string;
  fixtureInputsText: string;
  fixtureConfigText: string;
  createFixtureSubmitting: boolean;
  createFixtureError: string | null;
  fixtureInputsError: string | null;
  fixtureConfigError: string | null;
  onToggleOpen: () => void;
  onNameChange: (value: string) => void;
  onAgentChange: (value: string) => void;
  onInputsChange: (value: string) => void;
  onConfigChange: (value: string) => void;
  onCreate: () => void;
  onCancel: () => void;
}

export function CreateFixturePanel({
  open,
  fixtureName,
  fixtureAgentName,
  fixtureInputsText,
  fixtureConfigText,
  createFixtureSubmitting,
  createFixtureError,
  fixtureInputsError,
  fixtureConfigError,
  onToggleOpen,
  onNameChange,
  onAgentChange,
  onInputsChange,
  onConfigChange,
  onCreate,
  onCancel,
}: CreateFixturePanelProps) {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between gap-3">
        <span className="micro-label">Créer une fixture benchmark</span>
        <button
          type="button"
          className="btn-primary"
          onClick={onToggleOpen}
          aria-label={open ? 'Masquer le formulaire de fixture' : 'Afficher le formulaire de fixture'}
        >
          <Plus className="w-3.5 h-3.5" /> {open ? 'FERMER' : 'NOUVELLE FIXTURE'}
        </button>
      </div>

      {open ? (
        <div className="hw-surface-alt p-4 border border-border/50">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="micro-label block mb-1.5" htmlFor="benchmark-fixture-name">Nom</label>
              <input
                id="benchmark-fixture-name"
                type="text"
                value={fixtureName}
                onChange={(event) => onNameChange(event.target.value)}
                placeholder="Technical Analyst — EURUSD H1"
                aria-label="Nom de la fixture"
              />
            </div>

            <div>
              <label className="micro-label block mb-1.5" htmlFor="benchmark-fixture-agent">Agent</label>
              <select
                id="benchmark-fixture-agent"
                value={fixtureAgentName}
                onChange={(event) => onAgentChange(event.target.value)}
                aria-label="Agent de trading pour la fixture"
              >
                {BENCHMARK_AGENTS.map((agentName) => (
                  <option key={agentName} value={agentName}>
                    {agentName}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="micro-label block mb-1.5" htmlFor="benchmark-fixture-inputs">Inputs (JSON)</label>
              <textarea
                id="benchmark-fixture-inputs"
                value={fixtureInputsText}
                onChange={(event) => onInputsChange(event.target.value)}
                className="min-h-[128px]"
                placeholder='{"pair": "EURUSD", "timeframe": "H1"}'
                aria-label="Inputs JSON de la fixture"
              />
              {fixtureInputsError ? <p className="alert mt-2">{fixtureInputsError}</p> : null}
            </div>

            <div>
              <label className="micro-label block mb-1.5" htmlFor="benchmark-fixture-config">Config (JSON)</label>
              <textarea
                id="benchmark-fixture-config"
                value={fixtureConfigText}
                onChange={(event) => onConfigChange(event.target.value)}
                className="min-h-[128px]"
                placeholder="{}"
                aria-label="Configuration JSON optionnelle"
              />
              {fixtureConfigError ? <p className="alert mt-2">{fixtureConfigError}</p> : null}
            </div>
          </div>

          <div className="flex items-center gap-3 mt-4">
            <button
              type="button"
              className="btn-primary"
              disabled={createFixtureSubmitting}
              onClick={onCreate}
              aria-label="Créer la fixture benchmark"
            >
              {createFixtureSubmitting ? (
                <>
                  <ButtonSpinner /> CRÉATION...
                </>
              ) : (
                <>
                  <Plus className="w-3.5 h-3.5" /> CRÉER FIXTURE
                </>
              )}
            </button>

            <button
              type="button"
              className="btn-ghost"
              disabled={createFixtureSubmitting}
              onClick={onCancel}
              aria-label="Annuler la création de fixture"
            >
              ANNULER
            </button>
          </div>

          {createFixtureError ? <p className="alert mt-3">{createFixtureError}</p> : null}
        </div>
      ) : null}
    </div>
  );
}
