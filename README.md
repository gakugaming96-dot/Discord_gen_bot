# 🎫 GG discord Gen Bot

A professional, prefix-based Discord generator bot built with Python and Pycord. This bot replaces standard account generation with a **Ticket System**, featuring role-based access levels, presence-based auto-roles, and a secure configuration optimized for cloud hosting like Railway.

---

## 🚀 Features

- **Advanced Prefix System:** Supports custom command routing (`F.`, `B.`, `V.`, and `D.`).
- **Ticket Generation:** Generates unique 9-character alphanumeric codes instead of sending raw account data.
- **Access Levels:**
  - **Free:** Requires a custom status/presence to unlock.
  - **Booster:** Restricted to server boosters.
  - **VIP:** Premium access for paid members.
- **Auto-Role System:** Automatically assigns roles to users who support the server via their Discord status.
- **Railway Ready:** Built-in support for environment variables to keep your bot token and IDs secure.
- **Auto-Maintenance:** Clears command channels and updates instruction embeds on startup.
- **Hidden Admin Tools:** Secure restart and whitelist management.

---

## 🛠️ Commands

| Command       | Usage                  | Description                                      |
|---------------|------------------------|--------------------------------------------------|
| `F.gen`       | `F.gen [service]`      | Generates a Free tier ticket (Requires Status).  |
| `B.`          | `B.[service]`          | Generates a Booster tier ticket.                 |
| `V.`          | `V.[service]`          | Generates a VIP tier ticket.                     |
| `D.restart`   | `D.restart`            | Hidden command to restart the bot process (Owner only). |
| `F.whitelist` | `F.whitelist @user`    | Adds a user to the bot's admin whitelist.        |
| `F.unwhitelist`| `F.unwhitelist @user` | Removes a user from the whitelist.               |
| `F.get_log_file`| `F.get_log_file`     | DMs the administrator the current log file.      |

---

## 📦 Installation & Setup

### 1. Local Hosting
1. Install dependencies:
   ```bash
   pip install pycord colorama
