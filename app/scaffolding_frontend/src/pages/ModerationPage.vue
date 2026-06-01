<template>
  <div class="container">

    <h2>Moderation Tool</h2>

    <div v-if="loading">Loading...</div>

    <div v-else-if="!current">
      No comments
    </div>

    <div v-else>

      <div class="context">
        <h3>Post ({{ current.group_name }})</h3>
        <p>{{ current.post_text }}</p>
        <a :href="current.link" target="_blank">Open post</a>
      </div>

      <hr />

      <div class="comment">
        <h3>Comment</h3>
        <p>{{ current.comment_text }}</p>
      </div>

      <div class="buttons">
        <button @click="submit('neutral')">1 Neutral</button>
        <button @click="submit('extremism')">2 Extremism</button>
        <button @click="submit('skip')">3 Skip</button>
      </div>

    </div>

  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, onBeforeUnmount } from "vue";
import { getNextComment, labelComment } from "../api/comments";

const current = ref<any>(null);
const loading = ref(false);

async function loadNext() {
  loading.value = true;
  try {
    current.value = await getNextComment();
  } catch {
    current.value = null;
  }
  loading.value = false;
}

async function submit(label: string) {
  if (!current.value) return;

  if (label !== "skip") {
    await labelComment({
      comment_id: current.value.comment_id,
      label,
    });
  }

  await loadNext();
}

function onKey(e: KeyboardEvent) {
  if (e.key === "1") submit("neutral");
  if (e.key === "2") submit("extremism");
  if (e.key === "3") submit("skip");
}

onMounted(() => {
  loadNext();
  window.addEventListener("keydown", onKey);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", onKey);
});
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: sans-serif;
}

.context {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 8px;
}

.comment {
  margin-top: 20px;
  font-size: 18px;
}

.buttons {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

button {
  padding: 10px;
  cursor: pointer;
}
</style>
