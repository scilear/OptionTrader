-- Schema for v1 (DuckDB/SQLite compatible)

CREATE SEQUENCE IF NOT EXISTS snapshots_id_seq;
CREATE SEQUENCE IF NOT EXISTS option_quotes_id_seq;
CREATE SEQUENCE IF NOT EXISTS iv_points_id_seq;
CREATE SEQUENCE IF NOT EXISTS surface_metrics_id_seq;
CREATE SEQUENCE IF NOT EXISTS alerts_id_seq;
CREATE SEQUENCE IF NOT EXISTS trade_ideas_id_seq;
CREATE SEQUENCE IF NOT EXISTS pipeline_runs_id_seq;

CREATE TABLE IF NOT EXISTS pipeline_runs (
  run_id INTEGER PRIMARY KEY DEFAULT nextval('pipeline_runs_id_seq'),
  started_at TIMESTAMP NOT NULL,
  finished_at TIMESTAMP,
  status TEXT NOT NULL,
  config_hash TEXT,
  code_version TEXT,
  error_message TEXT
);

CREATE TABLE IF NOT EXISTS snapshots (
  snapshot_id INTEGER PRIMARY KEY DEFAULT nextval('snapshots_id_seq'),
  run_id INTEGER,
  ts TIMESTAMP NOT NULL,
  underlying TEXT NOT NULL,
  spot DOUBLE PRECISION NOT NULL,
  source TEXT NOT NULL,
  session_tag TEXT NOT NULL,
  notes TEXT,
  FOREIGN KEY(run_id) REFERENCES pipeline_runs(run_id)
);

CREATE TABLE IF NOT EXISTS option_quotes (
  quote_id INTEGER PRIMARY KEY DEFAULT nextval('option_quotes_id_seq'),
  snapshot_id INTEGER NOT NULL,
  expiry DATE NOT NULL,
  strike DOUBLE PRECISION NOT NULL,
  option_right TEXT NOT NULL,
  bid DOUBLE PRECISION,
  ask DOUBLE PRECISION,
  last DOUBLE PRECISION,
  bid_size INTEGER,
  ask_size INTEGER,
  oi INTEGER,
  volume INTEGER,
  flags TEXT,
  FOREIGN KEY(snapshot_id) REFERENCES snapshots(snapshot_id)
);

CREATE TABLE IF NOT EXISTS iv_points (
  iv_id INTEGER PRIMARY KEY DEFAULT nextval('iv_points_id_seq'),
  snapshot_id INTEGER NOT NULL,
  expiry DATE NOT NULL,
  delta_bucket TEXT NOT NULL,
  iv_mid DOUBLE PRECISION,
  iv_bid DOUBLE PRECISION,
  iv_ask DOUBLE PRECISION,
  solve_status TEXT NOT NULL,
  quality_score DOUBLE PRECISION,
  fit_model_id TEXT,
  fit_residual DOUBLE PRECISION,
  fit_support INTEGER,
  fit_confidence DOUBLE PRECISION,
  fit_reason_codes TEXT,
  FOREIGN KEY(snapshot_id) REFERENCES snapshots(snapshot_id)
);

CREATE TABLE IF NOT EXISTS surface_metrics (
  metric_id INTEGER PRIMARY KEY DEFAULT nextval('surface_metrics_id_seq'),
  snapshot_id INTEGER NOT NULL,
  expiry_bucket TEXT NOT NULL,
  atm_iv_mid DOUBLE PRECISION,
  rr25_mid DOUBLE PRECISION,
  rr10_mid DOUBLE PRECISION,
  fly25_mid DOUBLE PRECISION,
  fly10_mid DOUBLE PRECISION,
  term_slope_mid DOUBLE PRECISION,
  atm_iv_worst DOUBLE PRECISION,
  rr25_worst DOUBLE PRECISION,
  rr10_worst DOUBLE PRECISION,
  fly25_worst DOUBLE PRECISION,
  fly10_worst DOUBLE PRECISION,
  term_slope_worst DOUBLE PRECISION,
  fit_model_id TEXT,
  fit_residual DOUBLE PRECISION,
  fit_support INTEGER,
  fit_confidence DOUBLE PRECISION,
  surface_quality_score DOUBLE PRECISION,
  qc_pass BOOLEAN,
  qc_reason_codes TEXT,
  FOREIGN KEY(snapshot_id) REFERENCES snapshots(snapshot_id)
);

CREATE TABLE IF NOT EXISTS regime_state (
  regime_date DATE PRIMARY KEY,
  vix_percentile DOUBLE PRECISION NOT NULL,
  rv20_percentile DOUBLE PRECISION NOT NULL,
  drawdown_percent DOUBLE PRECISION NOT NULL,
  regime_score INTEGER NOT NULL,
  regime_label TEXT NOT NULL,
  regime_config_hash TEXT,
  vix_spot DOUBLE PRECISION,
  rv20_value DOUBLE PRECISION,
  drawdown_value DOUBLE PRECISION,
  event_score DOUBLE PRECISION,
  stress_proxy_score DOUBLE PRECISION,
  decomposition TEXT
);

CREATE TABLE IF NOT EXISTS regime_snapshot_labels (
  snapshot_id INTEGER PRIMARY KEY,
  run_id INTEGER,
  regime_date DATE NOT NULL,
  regime_label TEXT NOT NULL,
  regime_config_hash TEXT,
  decomposition TEXT,
  FOREIGN KEY(snapshot_id) REFERENCES snapshots(snapshot_id)
);

CREATE TABLE IF NOT EXISTS alerts (
  alert_id INTEGER PRIMARY KEY DEFAULT nextval('alerts_id_seq'),
  snapshot_id INTEGER NOT NULL,
  alert_type TEXT NOT NULL,
  expiry_bucket TEXT NOT NULL,
  severity DOUBLE PRECISION NOT NULL,
  zscore_mid DOUBLE PRECISION NOT NULL,
  zscore_worst DOUBLE PRECISION NOT NULL,
  tradability_score DOUBLE PRECISION NOT NULL,
  confidence_tier TEXT NOT NULL,
  persistence_count INTEGER NOT NULL,
  regime_label TEXT NOT NULL,
  signal_state TEXT NOT NULL,
  transition_reason_code TEXT,
  explain TEXT,
  FOREIGN KEY(snapshot_id) REFERENCES snapshots(snapshot_id)
);

CREATE TABLE IF NOT EXISTS alert_outcomes (
  alert_id INTEGER PRIMARY KEY,
  horizon_days INTEGER NOT NULL,
  outcome_label TEXT NOT NULL,
  resolved_snapshot_id INTEGER,
  resolved_ts TIMESTAMP,
  base_metric_value DOUBLE PRECISION,
  resolved_metric_value DOUBLE PRECISION,
  reversion_ratio DOUBLE PRECISION,
  outcome_source TEXT,
  evaluated_at TIMESTAMP NOT NULL,
  FOREIGN KEY(alert_id) REFERENCES alerts(alert_id)
);

CREATE TABLE IF NOT EXISTS trade_ideas (
  trade_id INTEGER PRIMARY KEY DEFAULT nextval('trade_ideas_id_seq'),
  alert_id INTEGER NOT NULL,
  template TEXT NOT NULL,
  legs TEXT NOT NULL,
  price_mid DOUBLE PRECISION,
  price_worst DOUBLE PRECISION,
  greeks TEXT,
  scenarios TEXT,
  risk_flags TEXT,
  FOREIGN KEY(alert_id) REFERENCES alerts(alert_id)
);

CREATE INDEX IF NOT EXISTS idx_iv_points_snapshot_id ON iv_points(snapshot_id);
CREATE INDEX IF NOT EXISTS idx_surface_metrics_snapshot_id ON surface_metrics(snapshot_id);
CREATE INDEX IF NOT EXISTS idx_alert_outcomes_label ON alert_outcomes(outcome_label);
