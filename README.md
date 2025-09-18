# Financial Telegram Bot with Reminders

A comprehensive Telegram bot for managing finances, cryptocurrency assets, piggy banks, shopping lists, and now reminders.

## Features

- 💰 Cryptocurrency management (Bybit API integration)
- 🍘 Piggy banks for saving money
- 🛒 Shopping lists with categories
- ⏰ Reminders with date/time scheduling and repeat options
- ⚙️ Settings and help menus

## Reminders Functionality

The new reminders feature allows users to:

1. Create reminders with custom titles and content
2. Set dates using quick buttons:
   - Through an hour
   - Tomorrow
   - Saturday (nearest)
   - 15th of the month (nearest)
   - 31st of the month (nearest)
   - Custom date/time
3. Enter custom dates in natural language format (e.g., "tomorrow at noon", "next Monday")
4. Set time in HH:MM format
5. View, edit, reschedule, and delete reminders
6. Set repeat options:
   - No repeat
   - Daily
   - Weekly
   - Monthly
   - Weekdays only
7. Receive notifications at the specified date and time
8. Reschedule or delete reminders directly from notification messages

## Enhanced Reminders Features

- **Timezone Support**: All reminders are stored with timezone information (Europe/Moscow by default)
- **Grace Period**: Reminders that were missed within 24 hours will still be sent
- **Repeat Logic**: Repeating reminders automatically calculate the next occurrence after being sent
- **Startup Catch-up**: Missed reminders are sent when the bot starts up
- **Concurrent Access Protection**: File locking prevents data corruption when multiple processes access user data
- **Backward Compatibility**: Old reminder format is automatically converted to the new format

## Installation

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your Telegram bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   ```

3. Run the bot:
   ```
   python bot.py
   ```

## Setup Instructions

For detailed setup instructions, please see [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md).

## Usage

Start the bot by sending `/start` to your bot in Telegram.

Navigate through the menus to access different features:
- 💰 Crypto: Manage cryptocurrency assets (requires Bybit API keys)
- 🍘 Piggy Bank: Create and manage savings goals
- 🛒 Shopping List: Maintain categorized shopping lists
- ⏰ Reminders: Create and manage timed notifications
- ⚙️ Settings: Configure API keys and other settings
- ℹ️ Help: Get information about bot features

## Reminders Menu

In the reminders section, you can:
- Create new reminders with the "➕ Создать напоминание" button
- View existing reminders by clicking on them
- Edit reminder content
- Reschedule reminders to new dates/times
- Set repeat options for recurring reminders
- Delete reminders you no longer need

When a reminder's date and time match the current time, the bot will send a notification message to the user with options to reschedule or delete the reminder.

## Launcher Script

For Windows users, a launcher script [launcher.bat](launcher.bat) is provided with the following features:
- Start/Stop/Restart the bot
- Update from GitHub
- Check logs
- Install/Update dependencies
- Configuration checking
- Troubleshooting assistance

## Testing

A test script [test_bot_startup.py](test_bot_startup.py) is available to verify bot configuration and dependencies.