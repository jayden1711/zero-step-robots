Aborted call (2026-11-09 19:28 CST): the Walker2d batch started early (its wait-done chain fired when the hopper job
exited on an error, before the Sonnet hopper cells ran, i.e. before the prereg's walker2d start condition). The session
stopped the job (stop-job) while this first call was in flight: no reply was received. Renamed from
cpg-claude-opus-5-5_walker2d_H2_cpgspec_00 so the index runs later in the prereg order. The batch's isolation probe
(claude_isolation_probe_claude-opus-5-5_20261109T192837.json) also ran. Kept, not deleted.
