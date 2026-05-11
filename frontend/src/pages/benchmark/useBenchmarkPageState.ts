import { useEffect, useMemo, useState } from 'react';
import { api } from '../../api/client';
import type { BenchmarkFixture } from '../../types/benchmark';

export function useBenchmarkPageState(token: string | null) {
  const [fixtures, setFixtures] = useState<BenchmarkFixture[]>([]);
  const [fixturesLoading, setFixturesLoading] = useState(false);
  const [fixturesError, setFixturesError] = useState<string | null>(null);
  const [selectedFixtureId, setSelectedFixtureId] = useState<number | null>(null);

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

  const selectedFixture = useMemo(
    () => fixtures.find((fixture) => fixture.id === selectedFixtureId) ?? null,
    [fixtures, selectedFixtureId],
  );

  return {
    fixtures,
    fixturesLoading,
    fixturesError,
    selectedFixtureId,
    selectedFixture,
    setSelectedFixtureId,
  };
}
