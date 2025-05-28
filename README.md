# Zeo++ API Service

A production-ready FastAPI service that wraps [Zeo++](http://www.zeoplusplus.org/) structural analysis functionality as containerized HTTP endpoints.

## 🚀 Features

- ✅ Fully wraps all Zeo++ analysis options via HTTP API
- 🧠 Automatic caching via file content hash
- 📂 Structured output (JSON or raw `.res`, `.sa`, `.vol`, etc.)
- ⚙️ Configurable via `.env`
- 🐳 Docker-ready (auto-downloads + compiles Zeo++)
- 🎨 Rich logs and well-typed request/response models

---

## 📁 Project Structure

```text
app/
├── api/            # All FastAPI route modules (one per Zeo++ feature)
├── models/         # Pydantic request/response models
├── core/           # Runner + config
├── utils/          # File save, logging, Zeo++ output parser
├── main.py         # Entrypoint to register all routers
workspace/          # tmp/ and cache/ for intermediate files
```

---

## ⚙️ .env Example

```ini
ZEO_EXEC_PATH=network
ZEO_WORKSPACE=workspace
ENABLE_CACHE=true
LOG_LEVEL=INFO
```

---

## 🐳 Docker Build & Run

```bash
docker build -t zeopp-api .
docker run -it --rm -p 8000:8000 zeopp-api
```

---

## 📚 API Reference

### `/api/pore_diameter` → Zeo++ `-res`
| Field             | Type    | Required | Default       | Description                              |
|------------------|---------|----------|---------------|------------------------------------------|
| `structure_file` | file    | ✅        | —             | Structure file (`.cif`, `.cssr`, etc.)   |
| `ha`             | bool    | ❌        | `true`        | Use high-accuracy mode                   |
| `output_filename`| str     | ❌        | `result.res`  | Custom output filename                   |

---

### `/api/surface_area` → Zeo++ `-sa`
| Field             | Type    | Required | Default       | Description                              |
|------------------|---------|----------|---------------|------------------------------------------|
| `structure_file` | file    | ✅        | —             | Input structure                          |
| `chan_radius`    | float   | ✅        | —             | Probe radius for accessibility check     |
| `probe_radius`   | float   | ✅        | —             | Monte Carlo sampling radius              |
| `samples`        | int     | ✅        | —             | Samples per atom                         |
| `output_filename`| str     | ❌        | `result.sa`   | Output filename                          |
| `ha`             | bool    | ❌        | `true`        | High accuracy mode                       |

---

### `/api/accessible_volume` → Zeo++ `-vol`
| Field             | Type    | Required | Default       | Description                              |
|------------------|---------|----------|---------------|------------------------------------------|
| `structure_file` | file    | ✅        | —             | Structure input file                     |
| `chan_radius`    | float   | ✅        | —             | Probe for accessibility                  |
| `probe_radius`   | float   | ✅        | —             | Probe for volume measurement             |
| `samples`        | int     | ✅        | —             | Samples per unit cell                    |
| `output_filename`| str     | ❌        | `result.vol`  | Custom output filename                   |
| `ha`             | bool    | ❌        | `true`        | Use high accuracy                        |

---

### `/api/probe_volume` → Zeo++ `-volpo`
Same parameters as `/api/accessible_volume`.

---

### `/api/channel_analysis` → Zeo++ `-chan`
| Field             | Type    | Required | Default       | Description                              |
|------------------|---------|----------|---------------|------------------------------------------|
| `structure_file` | file    | ✅        | —             | Input structure file                     |
| `probe_radius`   | float   | ✅        | —             | Spherical probe radius                   |
| `output_filename`| str     | ❌        | `result.chan` | Output file                              |
| `ha`             | bool    | ❌        | `true`        | High accuracy                            |

---

### `/api/pore_size_dist` → Zeo++ `-psd`
| Field             | Type    | Required | Default       | Description                              |
|------------------|---------|----------|---------------|------------------------------------------|
| `structure_file` | file    | ✅        | —             | Structure file                           |
| `chan_radius`    | float   | ✅        | —             | Channel probe radius                     |
| `probe_radius`   | float   | ✅        | —             | Probe radius for sampling                |
| `samples`        | int     | ✅        | —             | Monte Carlo samples                      |
| `output_filename`| str     | ❌        | `result.psd_histo` | Output file name                   |
| `ha`             | bool    | ❌        | `true`        | High accuracy                            |

---

### `/api/ray_tracing` → Zeo++ `-ray_atom`
Same as `/api/pore_size_dist` but for ray tracing.

---

### `/api/blocking_spheres` → Zeo++ `-block`
| Field             | Type    | Required | Default       | Description                              |
|------------------|---------|----------|---------------|------------------------------------------|
| `structure_file` | file    | ✅        | —             | Input file                               |
| `probe_radius`   | float   | ✅        | —             | Blocking probe radius                    |
| `samples`        | int     | ✅        | —             | Monte Carlo samples                      |
| `output_filename`| str     | ❌        | `result.block`| Blocking sphere output                   |
| `ha`             | bool    | ❌        | `true`        | Use high accuracy                        |

---

### `/api/distance_grid` → Zeo++ `-gridG`, `-gridBOV`, etc.
| Field             | Type    | Required | Default      | Description                              |
|------------------|---------|----------|--------------|------------------------------------------|
| `structure_file` | file    | ✅        | —            | Input structure                          |
| `mode`           | str     | ✅        | —            | `gridG`, `gridGBohr`, `gridBOV`          |
| `output_basename`| str     | ❌        | `result`     | Base name of output files                |
| `ha`             | bool    | ❌        | `true`       | High accuracy mode                       |

---

### `/api/structure_info` → Zeo++ `-strinfo`
| Field             | Type    | Required | Default          | Description                              |
|------------------|---------|----------|------------------|------------------------------------------|
| `structure_file` | file    | ✅        | —                | MOF structure                            |
| `output_filename`| str     | ❌        | `result.strinfo` | Output filename                          |

---

### `/api/voronoi_network` → Zeo++ `-nt2`
| Field             | Type    | Required | Default        | Description                              |
|------------------|---------|----------|----------------|------------------------------------------|
| `structure_file` | file    | ✅        | —              | MOF structure                            |
| `use_radii`      | bool    | ❌        | `true`         | Use atomic radii or not (-r vs -nor)     |
| `output_filename`| str     | ❌        | `result.nt2`   | Output file name                         |

---

## 🔒 Notes

- Supported file formats: `.cssr`, `.cif`, `.pdb`
- All endpoints support `ha=true` for high-accuracy mode.
- Set `output_filename` to customize output file names.
- All results are cached based on file hash + parameters.

---

## 📜 License

MIT © Shibo Li, 2025
