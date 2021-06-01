<template>
    <el-main class="margin" v-loading.fullscreen.lock="loading"
        element-loading-text="Loading..."
        element-loading-spinner="el-icon-loading"
        element-loading-background="rgba(0, 0, 0, 0.8)">
        <h1> 【WHL】 White-Lucida Control Panel </h1>
        <div class="forms">
            <embed-form :roles="selectableRoles" v-for="embed in dataOfEmbeds" :key="embed.id.objID" :roleMessageData="embed" 
                @change="onMessageDataEdit" @post="onSendMessageData" />
        </div>
        <el-button type="primary" icon="el-icon-plus" @click="appendNewEmbed">New</el-button>
    </el-main>
</template>

<script>
import EmbedForm from './EmbedForm';
import { MessageBox } from 'element-ui';

import RoleMessageData from '../classes/roleMessageData';
import RoleData from '../classes/roleData';
import ID from '../classes/id';
import axios from 'axios' // eslint-disable-line no-unused-vars

export default {
    name: "main-vue",
    components: {
        EmbedForm
    },
    data() {
        return {
            selectableRoles: {},
            dataOfEmbeds: [],
            loaded: {
                roles: false,
                roleMessages: false
            },
            loading: true
        }
    },
    methods: {
        onMessageDataEdit({ id, summary, description, roles, color }) {
            console.log(id, summary, description, roles, color);
            const copy = [ ...this.dataOfEmbeds ];
            this.dataOfEmbeds = copy.map(embed => {
                if (embed.id == id) {
                    return { id, summary, description, roles, color }
                } else {
                    return embed;
                }
            });
        },
        alert(content) {
            MessageBox.alert(content, {
                confirmButtonText: 'OK'
            });
        },
        sendData(embed) {
            if (!(embed.summary && embed.description && embed.color)) {
                this.alert("メッセージ概要、メッセージ説明、埋め込みカラーはいずれも空でない必要があります。");
                return;
            }
            if (embed.roles.length == 0) {
                this.alert("1つ以上ロールを追加してください。");
                return;
            }
            for (const role of embed.roles) {
                if (!role.id.isDiscordID) {
                    this.alert("Discord上のロールを選択している必要があります。");
                    return;
                }
                if (!(role.summary && role.emoji)) {
                    this.alert("ロール絵文字とロール概要は空でない必要があります。");
                    return;
                }
            }
            axios.post("http://localhost:5000/api/roles", embed).then(resp => {
                console.log(resp);
                if (!embed.id.isDiscordID) {
                    const newEmbedData = this.dataOfEmbeds.map(target => {
                        if (target.id.objID == embed.id.objID) {
                            const copy = embed.id.copy();
                            copy.setID(resp.data); // eslint-disable-line
                            return { ...target, id: copy };
                        } else {
                            return target;
                        }
                    })
                    this.dataOfEmbeds = newEmbedData;
                    this.alert("Discordにメッセージが投稿されました。");
                    return;
                }
                this.alert("Discordのメッセージが編集されました。");
            });
        },
        onSendMessageData({ id }) {
            // const copy = { ...this.dataOfEmbeds };
            // 送信処理
            console.log(id);
            this.dataOfEmbeds.forEach(embed => {
                if (embed.id.objID == id.objID) {
                    this.sendData(embed);
                }
            })
        },
        createNewEmbed() {
            return new RoleMessageData({
                id: new ID(),
                summary: "",
                description: "",
                roles: [],
                color: null
            });
        },
        appendNewEmbed() {
            this.dataOfEmbeds = [ ...this.dataOfEmbeds, this.createNewEmbed() ];
        }
    },
    created() {

        axios.get("http://localhost:5000/api/roledata").then(resp => {
            console.log(resp.data);
            this.selectableRoles = resp.data;

            this.loaded.roles = true;
            if (this.loaded.roleMessages) {
               this.loading = false;
            }
        });

        axios.get("http://localhost:5000/api/roles").then(resp => {
            console.log(resp.data);
            const embeds = [];
            for (const messageData of resp.data) {
                const roles = [];
                for (const roleData of messageData.roles) {
                    roles.push(
                        new RoleData({
                            id: new ID(roleData.role_id),
                            emoji: roleData.role_emoji,
                            summary: roleData.role_summary
                        })
                    );
                }
                
                embeds.push(
                    new RoleMessageData({
                        id: new ID(messageData.message_id),
                        summary: messageData.summary,
                        description: messageData.description,
                        color: messageData.color_value,
                        roles: roles
                    })
                );
            }
            this.dataOfEmbeds = embeds;
            this.loaded.roleMessages = true;

            if (this.loaded.roles) {
                this.loading = false;
            }
        });
    }
}
</script>

<style scoped>
.margin {
    margin-top: 6em;
    text-align: center;
}

h1 {
    color: white;
    font-family: "Helvetica Neue",Helvetica,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","微软雅黑",Arial,sans-serif;
}

.forms {
    display: flex;
    gap: 15px;
    align-items: flex-start;
    flex-wrap: wrap;
}
</style>