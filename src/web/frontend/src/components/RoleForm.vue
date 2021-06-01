<template>
    <section class="role-parent">
        <div class="summary">
            <input :value="roleData.summary" @change="onSummaryChange" placeholder="ロールの概要" class="role-summary" />
            <el-button icon="el-icon-delete" class="delete-button" @click="onRoleDelete" circle></el-button>
        </div>
        <role-select :roles="roles" class="role-select" @select="onRoleSelect" :selectedRoleID="roleData.id.rawID" />
        <div class="emoji">
            <emoji-form @select="onSelectEmoji" class="role-emoji" :rawEmoji="roleData.emoji"/> <p class="please-press"> を押してください。 </p>
        </div>
    </section>
</template>

<script>

/* roles protocol */
/*
    id: {
        color: "",
        name: ""
    }
*/
import EmojiForm from './EmojiForm';
import RoleSelect from './RoleSelect';

export default {
    name: "role-form",
    props: ["roles", "roleData"],
    components: { 
        EmojiForm,
        RoleSelect 
    },
    methods: {
        onSelectEmoji(emoji) {
            this.$emit("change", { id: this.roleData.id, emoji, summary: this.roleData.summary });
        },
        onRoleSelect(id) {
            this.$emit("set-id", { id: this.roleData.id, newerID: id });
        },
        onSummaryChange(event) {
            const summary = event.target.value;
            this.$emit("change", { id: this.roleData.id, emoji: this.roleData.emoji, summary });
        },
        onRoleDelete() {
            this.$emit("remove", { rawID: this.roleData.id.rawID });
        },
    }
}
</script>

<style scoped>
.summary {
    grid-row: 1;
    grid-column: 1;

    display: grid;
    grid-template-columns: calc(100% - 2.8em) 2.8em;
    grid-template-rows: 2.8em;
}

.role-summary {
    color: white;
    border: none;
    background-color: inherit;
    font-size: 108%;
    font-family: sans-serif;
    font-weight: bold;

    grid-row: 1;
    grid-column: 1;
}

.p {
    color: white;
}

.role-parent {
    display: grid;
    grid-template-columns: 100%;
    grid-auto-rows: 2.8em;
}

.role-select {
    margin-left: 3px;
    width: 15em;
    grid-row: 2;
    grid-column: 1;
}

.emoji {
    grid-row: 3;
    grid-column: 1;
    display: flex;
    gap: 5px;
    align-items: center;
}

.role-emoji {
    margin-left: 3px;
}

.please-press {
    color: white;
}

.el-button {
    background-color: #2f3136;
}

.delete-button {
    grid-row: 1;
    grid-column: 2;
}
</style>