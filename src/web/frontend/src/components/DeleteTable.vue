<template>
    <el-table :data="embedsToDeleteDialog" @selection-change="onChangeSelection" ref="multipleTable">
        <el-table-column
            type="selection"
            width="55">
        </el-table-column>
        <el-table-column
            prop="messageId"
            label="メッセージID"
            width="200">
        </el-table-column>
        <el-table-column
            property="summary"
            label="概要"
            width="250">
        </el-table-column>
        <el-table-column
            property="description"
            label="説明"
            width="300">
        </el-table-column>
    </el-table>
</template>

<script>
export default {
    props: ["embedsToDeleteDialog", "multipleSelection"],
    methods: {
        onChangeSelection(val) {
            this.$emit("change", val);
        }
    }
}
</script>