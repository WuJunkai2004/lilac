<template>
  <div class="flex flex-column h-full overflow-hidden">
    <PageHeader
      class="flex-shrink-0"
      title="AI 伙伴"
      :subtitle="currentChatType === 'daily' ? '今日专属' : '深层共鸣'"
    >
      <template #controls>
        <SelectButton
          v-model="currentChatType"
          :options="chatOptions"
          optionLabel="label"
          optionValue="value"
          aria-labelledby="basic"
          size="small"
        />
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
          <div class="text-sm line-height-3">{{ msg.content }}</div>
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
          class="self-start bg-surface-0 text-surface-500 p-3 border-round-right-2xl border-round-top-2xl shadow-1 italic text-sm"
        >
          <span class="animate-pulse flex align-items-center">
            <i class="pi pi-spin pi-spinner mr-2"></i>
            AI 正在思考...
          </span>
        </div>
      </div>

      <footer class="p-4 bg-surface-0 shadow-5 z-2">
        <div class="flex gap-3 align-items-center">
          <InputText
            v-model="userInput"
            @keyup.enter="sendMessage"
            placeholder="聊聊你的心情..."
            class="flex-1 border-round-3xl bg-surface-50 px-4"
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

<script setup>
import { ref, computed, watch, nextTick } from "vue";

const currentChatType = ref("daily");
const userInput = ref("");
const isTyping = ref(false);
const messageContainer = ref(null);

const chatOptions = [
  { label: "今日", value: "daily" },
  { label: "长期", value: "long-term" },
];

const dailyMessages = ref([
  {
    role: "assistant",
    content: "嗨！我是你今天的 AI 伙伴。今天阳光不错，你感觉怎么样？",
    time: "09:00",
  },
]);

const longTermMessages = ref([
  {
    role: "assistant",
    content: "好久不见。我一直在这里听你倾诉。你最近的情绪似乎有所好转。",
    time: "昨天",
  },
]);

const currentMessages = computed(() => {
  return currentChatType.value === "daily"
    ? dailyMessages.value
    : longTermMessages.value;
});

const scrollToBottom = async () => {
  await nextTick();
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight;
  }
};

watch(
  currentMessages,
  () => {
    scrollToBottom();
  },
  { deep: true },
);

const sendMessage = async () => {
  if (!userInput.value.trim()) return;

  const now = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
  const userMsg = { role: "user", content: userInput.value, time: now };

  if (currentChatType.value === "daily") {
    dailyMessages.value.push(userMsg);
  } else {
    longTermMessages.value.push(userMsg);
  }

  const userText = userInput.value;
  userInput.value = "";
  isTyping.value = true;

  // Mock AI response
  setTimeout(() => {
    isTyping.value = false;
    const aiMsg = {
      role: "assistant",
      content: generateMockAIResponse(userText),
      time: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };

    if (currentChatType.value === "daily") {
      dailyMessages.value.push(aiMsg);
    } else {
      longTermMessages.value.push(aiMsg);
    }
    scrollToBottom();
  }, 1200);
};

const generateMockAIResponse = (text) => {
  if (text.includes("吃") || text.includes("饿") || text.includes("美食")) {
    const foods = [
      "二食堂的红烧肉",
      "清真餐厅的拉面",
      "学府餐厅的瓦罐汤",
      "三食堂的烤鱼",
      "丁香园的自选餐",
    ];
    return `既然你提到了美食，今天不如试试${foods[Math.floor(Math.random() * foods.length)]}吧？心情不好的时候，美食最能慰藉人心。`;
  }

  if (text.includes("去哪") || text.includes("活动") || text.includes("散步")) {
    const spots = [
      "图书馆五楼的露台",
      "荷花池边的长椅",
      "中心操场的塑胶跑道",
      "体育馆后的丁香林",
    ];
    return `我推荐你去${spots[Math.floor(Math.random() * spots.length)]}走走。那里的环境非常适合放松和沉淀思绪。`;
  }

  const responses = [
    "我听到了。有时候我们需要静静地感受这种情绪。",
    "这听起来很有趣！也许我们可以聊聊更多关于这件事的细节？",
    "没关系，每个人都会有这样的时候。要不要试试深呼吸？",
    "我很理解你的感受。在这个校园里，你并不孤单。",
    "今天又是新的一天，希望我的陪伴能给你带来一点温暖。",
  ];
  return responses[Math.floor(Math.random() * responses.length)];
};
</script>

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
