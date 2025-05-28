<template>
  <div class="analysis-selection">
    <h3>2. Select Analysis</h3>
    <select v-model="selectedAnalysisId" @change="handleAnalysisChange">
      <option disabled value="">Please select an analysis</option>
      <option v-for="analysis in analyses" :key="analysis.id" :value="analysis.id">
        {{ analysis.name }}
      </option>
    </select>
    <p v-if="selectedAnalysisId">Selected: {{ selectedAnalysisDisplayName }}</p>
  </div>
</template>

<script setup>
import { ref, computed, defineEmits } from 'vue';

const analyses = ref([
  { id: 'pore_diameter', name: 'Pore Diameter (-res)' },
  { id: 'surface_area', name: 'Surface Area (-sa)' },
  { id: 'accessible_volume', name: 'Accessible Volume (-vol)' },
  { id: 'probe_volume', name: 'Probe Volume (-volpo)' },
  { id: 'channel_analysis', name: 'Channel Analysis (-chan)' },
  { id: 'pore_size_dist', name: 'Pore Size Distribution (-psd)' },
  { id: 'ray_tracing', name: 'Ray Tracing (-ray_atom)' },
  { id: 'blocking_spheres', name: 'Blocking Spheres (-block)' },
  { id: 'distance_grid', name: 'Distance Grid (-gridG, -gridBOV, etc.)' },
  { id: 'structure_info', name: 'Structure Info (-strinfo)' },
  { id: 'voronoi_network', name: 'Voronoi Network (-nt2)' },
]);

const selectedAnalysisId = ref('');
const emit = defineEmits(['analysis-selected']);

const handleAnalysisChange = () => {
  if (selectedAnalysisId.value) {
    emit('analysis-selected', selectedAnalysisId.value);
  }
};

const selectedAnalysisDisplayName = computed(() => {
  const selected = analyses.value.find(a => a.id === selectedAnalysisId.value);
  return selected ? selected.name : '';
});
</script>

<style scoped>
.analysis-selection {
  border: 1px solid #ddd;
  padding: 15px;
  margin-bottom: 20px;
  border-radius: 5px;
  background-color: #f9f9f9;
}
select {
  width: 100%;
  padding: 8px;
  margin-top: 10px;
  border-radius: 4px;
  border: 1px solid #ccc;
}
p {
  margin-top: 10px;
  font-size: 0.9em;
  color: #333;
}
</style>
