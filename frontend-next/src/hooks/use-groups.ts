import { apiFetch } from "@/lib/api-client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

export interface Group {
  id: number;
  name: string;
  description?: string;
  type: "servers" | "notes" | "snippets" | "inventory";
  color: string;
  created_by?: number;
  created_at: string;
  updated_at: string;
  item_count?: number;
}

export function useGroups(type?: Group["type"]) {
  return useQuery<Group[]>({
    queryKey: ["groups", type],
    queryFn: () => {
      const url = type ? `/api/groups?type=${type}` : "/api/groups";
      return apiFetch<Group[]>(url);
    },
  });
}

export function useGroup(id: number) {
  return useQuery<Group>({
    queryKey: ["groups", id],
    queryFn: () => apiFetch<Group>(`/api/groups/${id}`),
    enabled: !!id,
  });
}

export function useCreateGroup() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: Omit<Group, "id" | "created_at" | "updated_at">) =>
      apiFetch<{ success: boolean; id: number }>("/api/groups", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["groups"] });
    },
  });
}

export function useUpdateGroup() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: Partial<Pick<Group, "name" | "description" | "color">>;
    }) =>
      apiFetch<{ success: boolean }>(`/api/groups/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["groups"] });
    },
  });
}

export function useDeleteGroup() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) =>
      apiFetch<{ success: boolean }>(`/api/groups/${id}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["groups"] });
    },
  });
}
