# Changelog

All notable changes to **xeno-channel-service** are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Multi-channel delivery orchestration (email, SMS, push)
- Kafka producer/consumer with dead letter queue
- Delivery receipt callback handler
- Channel health monitoring endpoint

### Fixed
- Fixed message ordering guarantee for high-throughput channels

### Changed
- Switched to idempotent Kafka producer configuration

---

## [1.0.0] - 2025-01-01

### Added
- Initial public release of xeno-channel-service.
- Core feature implementation.
- README and project documentation.
- GitHub Actions CI pipeline.

[Unreleased]: https://github.com/LAKSHYA-NIGAM/xeno-channel-service/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/LAKSHYA-NIGAM/xeno-channel-service/releases/tag/v1.0.0
