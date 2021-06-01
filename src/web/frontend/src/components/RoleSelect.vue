<template>
    <el-select :value="selectedRoleName" @change="onRoleChange">
        <el-option disabled value="">未選択</el-option>
        <el-option v-for="(role, id) in roles" :key="id" :value="id">
            <span :style="{ color: role.color }"> @{{role.name}} </span>
        </el-option>
    </el-select>
</template>

<script>

/* roles protocol */
/*
    id: {
        color: "",
        name: ""
    }
*/


export default {
    name: "role-select",
    props: ["roles", "selectedRoleID"],
    data() {
        return {
        }
    },
    computed: {
        selectedRoleName() {
            return "@" + (this.roles[this.selectedRoleID] || { name: "未選択" }).name;
        }
    },
    methods: {
        onRoleChange(id) {
            this.$emit("select", id);
        }
    }
}
</script>