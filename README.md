# 🧠 Skill Report Data Entry Program

This is a desktop GUI application built with `customtkinter` to help you manage course structures by levels and tasks, preview code and images, and generate professional PDF reports.

---

## 📁 Project Structure

```
your_project/
├── app.py              # <- Put this file here
└── [Day1], [Day2], ... # <- Your course folders go here (optional for auto-import)
```

- `app.py` is the main entry point. You run this file to start the app.
- You can optionally have folders like `Day1`, `Day2`, etc., each containing `.py` files that represent tasks.
- These folders can be auto-imported using the **Auto-Import Course Structure** feature.

---

## 🧹 Installation

### 1. Create a virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🛠️ Configuration (Constants & Settings)

The following constants are defined at the top of `app.py`. You can change them to fit your theme and style.

```python
FONT_FAMILY = "Segoe UI"
HEADING_FONT = (FONT_FAMILY, 16, "bold")
LABEL_FONT = (FONT_FAMILY, 12)
BUTTON_FONT = (FONT_FAMILY, 12, "bold")
ENTRY_FONT = (FONT_FAMILY, 12)

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")
```

### ✅ You can change:

- **Fonts**: Use another font like `"Arial"` or `"Roboto"` if desired.
- **Themes**: Use `customtkinter.set_default_color_theme("green")` for green or any other built-in theme.
- **Appearance Mode**: Switch to `"light"` if you prefer a white theme.

---

## 📦 Features

- Add unlimited Levels and Tasks.
- For each task:
  - Write a question
  - Choose a solution file
  - Automatically load and preview code
  - Attach an image or show a default one
- Auto-import folder structures like `Day1`, `Day2`...
- Generate a well-formatted PDF report
- Export includes code, images, and all task info.

---

## ⚠️ Important Notes

- All code and images are embedded into the PDF. Missing files will show placeholder messages.
- When importing folders, make sure the structure is consistent:
  - Folder names like `Day1 [Python Basics]` or just `Day1`
  - Inside, files like `1.1.py`, `1-1.py`, etc.
  - Also, inside Day Folders there should be a folder named `Screenshots` with files like `1.1.png`

---

## ▶️ Run the App

```bash
python app.py
```

---

## 💬 Need Help?

If anything goes wrong:

- Check the terminal for errors.
- Make sure your Python version is **3.8+**
- You can run this app on **Windows, macOS, or Linux**.

---

## 🧠 Made by Ammar & PlutoNix ❤️

I hope this application will be helpful to you and save you time to progress and achieve your goal. Best regards, Ammar & PlutoNix

---

## 🌟 شرح باللغة العربية:

هذا البرنامج هو تطبيق مكتبي مصمم بلغة Python باستخدام مكتبة `customtkinter`. الهدف منه هو إدارة هيكل الدورات التدريبية بسهولة من خلال تقسيمها إلى مستويات (Levels) ومهام (Tasks)، ومن ثم توليد تقرير PDF شامل يحتوي على الأسئلة، الأكواد، والصور.

### المزايا:

- يمكنك إنشاء عدد غير محدود من المستويات والمهام.
- لكل مهمة يمكنك:
  - إدخال نص السؤال.
  - تحديد ملف الحل (كود).
  - إرفاق صورة أو استخدام صورة افتراضية.
- خاصية الاستيراد التلقائي من مجلدات مثل `Day1`، `Day2`...
- توليد تقرير PDF منسق يحتوي على جميع التفاصيل.

### طريقة التشغيل:

1. ثبت المتطلبات:

```bash
pip install -r requirements.txt
```

2. شغّل التطبيق:

```bash
python app.py
```

### تخصيص الإعدادات:

- يمكنك تغيير نوع الخط، حجم الخط، الوضع الليلي أو الفاتح، ولون الواجهة من داخل الملف `app.py`.

### ملاحظات:

- التطبيق يدعم اللغة الإنجليزية في الواجهة.
- الأكواد والصور يتم إدراجها داخل التقرير تلقائيًا.
- يمكن تشغيل التطبيق على Windows، Linux، أو macOS.

بالتوفيق في استخدام البرنامج! ✨

