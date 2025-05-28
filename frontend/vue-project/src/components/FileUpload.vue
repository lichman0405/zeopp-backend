<template>
  <div class="file-upload">
    <h3>1. Upload Structure File</h3>
    <input type="file" @change="handleFileChange" accept=".cif,.cssr,.pdb">
    <p v="if_file_selected">Selected file: {{ selectedFile?.name }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const selectedFile = ref(null);
const emit = defineEmits(['file-selected']);

const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    selectedFile.value = file;
    emit('file-selected', file);
  }
};
</script>

<style scoped>
.file-upload {
  border: 1px solid #ddd;
  padding: 15px;
  margin-bottom: 20px;
  border-radius: 5px;
  background-color: #f9f9f9;
}
input[type="file"] {
  margin-top: 10px;
}
p {
  margin-top: 10px;
  font-size: 0.9em;
  color: #333;
}
</style>
