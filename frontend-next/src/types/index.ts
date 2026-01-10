export type Role = "admin" | "user" | "public" | string;

export type SessionUser = {
  username?: string;
  role?: Role;
  permissions?: string[];
  theme_preference?: "light" | "dark" | "system";
};

export type Server = {
  id: number;
  name: string;
  host: string;
  description?: string;
  status?: string;
  cpu?: number;
  memory?: number;
  disk?: number;
  tags?: string;
  last_check?: string;
};

export type ServerNote = {
  id: number;
  server_id: number;
  content: string;
  created_at?: string;
  updated_at?: string;
};

export type StatsOverview = {
  total_servers: number;
  online_servers: number;
  offline_servers: number;
  alerts_last_24h?: number;
};

export type SSHKey = {
  id: string;  // UUID instead of number
  name: string;
  description?: string;
  public_key?: string;
  key_type?: string;  // rsa, ed25519, ecdsa, etc.
  fingerprint?: string;
  created_by?: string;
  created_at?: string;
  deleted_at?: string;
};

export type EmailConfig = {
  enabled: boolean;
  smtp_host?: string;
  smtp_port?: number;
  smtp_username?: string;
  smtp_password?: string;
  recipients?: string[];
};

export type DomainSettings = {
  domain_name: string;
  ssl_enabled: number;
  ssl_type: string;
  cert_path?: string;
  key_path?: string;
  auto_renew?: number;
};

export type Alert = {
  id: number;
  server_id?: number;
  message: string;
  severity?: string;
  is_read?: number;
  created_at?: string;
};

export type User = {
  id: number;
  username: string;
  email?: string;
  role: Role;
  avatar_url?: string;
  permissions?: string[];
};

export type TerminalSession = {
  id: string;
  server_id: number;
  user_id: number;
  username?: string;
  server_name?: string;
  ssh_key_id?: string;
  ssh_key_name?: string;
  status: "active" | "closed" | "timeout" | "error";
  started_at: string;
  ended_at?: string;
  last_activity?: string;
};

export type AuditLog = {
  id: number;
  user_id: number;
  action: string;
  target_type: string;
  target_id: string;
  meta?: Record<string, unknown>;
  meta_json?: string;
  ip?: string;
  user_agent?: string;
  created_at: string;
  username?: string;
  server_name?: string;
};

export type ServerInventory = {
  server_id: number;
  collected_at: string;
  inventory: {
    collected_at: string;
    os: {
      name: string;
      version: string;
      pretty_name?: string;
    };
    kernel: string;
    hostname: string;
    uptime: {
      uptime_seconds?: number;
      uptime_human?: string;
      uptime_since?: string;
    };
    cpu: {
      model?: string;
      cores: number;
    };
    memory: {
      total_mb: number;
      used_mb?: number;
      available_mb?: number;
      used_percent?: number;
    };
    disk: {
      total_gb?: number;
      used_gb?: number;
      available_gb?: number;
      used_percent?: number;
    };
    network: {
      primary_ip?: string;
      interfaces?: string[];
    };
    packages?: Array<{ type: string; count: number }>;
    services?: Array<{ type: string; running_count: number }>;
    error?: string;
  };
};

export type RecentActivity = {
  activities: Array<{
    id: string;
    user_id: number;
    username?: string;
    action: string;
    target_type: string;
    target_id: string;
    server_name?: string;
    meta?: Record<string, unknown>;
    created_at: string;
  }>;
  count: number;
};

export type Task = {
  id: string;
  server_id: number;
  user_id: number;
  command: string;
  status: "queued" | "running" | "success" | "failed" | "timeout" | "cancelled";
  exit_code?: number;
  stdout?: string;
  stderr?: string;
  timeout_seconds: number;
  store_output: number;
  started_at?: string;
  finished_at?: string;
  created_at: string;
};

export type Webhook = {
  id: string;
  name: string;
  url: string;
  secret?: string;
  enabled: number;
  event_types: string[] | null;
  retry_max: number;
  timeout: number;
  created_at: string;
  updated_at: string;
  last_triggered_at?: string;
};

export type WebhookDelivery = {
  id: string;
  webhook_id: string;
  event_id: string;
  event_type: string;
  status: "success" | "failed" | "pending";
  status_code?: number;
  response_body?: string;
  error?: string;
  attempt: number;
  delivered_at: string;
};
