# Telegram Notification Hub

این ریپو هاب مرکزی اعلان‌های GitHub به Telegram است.

هسته ارسال تلگرام و Secretهای اصلی فقط در همین ریپو نگهداری می‌شوند.

## معماری

```text
Repo A ─┐
Repo B ─┤
Repo C ─┤
        ↓
repository_dispatch: notify
        ↓
zhstt13/Telegram
        ↓
Telegram Notification Hub
        ↓
Telegram Bot API
        ↓
Telegram
```

## Secrets

در همین ریپو به مسیر `Settings → Secrets and variables → Actions` برو.

این دو Repository Secret باید وجود داشته باشند:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Secretهای تلگرام نباید داخل فایل‌های ریپو Commit شوند.

## ورودی‌های Hub

Workflow سه روش اجرا دارد:

### 1. repository_dispatch

برای اتصال اتوماتیک سایر ریپوها، event با نوع `notify` ارسال می‌شود.

Payload پیشنهادی:

```json
{
  "event_type": "notify",
  "client_payload": {
    "project": "LoPRax",
    "repository": "zhstt13/LoPRax",
    "event": "Build passed",
    "status": "success",
    "message": "Frontend build completed successfully.",
    "branch": "main",
    "commit": "abcdef123456",
    "actor": "github-actions",
    "url": "https://github.com/..."
  }
}
```

فیلدهای قابل استفاده:

- `project`
- `repository`
- `event`
- `status`: `success`, `failure`, `warning`, `info`
- `message`
- `branch`
- `commit`
- `actor`
- `url`

فقط `message` عملاً ضروری است؛ بقیه برای ساخت پیام کامل‌تر هستند.

### 2. workflow_dispatch

از تب **Actions** می‌توان Workflow را دستی اجرا و Project / Event / Status / Message / URL را وارد کرد.

### 3. message.txt

برای تست سریع از ChatGPT یا GitHub، تغییر `message.txt` هنوز Workflow را اجرا می‌کند.

## نکته مهم درباره اتصال ریپوهای دیگر

Secretهای **Telegram** فقط در همین Hub می‌مانند.

اما GitHub برای اینکه Workflow یک Repo دیگر بتواند به API ریپوی `Telegram` درخواست `repository_dispatch` بفرستد، به احراز هویت GitHub نیاز دارد. `GITHUB_TOKEN` هر Repo معمولاً به همان Repo محدود است و نباید آن را با Telegram Bot Token اشتباه گرفت.

برای اتصال تعداد زیادی Repo بدون کپی‌کردن Secret تلگرام، مسیرهای مناسب این‌ها هستند:

1. **GitHub App** نصب‌شده روی Repoهای موردنظر — مناسب برای معماری شخصی چندریپویی.
2. **Organization Secret** اگر Repoها داخل یک GitHub Organization قرار بگیرند.
3. یک credential مرکزی محدودشده برای dispatch، اگر عمداً این مدل را انتخاب کنیم.

هدف این معماری این است که منطق و Secretهای Telegram تکرار نشوند؛ Callerها فقط event استاندارد به Hub بفرستند.

## قالب پیام

Hub خودش اطلاعات Event را تبدیل به پیام خوانا می‌کند، مثلاً:

```text
✅ LoPRax
Event: Build passed
Repo: zhstt13/LoPRax
Branch: main
Commit: abcdef1
Actor: github-actions

Frontend build completed successfully.
```

پیام‌ها برای محدودیت Telegram به حداکثر حدود 4000 کاراکتر کوتاه می‌شوند.
