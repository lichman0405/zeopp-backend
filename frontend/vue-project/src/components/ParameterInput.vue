<template>
  <div class="parameter-input">
    <h3>3. Set Parameters</h3>
    <form v-if="currentAnalysisId" @submit.prevent="onRunAnalysis">
      <div v-for="param in currentParams" :key="param.name" class="form-group">
        <label :for="param.name">{{ param.label }} ({{ param.name }})</label>
        <input
          v-if="param.type === 'text' || param.type === 'number' || param.type === 'float'"
          :type="param.type === 'float' ? 'number' : param.type"
          :id="param.name"
          v-model="formData[param.name]"
          :required="param.required"
          :step="param.type === 'float' ? 'any' : undefined"
          class="form-control"
        >
        <input
          v-else-if="param.type === 'checkbox'"
          type="checkbox"
          :id="param.name"
          v-model="formData[param.name]"
          class="form-check-input"
        >
        <select
          v-else-if="param.type === 'select'"
          :id="param.name"
          v-model="formData[param.name]"
          :required="param.required"
          class="form-control"
        >
          <option v-for="option_val in param.options" :key="option_val" :value="option_val">
            {{ option_val }}
          </option>
        </select>
        <small v-if="param.description" class="form-text text-muted">{{ param.description }}</small>
      </div>
      <button type="submit" :disabled="!isFormValid" class="btn btn-primary">Run Analysis</button>
    </form>
    <p v-else>Please select an analysis type first.</p>
  </div>
</template>

<script setup>
import { ref, watch, computed, defineProps, defineEmits } from 'vue';

const props = defineProps({
  analysisId: String,
  structureFile: Object,
});

const emit = defineEmits(['run-analysis']);

const formData = ref({});

const analysisParamsConfig = {
  pore_diameter: [
    { name: 'probe_radius', label: 'Probe Radius', type: 'float', required: true, defaultValue: 1.86, description: 'Radius of the probe in Angstroms (e.g., 1.86 for N2).' },
    { name: 'samples', label: 'Number of Samples', type: 'number', required: true, defaultValue: 1000, description: 'Number of samples for Monte Carlo integration.' },
    { name: 'ha', label: 'High Accuracy', type: 'checkbox', required: false, defaultValue: true, description: 'Enable high accuracy mode.' },
    { name: 'output_filename', label: 'Output Filename', type: 'text', required: false, defaultValue: 'results.res', description: 'Optional output filename.' },
  ],
  surface_area: [
    { name: 'probe_radius', label: 'Probe Radius', type: 'float', required: true, defaultValue: 1.86, description: 'Radius of the probe in Angstroms.' },
    { name: 'samples', label: 'Number of Samples', type: 'number', required: true, defaultValue: 1000, description: 'Number of samples per atom for Monte Carlo integration.' },
    { name: 'ha', label: 'High Accuracy', type: 'checkbox', required: false, defaultValue: true, description: 'Enable high accuracy mode.' },
    { name: 'output_filename', label: 'Output Filename', type: 'text', required: false, defaultValue: 'results.sa', description: 'Optional output filename.' },
  ],
  accessible_volume: [
    { name: 'probe_radius', label: 'Probe Radius', type: 'float', required: true, defaultValue: 1.86, description: 'Radius of the probe in Angstroms.' },
    { name: 'samples', label: 'Number of Samples', type: 'number', required: true, defaultValue: 1000, description: 'Number of samples per unit cell for Monte Carlo integration.' },
    { name: 'ha', label: 'High Accuracy', type: 'checkbox', required: false, defaultValue: true, description: 'Enable high accuracy mode.' },
    { name: 'output_filename', label: 'Output Filename', type: 'text', required: false, defaultValue: 'results.vol', description: 'Optional output filename.' },
  ],
  probe_volume: [ // -volpo, similar to accessible_volume but for a specific probe
    { name: 'probe_radius', label: 'Probe Radius', type: 'float', required: true, defaultValue: 1.2, description: 'Radius of the probe to estimate volume for (e.g. 1.2 for Helium).' },
    { name: 'samples', label: 'Number of Samples', type: 'number', required: true, defaultValue: 1000, description: 'Number of samples per unit cell for Monte Carlo integration.' },
    { name: 'ha', label: 'High Accuracy', type: 'checkbox', required: false, defaultValue: true, description: 'Enable high accuracy mode.' },
    { name: 'output_filename', label: 'Output Filename', type: 'text', required: false, defaultValue: 'results.volpo', description: 'Optional output filename.' },
  ],
  channel_analysis: [
    { name: 'chan_radius', label: 'Channel Radius', type: 'float', required: true, defaultValue: 1.2, description: 'Radius for channel identification.' },
    { name: 'probe_radius', label: 'Probe Radius', type: 'float', required: true, defaultValue: 1.86, description: 'Radius of the probe for sampling accessibility.' },
    { name: 'samples', label: 'Number of Samples', type: 'number', required: true, defaultValue: 1000, description: 'Number of samples for Monte Carlo integration.' },
    { name: 'ha', label: 'High Accuracy', type: 'checkbox', required: false, defaultValue: true, description: 'Enable high accuracy mode.' },
    { name: 'output_filename', label: 'Output Filename', type: 'text', required: false, defaultValue: 'results.chan', description: 'Optional output filename.' },
  ],
  pore_size_dist: [
    { name: 'probe_radius', label: 'Probe Radius', type: 'float', required: true, defaultValue: 1.86, description: 'Radius of the probe.' },
    { name: 'samples', label: 'Number of Samples', type: 'number', required: true, defaultValue: 2000, description: 'Number of samples for Monte Carlo integration.' },
    { name: 'ha', label: 'High Accuracy', type: 'checkbox', required: false, defaultValue: true, description: 'Enable high accuracy mode.' },
    { name: 'output_filename', label: 'Output Filename', type: 'text', required: false, defaultValue: 'results.psd', description: 'Optional output filename.' },
  ],
  ray_tracing: [ // -ray_atom or -ray_surface
    { name: 'probe_radius', label: 'Probe Radius', type: 'float', required: true, defaultValue: 0.1, description: 'Radius of rays for tracing (Angstroms). Smaller values for finer detail.' },
    { name: 'num_rays', label: 'Number of Rays', type: 'number', required: false, defaultValue: 100, description: 'Number of rays to trace from each atom/surface point.' },
    // Add other specific ray tracing params as needed, e.g., target_atom, surface_sample_density
    { name: 'ha', label: 'High Accuracy', type: 'checkbox', required: false, defaultValue: true, description: 'Enable high accuracy mode (may not be applicable, Zeo++ docs needed).' },
    { name: 'output_filename', label: 'Output Filename', type: 'text', required: false, defaultValue: 'results.ray', description: 'Optional output filename.' },
  ],
  blocking_spheres: [
    { name: 'probe_radius', label: 'Probe Radius', type: 'float', required: true, defaultValue: 1.86, description: 'Radius of the probe to determine accessible regions.' },
    { name: 'samples', label: 'Number of Samples', type: 'number', required: true, defaultValue: 1000, description: 'Number of samples for Monte Carlo integration.' },
    { name: 'output_filename', label: 'Output Filename', type: 'text', required: false, defaultValue: 'results.block', description: 'Optional output filename for blocking spheres coordinates.' },
  ],
  distance_grid: [ // -gridG, -gridGBohr, -gridBOV
    { name: 'mode', label: 'Grid Mode', type: 'select', options: ['gridG', 'gridGBohr', 'gridBOV'], required: true, defaultValue: 'gridG', description: 'Type of distance grid to calculate.' },
    { name: 'probe_radius', label: 'Probe Radius', type: 'float', required: false, defaultValue: 1.2, description: 'Radius of probe (used by some modes, e.g. gridBOV).' },
    { name: 'output_filename', label: 'Output Filename', type: 'text', required: false, defaultValue: 'results.grid', description: 'Optional output filename for the grid data.' },
  ],
  structure_info: [ // -strinfo, -strinfo_detail
    // No specific parameters required beyond the input file usually.
    // Add if specific options like -extradetail for -strinfo_detail are to be exposed
    { name: 'output_filename', label: 'Output Filename', type: 'text', required: false, defaultValue: 'structure.info', description: 'Optional output filename for structure information.' },
  ],
  voronoi_network: [ // -nt2
    { name: 'use_radii', label: 'Use Atomic Radii', type: 'checkbox', required: false, defaultValue: true, description: 'Use actual atomic radii instead of unit radii for Voronoi decomposition.' },
    { name: 'ha', label: 'High Accuracy', type: 'checkbox', required: false, defaultValue: true, description: 'Enable high accuracy mode.' }, // Assuming -ha might apply
    { name: 'output_filename', label: 'Output Filename', type: 'text', required: false, defaultValue: 'results.nt2', description: 'Optional output filename for Voronoi network data.' },
  ],
};

const currentParams = computed(() => {
  return props.analysisId ? analysisParamsConfig[props.analysisId] || [] : [];
});

watch(() => props.analysisId, (newAnalysisId) => {
  formData.value = {}; // Reset form data
  if (newAnalysisId && analysisParamsConfig[newAnalysisId]) {
    analysisParamsConfig[newAnalysisId].forEach(param => {
      // Set default values, especially for booleans
      if (param.type === 'checkbox') {
        formData.value[param.name] = param.defaultValue === undefined ? false : param.defaultValue;
      } else if (param.defaultValue !== undefined) {
        formData.value[param.name] = param.defaultValue;
      } else {
         formData.value[param.name] = null; // Or handle as per type, e.g. '' for text
      }
    });
  }
}, { immediate: true });


const isFormValid = computed(() => {
  if (!props.structureFile || !props.analysisId) {
    return false;
  }
  const paramsForAnalysis = analysisParamsConfig[props.analysisId] || [];
  return paramsForAnalysis.every(param => {
    if (!param.required) return true;
    const value = formData.value[param.name];
    // For checkboxes, being required means it must be true, but typically they are optional flags.
    // If a checkbox were truly required (must be checked), this logic would need adjustment.
    // For now, 'required' on a checkbox doesn't make sense unless it means "must be true".
    // Assuming 'required' for other types means "must have a value".
    return value !== null && value !== undefined && value !== '';
  });
});

const onRunAnalysis = () => {
  if (!isFormValid.value) return;

  const parameters = {};
  const paramsConfig = analysisParamsConfig[props.analysisId] || [];

  paramsConfig.forEach(param => {
    const value = formData.value[param.name];
    // Include if value is present, or if it's a boolean (always include boolean flags)
    // or if it's a number that could be 0
    if (value !== null && value !== undefined && value !== '' ) {
      if (param.type === 'number' || param.type === 'float') {
        parameters[param.name] = Number(value);
      } else {
        parameters[param.name] = value;
      }
    } else if (param.type === 'checkbox'){ // always include checkboxes
        parameters[param.name] = !!value; // ensure it's a boolean
    }
  });

  emit('run-analysis', {
    analysisId: props.analysisId,
    structureFile: props.structureFile,
    parameters,
  });
};

</script>

<style scoped>
.parameter-input {
  border: 1px solid #ddd;
  padding: 15px;
  margin-bottom: 20px;
  border-radius: 5px;
  background-color: #f9f9f9;
}
.form-group {
  margin-bottom: 15px;
}
.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}
.form-control {
  width: calc(100% - 22px); /* Adjust for padding/border */
  padding: 8px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}
.form-check-input {
  margin-left: 10px;
  vertical-align: middle;
}
.btn-primary {
  background-color: #007bff;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.btn-primary:hover {
  background-color: #0056b3;
}
.btn-primary:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
.form-text {
  font-size: 0.85em;
  color: #666;
}
</style>
