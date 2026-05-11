import { useEffect, useMemo, useState } from 'react';
import { api } from '../../api/client';
import type {
  BenchmarkCreateRunPayload,
  BenchmarkFixture,
  BenchmarkRun,
  BenchmarkRunDetail,
  ModelSpec,
} from '../../types/benchmark';

const DEFAULT_MODEL_SPEC: ModelSpec = {
  provider: 'openai',
  model_name: 'gpt-4o-mini',
  parameters: { temperature: 0 },
};

type ScenarioType = 'single-agent' | 'debate-bundle' | 'full-pipeline';

function toScenarioType(value: unknown): ScenarioType {
  if (value === 'debate-bundle' || value === 'full-pipeline') return value;
  return 'single-agent';
}

export function useBenchmarkPageState(token: string | null) {
  const [fixtures, setFixtures] = useState<BenchmarkFixture[]>([]);
  const [fixturesLoading, setFixturesLoading] = useState(false);
  const [fixturesError, setFixturesError] = useState<string | null>(null);
  const [selectedFixtureId, setSelectedFixtureId] = useState<number | null>(null);

  const [runs, setRuns] = useState<BenchmarkRun[]>([]);
  const [runsLoading, setRunsLoading] = useState(false);
  const [selectedRunId, setSelectedRunId] = useState<number | null>(null);
  const [runDetail, setRunDetail] = useState<BenchmarkRunDetail | null>(null);
  const [runDetailLoading, setRunDetailLoading] = useState(false);
  const [runDetailError, setRunDetailError] = useState<string | null>(null);

  const [modelSpecs, setModelSpecs] = useState<ModelSpec[]>([DEFAULT_MODEL_SPEC]);
  const [repeatCount, setRepeatCount] = useState('3');
  const [tagsInput, setTagsInput] = useState('');
  const [submittingRun, setSubmittingRun] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const selectedFixture = useMemo(
    () => fixtures.find((fixture) => fixture.id === selectedFixtureId) ?? null,
    [fixtures, selectedFixtureId],
  );

  const selectedRun = useMemo(
    () => runs.find((run) => run.id === selectedRunId) ?? null,
    [runs, selectedRunId],
  );

  const loadFixtures = async () => {
    if (!token) return;
    setFixturesLoading(true);
    setFixturesError(null);
    try {
      const data = await api.listBenchmarkFixtures(token);
      const active = data.filter((fixture) => !fixture.is_deleted);
      setFixtures(active);
      if (active.length > 0 && selectedFixtureId == null) {
        setSelectedFixtureId(active[0].id);
      }
    } catch (error) {
      setFixturesError(error instanceof Error ? error.message : 'Impossible de charger les fixtures');
    } finally {
      setFixturesLoading(false);
    }
  };

  useEffect(() => {
    void loadFixtures();
  }, [token]);

  useEffect(() => {
    if (!selectedFixtureId) {
      setRuns([]);
      return;
    }

    const loadRuns = async () => {
      if (!token) return;
      setRunsLoading(true);
      try {
        const data = await api.listBenchmarkRuns(token, { fixture_id: selectedFixtureId });
        setRuns(data);
      } finally {
        setRunsLoading(false);
      }
    };

    void loadRuns();
  }, [token, selectedFixtureId]);

  useEffect(() => {
    if (!selectedRunId) {
      setRunDetail(null);
      return;
    }

    const loadRunDetail = async () => {
      if (!token) return;
      setRunDetailLoading(true);
      setRunDetailError(null);
      try {
        const detail = await api.getBenchmarkRun(token, selectedRunId);
        setRunDetail(detail);
        try {
          await api.getBenchmarkRunResults(token, selectedRunId);
        } catch {
          // TODO(GH-26/OQ-1): fallback silencieux tant que le contrat /results n'est pas stabilisé.
        }
      } catch (error) {
        setRunDetail(null);
        setRunDetailError(error instanceof Error ? error.message : 'Impossible de charger le détail du run');
      } finally {
        setRunDetailLoading(false);
      }
    };

    void loadRunDetail();
  }, [token, selectedRunId]);

  const handleModelSpecChange = (index: number, field: keyof ModelSpec, value: string) => {
    setModelSpecs((prev) => {
      const next = [...prev];
      const current = next[index] ?? DEFAULT_MODEL_SPEC;
      if (field === 'parameters') {
        next[index] = {
          ...current,
          parameters: {
            ...(current.parameters ?? {}),
            temperature: value === '' ? undefined : Number(value),
          },
        };
        return next;
      }
      next[index] = {
        ...current,
        [field]: value,
      };
      return next;
    });
  };

  const handleSubmitRun = async () => {
    if (!token || !selectedFixture) return;

    const validSpecs = modelSpecs.filter(
      (spec) => spec.provider.trim().length > 0 && spec.model_name.trim().length > 0,
    );

    if (validSpecs.length === 0) {
      setSubmitError('Ajoutez au moins un modèle valide (provider + model_name).');
      return;
    }

    setSubmittingRun(true);
    setSubmitError(null);

    try {
      for (const spec of validSpecs) {
        const payload: BenchmarkCreateRunPayload = {
          fixture_id: selectedFixture.id,
          fixture_hash: selectedFixture.hash,
          model_spec: spec,
          scenario_type: toScenarioType(selectedFixture.config?.scenario_type),
          repetitions: Number(repeatCount) || 3,
        };
        await api.createBenchmarkRun(token, payload);
      }

      const refreshedRuns = await api.listBenchmarkRuns(token, { fixture_id: selectedFixture.id });
      setRuns(refreshedRuns);
      // TODO(GH-26/OQ-3): tags préparés côté UI, endpoint backend actuel ne supporte pas encore le champ.
      void tagsInput;
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'Échec du lancement benchmark');
    } finally {
      setSubmittingRun(false);
    }
  };

  return {
    fixtures,
    fixturesLoading,
    fixturesError,
    selectedFixtureId,
    selectedFixture,
    runs,
    runsLoading,
    selectedRun,
    selectedRunId,
    runDetail,
    runDetailLoading,
    runDetailError,
    modelSpecs,
    repeatCount,
    tagsInput,
    submittingRun,
    submitError,
    setSelectedFixtureId,
    setSelectedRunId,
    setModelSpecs,
    setRepeatCount,
    setTagsInput,
    handleModelSpecChange,
    handleSubmitRun,
  };
}
