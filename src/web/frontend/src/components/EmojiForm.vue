<template> 
    <el-popover placement="bottom" trigger="click" width="360px">
        <Picker :data="emojiIndex" set="twitter" @select="onSelectEmoji" />
        <el-button slot="reference" class="emoji-button"> <emoji :data="emojiIndex" :emoji="rawEmoji" set="twitter" :size="20" /> </el-button>
    </el-popover>
</template>

<script>
import data from "emoji-mart-vue-fast/data/all.json";
// Import default CSS
import "emoji-mart-vue-fast/css/emoji-mart.css";

import { Emoji, Picker, EmojiIndex } from "emoji-mart-vue-fast";

// Create emoji data index.
// We can change it (for example, filter by category) before passing to the component.
let emojiIndex = new EmojiIndex(data);

export default {
    props: ["rawEmoji"],
    name: "emoji-form",
    components: {
        Picker,
        Emoji
    },
    data() {
        return {
            emojiIndex: emojiIndex
        }
    },
    methods: {
        onSelectEmoji(emoji) {
            this.$emit("select", emoji.native);
        }
    }
}
</script>

<style scoped>
.emoji-button {
    padding: 8px 8px;
}
</style>