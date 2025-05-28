<template>
  <div class="results-display">
    <h3>4. Results</h3>
    <div v-if="!analysisResult || analysisResult.status === 'idle'">
      <p>Results will appear here once an analysis is run.</p>
    </div>
    <div v-else-if="analysisResult.status === 'loading'">
      <p>Loading results...</p>
    </div>
    <div v-else-if="analysisResult.status === 'success'">
      <h4>Analysis Successful</h4>
      <pre v-if="typeof analysisResult.data === 'string'">{{ analysisResult.data }}</pre>
      <div v-else-if="analysisResult.data && analysisResult.data.downloadUrl">
        <p>Analysis complete. <a :href="analysisResult.data.downloadUrl" target="_blank" download>Download Result File</a> ({{ analysisResult.data.filename || 'result' }})</p>
        <p v-if="analysisResult.data.preview" >Preview:</p>
        <pre v-if="analysisResult.data.preview">{{ analysisResult.data.preview }}</pre>
      </div>
      <pre v-else>{{ JSON.stringify(analysisResult.data, null, 2) }}</pre>
    </div>
    <div v-else-if="analysisResult.status === 'error'">
      <h4>Analysis Failed</h4>
      <pre class="error-message">{{ analysisResult.error }}</pre>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';

const props = defineProps({
  analysisResult: Object, // Expected shape: { status: string, data?: any, error?: any }
});
</script>

<style scoped>
.results-display {
  border: 1px solid #ddd;
  padding: 15px;
  margin-top: 20px;
  border-radius: 5px;
  background-color: #f9f9f9;
  min-height: 100px;
}
pre {
  background-color: #eee;
  padding: 10px;
  border-radius: 4px;
  white-space: pre-wrap; /* Allow text wrapping */
  word-break: break-all; /* Break long words */
  text-align: left;
}
.error-message {
  color: red;
  background-color: #ffe0e0;
}
a {
  color: #007bff;
}
h3, h4 {
  text-align: left;
}
p {
  text-align: left;
}
</style>
