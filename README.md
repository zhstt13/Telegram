# ChatGPT → GitHub → Telegram Bridge

این ریپو یک پل ساده برای فرستادن پیام از ChatGPT به تلگرام است، بدون استفاده از OpenAI API.

## جریان کار

1. ChatGPT متن `message.txt` را تغییر می‌دهد و روی GitHub Commit می‌کند.
2. GitHub Actions با تغییر `message.txt` اجرا می‌شود.
3. Workflow متن فایل را با Telegram Bot API برای Chat ID تعیین‌شده می‌فرستد.

## Secrets لازم

در GitHub به مسیر زیر برو:

`Settings → Secrets and variables → Actions → New repository secret`

دو Secret بساز:

- `TELEGRAM_BOT_TOKEN` — توکن BotFather
- `TELEGRAM_CHAT_ID` — شناسه چتی که پیام باید به آن ارسال شود

> توکن ربات را داخل فایل‌های ریپو Commit نکن.

## ارسال پیام

کافی است محتوای `message.txt` تغییر کند. هر Push مربوط به این فایل، Workflow را اجرا می‌کند و پیام را به تلگرام می‌فرستد.

Workflow را همچنین می‌توان به‌صورت دستی از بخش Actions اجرا کرد تا همان پیام فعلی دوباره ارسال شود.
