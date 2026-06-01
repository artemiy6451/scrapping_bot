import { api } from "./client";

export interface CommentForModeration {
  comment_id: number;
  group_name: string;
  post_text: string;
  comment_text: string;
  link: string;
}

export async function getNextComment() {
  const res = await api.get<CommentForModeration>("/comments/next");
  return res.data;
}

export async function labelComment(payload: {
  comment_id: number;
  label: string;
}) {
  await api.post("/comments/label", payload);
}
