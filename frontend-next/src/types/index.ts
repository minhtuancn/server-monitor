export type Role = "admin" | "user" | "public" | string;

export type SessionUser = {
  username?: string;
  role?: Role;
  permissions?: string[];
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
  username?: string;
  action: string;
  target_type?: string;
  target_id?: string;
  meta_json?: string;
  ip?: string;
  user_agent?: string;
  created_at: string;
};
