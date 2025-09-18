# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-09-18

### Added
- Timezone support for reminders (Europe/Moscow by default)
- Repeat options for reminders:
  - No repeat
  - Daily
  - Weekly
  - Monthly
  - Weekdays only
- Grace period for missed reminders (up to 24 hours)
- Startup catch-up for missed reminders
- Concurrent access protection using file locking (portalocker)
- Backward compatibility for old reminder format
- Enhanced date parsing with natural language support
- Improved validation for reminder data

### Changed
- Reminder storage format from DD.MM.YYYY/HH:MM to ISO 8601 with timezone
- Reminder checking logic to use time windows instead of exact matches
- Repeat logic to automatically calculate next occurrence
- File writing to use atomic operations with file locking

### Fixed
- Issue with missed reminders never being sent
- Race conditions when multiple processes accessed user data
- Timezone inconsistencies when server was in different timezone
- Data corruption issues with concurrent writes to user data file

## [1.0.0] - 2025-09-10

### Added
- Initial release with basic functionality
- Cryptocurrency management (Bybit API integration)
- Piggy banks for saving money
- Shopping lists with categories
- Basic reminders with date/time scheduling