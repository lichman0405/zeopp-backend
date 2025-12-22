# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-12-22

### Added
- **API Versioning**: All analysis endpoints now use `/api/v1/` prefix for better version control
- **Health Check Endpoints**: 
  - `/health` - Basic health check
  - `/health/detailed` - Detailed health check with system information and Zeo++ availability
- **Version Endpoint**: `/version` - Get API version information
- **Enhanced Error Handling**:
  - Custom exception classes (`ZeoppBaseException`, `ZeoppExecutionError`, `ZeoppParsingError`, etc.)
  - More specific error messages with detailed context
  - Better error logging and debugging information
- **Improved .gitignore**: More comprehensive file exclusions

### Changed
- **Error Messages**: Now provide more detailed information about failures
- **Parser Functions**: Enhanced error handling with specific exception types instead of generic `Exception`
- **Handler Function**: Improved error differentiation between execution, parsing, and output errors
- **Documentation**: Updated both README.md and README-en.md with new endpoints and version information

### Fixed
- Parser error handling now catches specific exception types (ValueError, IndexError) instead of broad Exception
- Better logging for parsing failures

## [0.2.0] - 2025-06-16

### Added
- Refactored API endpoints to use generic handler function
- Improved code reusability with `process_zeo_request`

### Changed
- Consolidated boilerplate code across all API endpoints

## [0.1.0] - 2025-05-13

### Added
- Initial release
- Docker support with automatic Zeo++ compilation
- FastAPI-based REST API
- Smart caching system
- Support for 9 Zeo++ analysis types:
  - Pore diameter
  - Surface area
  - Accessible volume
  - Probe volume
  - Channel analysis
  - Pore size distribution
  - Blocking spheres
  - Framework info
  - Open metal sites
- Rich logging with beautiful console output
- Configuration via .env file
