<script setup>
import { ref, computed, watch, nextTick, onMounted } from "vue";
import { useRouter } from "vue-router";
import { resCheck, authCheck } from "#/check";
import storage from "#/storage";
import { useAlert } from "#/alert";
import { markdown } from "#/markdown";

const { alerts, awaitAlert, shows } = useAlert();
const router = useRouter();

const currentChatType = ref("daily");
const userInput = ref("");
const isTyping = ref(false);
const messageContainer = ref(null);

const chatOptions = [
  { label: "今日", value: "daily" },
  { label: "长期", value: "long-term" },
];

const messages = ref({
  daily: [],
  "long-term": [],
});

const currentMessages = computed(() => {
  return messages.value[currentChatType.value] || [];
});

const greetings = [
  "今天你想和我分享什么？",
  "此时此刻，你的心情如何？",
  "有什么想聊聊的吗？我一直都在。",
  "今天过得怎么样？愿闻其详。",
  "看到你很高兴，今天有什么新鲜事吗？",
];

const addGreeting = () => {
  const greeting = greetings[Math.floor(Math.random() * greetings.length)];
  messages.value[currentChatType.value] = [
    {
      role: "assistant",
      content: greeting,
      time: formatTime(new Date().toISOString()),
    },
  ];
};

const formatTime = (dateStr) => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
};

const scrollToBottom = async () => {
  await nextTick();
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight;
  }
};

const fetchHistory = async () => {
  const token = await storage.get("token");
  if (!token) {
    router.push("/login");
    return;
  }

  fetch(`/api/chat/history?session_type=${currentChatType.value}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
    .then(resCheck)
    .then(authCheck)
    .then((res) => {
      if (res.success && res.data && res.data.length > 0) {
        messages.value[currentChatType.value] = res.data.map((msg) => ({
          role: msg.role,
          content: msg.content,
          time: formatTime(msg.created_at),
        }));
        scrollToBottom();
      } else {
        addGreeting();
      }
    })
    .catch((error) => {
      console.error("获取历史记录失败:", error);
      shows("加载失败", "无法获取历史对话", "error");
    });
};

onMounted(() => {
  fetchHistory();
});

watch(currentChatType, (newVal, oldVal) => {
  if (!newVal) {
    currentChatType.value = oldVal || "daily";
    return;
  }
  if (messages.value[currentChatType.value].length === 0) {
    fetchHistory();
  } else {
    scrollToBottom();
  }
});

const confirmClearHistory = async () => {
  const confirmed = await awaitAlert(
    "确认清空",
    `确定要清空当前的${currentChatType.value === "daily" ? "今日" : "长期"}对话记录吗？`,
    { accept: "确认清除", reject: "取消" },
  );

  if (confirmed) {
    const token = await storage.get("token");
    if (!token) return;

    fetch("/api/chat/delete", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        session_type: currentChatType.value,
      }),
    })
      .then(resCheck)
      .then(authCheck)
      .then((res) => {
        if (res.success) {
          messages.value[currentChatType.value] = [];
          addGreeting();
          shows("清除成功", "对话历史已清空");
        }
      })
      .catch((error) => {
        console.error("清除历史失败:", error);
        alerts("清除失败", "请稍后再试");
      });
  }
};

const sendMessage = async () => {
  if (!userInput.value.trim() || isTyping.value) return;

  const token = await storage.get("token");
  if (!token) {
    alerts("未登录", "请先登录后再聊天");
    return;
  }

  const content = userInput.value;
  const now = new Date().toISOString();

  // 立即在 UI 显示用户消息
  const userMsg = {
    role: "user",
    content: content,
    time: formatTime(now),
  };
  messages.value[currentChatType.value].push(userMsg);

  userInput.value = "";
  isTyping.value = true;
  scrollToBottom();

  fetch("/api/chat/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      message: content,
      session_type: currentChatType.value,
    }),
  })
    .then(resCheck)
    .then(authCheck)
    .then((res) => {
      isTyping.value = false;
      if (res.success && res.data) {
        const aiMsg = {
          role: res.data.role,
          content: res.data.content,
          time: formatTime(res.data.created_at),
        };
        messages.value[currentChatType.value].push(aiMsg);
        scrollToBottom();
      } else {
        shows("发送失败", res.message || "服务器异常", "error");
      }
    })
    .catch((error) => {
      isTyping.value = false;
      console.error("发送消息失败:", error);
      shows("发送失败", "网络连接错误", "error");
    });
};
</script>

<template>
  <div class="flex flex-column h-full overflow-hidden">
    <PageHeader
      class="flex-shrink-0"
      title="AI 伙伴"
      :subtitle="currentChatType === 'daily' ? '今日专属' : '深层共鸣'"
    >
      <template #controls>
        <div class="flex gap-2 align-items-center">
          <SelectButton
            v-model="currentChatType"
            :options="chatOptions"
            optionLabel="label"
            optionValue="value"
            aria-labelledby="basic"
            size="small"
            :allowEmpty="false"
          />
          <Button
            icon="pi pi-trash"
            severity="secondary"
            text
            rounded
            @click="confirmClearHistory"
            v-tooltip.bottom="'清除历史'"
          />
        </div>
      </template>
    </PageHeader>
    <div
      class="chat-page flex-1 flex flex-column bg-surface-50 overflow-hidden"
    >
      <div
        class="chat-messages flex-1 overflow-y-auto p-4 flex flex-column gap-4"
        ref="messageContainer"
      >
        <div
          v-for="(msg, index) in currentMessages"
          :key="index"
          :class="[
            'message-bubble p-3 max-w-85 shadow-2 transition-all',
            msg.role === 'user'
              ? 'self-end bg-primary text-primary-contrast border-round-left-2xl border-round-top-2xl'
              : 'self-start bg-surface-0 text-surface-900 border-round-right-2xl border-round-top-2xl',
          ]"
        >
          <div v-if="msg.role === 'user'" class="text-sm line-height-3">
            {{ msg.content }}
          </div>
          <div
            v-else
            class="markdown-content text-sm line-height-3"
            v-html="markdown(msg.content)"
            v-cached-images
          ></div>
          <div
            class="text-xxs mt-2 opacity-60 text-right flex align-items-center justify-content-end"
          >
            <i
              v-if="msg.role === 'assistant'"
              class="pi pi-sparkles mr-1"
              style="font-size: 0.5rem"
            ></i>
            {{ msg.time }}
          </div>
        </div>

        <div
          v-if="isTyping"
          class="message-bubble p-3 max-w-85 shadow-2 transition-all self-start bg-surface-0 text-surface-900 border-round-right-2xl border-round-top-2xl"
        >
          <span class="animate-pulse flex align-items-center">
            <i class="pi pi-spin pi-spinner mr-2"></i>
            AI 正在思考...
          </span>
        </div>
      </div>

      <footer class="px-4 pt-2 pb-2 bg-surface-0 shadow-5 z-2">
        <div class="flex gap-3 align-items-center">
          <Textarea
            v-model="userInput"
            autoResize
            rows="1"
            @keydown.enter.exact.prevent="sendMessage"
            placeholder="聊聊你的心情..."
            class="flex-1 border-round-3xl bg-surface-50 px-4 py-2"
            style="resize: none; max-height: 200px"
          />
          <Button
            icon="pi pi-send"
            rounded
            @click="sendMessage"
            :disabled="!userInput.trim() || isTyping"
            class="shadow-2 w-3rem h-3rem"
          />
        </div>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.text-xxs {
  font-size: 0.65rem;
}

.max-w-85 {
  max-width: 85%;
}

.message-bubble {
  word-wrap: break-word;
}

:deep(.markdown-content) p {
  margin: 0 0 0.5rem 0;
}

:deep(.markdown-content) p:last-child {
  margin-bottom: 0;
}

:deep(.markdown-content) ul,
:deep(.markdown-content) ol {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

:deep(.markdown-content) code {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: monospace;
}

:deep(.markdown-content) pre {
  background-color: #f4f4f4;
  padding: 0.75rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0.5rem 0;
}

:deep(.markdown-content) pre code {
  background-color: transparent;
  padding: 0;
}

:deep(.markdown-content) blockquote {
  border-left: 4px solid #ddd;
  padding-left: 1rem;
  margin: 0.5rem 0;
  color: #666;
}

:deep(.markdown-content) img {
  max-width: 100%;
  border-radius: 4px;
}

:deep(.markdown-content) a {
  color: var(--p-primary-color);
  text-decoration: underline;
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
