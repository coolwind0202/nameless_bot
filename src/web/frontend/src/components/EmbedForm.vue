<template>
    <form class="embed-parent" :style="{ borderLeftColor:  roleMessageData.color }">
        <div class="top-level-form">
            <input :value="summary" @change="onEditSummary" placeholder="ロールメッセージの概要" class="text summary"/>
            <el-color-picker v-model="color" @change="onChangeColor" class="color"></el-color-picker>
        </div>
        <textarea :value="description" @change="onEditDescription" placeholder="ロールメッセージの説明欄" class="text description"></textarea>
        <div class="roles-parent">
            <role-form :roles="roles" :roleData="role" class="role" v-for="role in roleMessageData.roles"
                :key="role.id.objID" @change="onEditRole" @remove="onRemoveRole" @set-id="onSetRoleID"/>
        </div>
        <el-button round @click="onAddRole" class="add-role-button"> ロールを追加する </el-button>
        <span></span>
        <el-button round @click="onPostRoleData" class="post-role-button" type="primary"> 投稿する </el-button>
    </form>
</template>

<script>
import RoleForm from './RoleForm';
// import { MessageBox } from 'element-ui';

// import RoleMessageData from '../classes/roleMessageData';
import RoleData from '../classes/roleData';
import ID from '../classes/id';
import axios from 'axios' // eslint-disable-line no-unused-vars

export default {
    name: "embed-form",
    props: ["roles", "roleMessageData"],
    components: {
        RoleForm,
    },
    data() {
        return {
            color: null,
            summary: "",
            description: ""
        }
    },
    methods: {
        onMessageDataEdit() {
            console.log("edit..")
            this.$emit("change", { 
                id: this.roleMessageData.id, 
                color: this.color, 
                summary: this.summary, 
                description: this.description, 
                roles: this.roleMessageData.roles
            });
        },
        onEditSummary(event) {
            this.summary = event.target.value;
            // this.$emit("change", { color: this.color, summary, description: this.description, roles: this.roleMessageData.roles });
            this.onMessageDataEdit();
        },
        onChangeColor() {
            // this.$emit("change", { color: this.color, summary: this.summary, description: this.description, roles: this.roleMessageData.roles });
            this.onMessageDataEdit();
        },
        onEditDescription(event) {
            this.description = event.target.value;
            // this.$emit("change", { color: this.color, summary: this.summary, description, roles: this.roleMessageData.roles });
            this.onMessageDataEdit();
        },
        onAddRole() {
            const copy = [...this.roleMessageData.roles];
            copy.push(
                new RoleData({
                    id: new ID(),
                    emoji: "😀",
                    summary: ""
                })
            );
            this.$emit("change", { ...this.roleMessageData, roles: copy });
        },

        onEditRole({ id, emoji, summary }) {
            console.log(id, emoji, summary);
            const copy = [...this.roleMessageData.roles];
            const roles = copy.map(role => {
                if (role.id.objID == id.objID) {
                    return { id, emoji, summary };
                } else return role;
            });
            this.$emit("change", { ...this.roleMessageData, roles });
        },

        onRemoveRole({ rawID }) {
            const copy = [...this.roleMessageData.roles];
            this.$emit("change", { ...this.roleMessageData, roles: copy.filter(role => role.id.rawID !== rawID) });
        },

        onSetRoleID({ id, newerID }) {
            console.log(id);
            const roles = this.roleMessageData.roles.map(role => {
                if (role.id.objID == id.objID) {
                    const copy = role.id.copy();
                    copy.setID(newerID);
                    return { ...role, id: copy };
                } else {
                    return role;
                }
            })

            this.$emit("change", { ...this.roleMessageData, roles });
        },
        onPostRoleData() {
            this.$emit("post", { id: this.roleMessageData.id });
        }


        /*
        addRoleForm() {
            console.log(this.roleCounter);
            const copy = {...this.userInputRoles};
            copy[this.roleCounter.toString()] = {
                roleId: null,
                emoji: "",
                summary: ""
            };
            this.userInputRoles = copy;
            this.roleCounter++;
        },
        onRoleEdit(roleNumber, roleId, emoji, summary) {
            roleNumber = roleNumber.toString();
            if (this.userInputRoles[roleNumber] !== undefined) {
                this.userInputRoles[roleNumber] = {
                    roleId, emoji, summary
                }
            }
        },
        onRoleDelete(roleNumber) {
            roleNumber = roleNumber.toString();
            const copy = {...this.userInputRoles};
            delete copy[roleNumber];
            this.userInputRoles = copy;
        },
        alert(s) {
            MessageBox.alert(s, {
                confirmButtonText: 'OK',
                callback: () => {}
            });
        },
        postRoleData() {
            const data = {
                ...this.form,
                roles: {}
            }
            if (!(data.summary && data.description && data.color)) {
                this.alert("メッセージ概要、メッセージ説明、埋め込みカラーはいずれも空でない必要があります。");
                return;
            }
            for (const key in this.userInputRoles) {
                const role = this.userInputRoles[key];
                data.roles[role.roleId] = {
                    emoji: role.emoji,
                    summary: role.summary
                }

                if (!(role.roleId && role.emoji && role.summary)) {
                    this.alert("ロール情報はいずれも空でない必要があります。");
                    return;
                }
            }
            console.log(data);
            axios.post("http://localhost:5000/api/roles", data).then(resp => {
                const messageId = Number(resp);
            })
            
        }
        */
    },
    created() {
        this.summary = this.roleMessageData.summary;
        this.color = this.roleMessageData.color;
        this.description = this.roleMessageData.description;
    }
}
</script>

<style scoped>
.embed-parent {
    width: 32em;
    background-color: #2f3136;
    border-left-width: 5px;
    border-left-style: solid;
    border-radius: 4px;

    padding-top: 15px;
    padding-left: 17px;
    padding-bottom: 17px;

    display: grid;
    grid-template-columns: 92%;
    grid-template-rows: repeat(2, 2.5em);
    gap: 0.5em;
}

.text {
    color: white;
    border: none;
    background-color: inherit;
    font-family: sans-serif;
}

.top-level-form {
    grid-column: 1;
    grid-row: 1;

    display: grid;
    grid-template-columns: 25em;
}

.summary {
    font-size: x-large;
    font-weight: bold;

    grid-column: 1;
}

.description {
    font-size: large;

    margin-left: 2px;
    grid-column: 1;
    grid-row: 2;
}

.color {
    grid-column: 2;
}

.roles-parent {
    grid-column: 1;
    grid-row: 3;
}

.add-role-button {
    grid-column: 1;
    grid-row: 4;
}

.post-role-button {
    grid-column: 1;
    grid-row: 5;
}
</style>
