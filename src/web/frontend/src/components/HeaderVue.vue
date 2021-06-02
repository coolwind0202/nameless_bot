<template>
    <el-header class="header">
        <img :src="avatar_url" />
        <el-button type="text"><el-link href="../logout/"> ログアウト </el-link></el-button>
    </el-header>
</template>

<script>
import axios from 'axios' // eslint-disable-line no-unused-vars
export default {
    name: "header-vue",
    data() {
        return {
            avatar_url: "",
            username: ""
        }
    },
    created() {
        axios.get("https://118.27.109.186/api/user").then(resp => {
            this.avatar_url = resp.data["avatar_url"];
            this.username = resp.data["username"];
        })
    }
}
</script>

<style scoped>
.header {
    width: 100%;
    height: 5.7em!important;
    position: fixed;
    top: 0;
    left: 0;
    background-color: #292b2f;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-end;
    gap: 14px;
    z-index: 1;
}

a {
    color: #d6d7d8;
}

img {
    height: 4.2em;
    width: 4.2em;
    border-radius: 2.1em;
}

a, img {
    display: inline-flex;
}
</style>
