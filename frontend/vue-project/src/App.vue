<template>
  <div id="app">
    <h1>Zeo++ Web Interface</h1>
    <FileUpload @file-selected="handleFileSelected" />
    <AnalysisSelection @analysis-selected="handleAnalysisSelected" />
    <ParameterInput
      :analysis-id="currentAnalysisId"
      :structure-file="currentFile"
      @run-analysis="handleRunAnalysis"
    />
    <ResultsDisplay :analysis-result="analysisResult" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import FileUpload from './components/FileUpload.vue';
import AnalysisSelection from './components/AnalysisSelection.vue';
import ParameterInput from './components/ParameterInput.vue';
import ResultsDisplay from './components/ResultsDisplay.vue';
import { callZeoPlusPlusApi } from './utils/api.js'; // Import the API function

const currentFile = ref(null);
const currentAnalysisId = ref('');
const analysisResult = ref({ status: 'idle', data: null, error: null });

const handleFileSelected = (file) => {
  currentFile.value = file;
  console.log('File selected in App.vue:', file?.name);
  analysisResult.value = { status: 'idle', data: null, error: null }; // Reset
};

const handleAnalysisSelected = (analysisId) => {
  currentAnalysisId.value = analysisId;
  console.log('Analysis selected in App.vue:', analysisId);
  analysisResult.value = { status: 'idle', data: null, error: null }; // Reset
};

const handleRunAnalysis = async (analysisData) => { // Make it async
  console.log('Run Analysis Event Data:', analysisData);
  analysisResult.value = { status: 'loading', data: null, error: null };

  try {
    const responseData = await callZeoPlusPlusApi(
      analysisData.analysisId,
      analysisData.structureFile,
      analysisData.parameters
    );
    analysisResult.value = { status: 'success', data: responseData };
  } catch (error) {
    console.error('API Call Failed:', error);
    analysisResult.value = { status: 'error', error: error.message || 'An unknown error occurred during the API call.' };
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
h1 {
  margin-bottom: 40px;
}
</style>
