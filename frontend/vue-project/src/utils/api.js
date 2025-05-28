export async function callZeoPlusPlusApi(analysisId, structureFile, parameters) {
  const formData = new FormData();
  formData.append('structure_file', structureFile, structureFile.name);

  for (const key in parameters) {
    if (parameters[key] !== null && parameters[key] !== undefined) {
      // FastAPI handles boolean 'true'/'false' strings well in FormData.
      // So, explicitly convert booleans to strings. Numbers can be sent as is.
      if (typeof parameters[key] === 'boolean') {
        formData.append(key, parameters[key].toString());
      } else {
        formData.append(key, parameters[key]);
      }
    }
  }

  // Log FormData contents for debugging (optional)
  // for (var pair of formData.entries()) {
  //   console.log(pair[0]+ ', ' + pair[1]);
  // }

  const response = await fetch(`/api/${analysisId}`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch (e) {
      errorData = { detail: `HTTP error! status: ${response.status}, statusText: ${response.statusText}` };
    }
    throw new Error(errorData.detail || `API request failed with status ${response.status}`);
  }

  // Determine if the response is a file to download or JSON data
  const contentType = response.headers.get('content-type');
  const contentDisposition = response.headers.get('content-disposition');
  let filename = parameters.output_filename || 'result.txt'; // Default filename

  if (contentDisposition) {
     const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
     if (filenameMatch && filenameMatch[1]) {
         filename = filenameMatch[1];
     }
  }


  // Heuristic: If it's not explicitly JSON and has a common Zeo++ output extension, treat as file.
  // Or, if backend always returns JSON for success with a link, or always file for direct output.
  // Assuming direct file response for now if not application/json.
  if (contentType && (contentType.includes('application/octet-stream') || contentType.includes('text/plain') || !contentType.includes('application/json'))) {
    const blob = await response.blob();
    const downloadUrl = URL.createObjectURL(blob);
    let preview = `Binary data or file too large for preview. Click to download. (${filename})`;

    // Attempt to read preview for text-based files
    if (contentType.includes('text/plain') || filename.endsWith('.res') || filename.endsWith('.strinfo') || filename.endsWith('.chan') || filename.endsWith('.psd_histo') || filename.endsWith('.nt2') || filename.endsWith('.block')) {
      try {
         const textContent = await blob.text();
         preview = textContent.substring(0, 500) + (textContent.length > 500 ? '...' : ''); // First 500 chars
      } catch (e) {
         console.error("Error reading blob as text:", e);
         preview = "Could not generate preview for this text-based file.";
      }
    }
    return { downloadUrl, filename, preview };
  } else {
    // Assuming JSON response if not treated as a file
    return await response.json();
  }
}
